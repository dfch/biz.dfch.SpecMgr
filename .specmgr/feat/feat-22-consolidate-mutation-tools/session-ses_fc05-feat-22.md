# Consolidate update commands into one

**Session ID:** ses_fc05744c7ffeQYQ4MuOkcx2IN2
**Created:** 8/26/2026, 10:00:17 PM
**Updated:** 8/26/2026, 11:56:45 PM

---

## User

I want to create a feature: Consolidate all update commands into a single update command. The idea behind this: all update commands take a whole body. The uuid is unique. So, we either create an update command, that needs a `type` (example: rsk) and a `uuid`. Or just the `uuid` because the uuis is unique.
With this we can remove a lot of tools and make the tool arsenal simpler.
What do you think of this?

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 70.0s)

_Thinking:_

The user is asking for my opinion on a feature proposal to consolidate all update commands into a single update command in the specmgr codebase. This is plan mode, read-only.

Let me think about what's being proposed:

- Currently there are per-domain update commands: `update_req`, `update_uc`, `update_tsk`, `update_qa`, `update_prb`, `update_gol`, `update_rsk`, `update_section` (ADR-specific), `update_frontmatter` (ADR-specific).
- These all do whole-body replacement, take an id (UUID) and content.
- Since the UUID is unique, a single `update` command taking just a uuid (or uuid + type) could work.

I should first explore the codebase to understand the current structure, then form an opinion and a plan.

Key considerations to research:

1. Current update tool implementations in each domain (are they really identical in behavior? ADR has update_section + update_frontmatter + set_status, others have update\_<domain>).
2. Id resolution: how are ids mapped to file paths? Is there a central registry, or per-domain directories? Per-domain base directories are probably via env vars (SPECMGR_ADR_DIR etc.). If ids are globally unique UUIDs, a single update can look up the domain from the id... but how? Each domain has its own directory; resolving an id requires knowing which directory to look in. Unless there's an index. The `specmgr_list_*` tools say "ref" is for docs without an assigned id. The id -> file path resolution (plan §9a) is mentioned in the ADR frontmatter docstring.

So for a single `update` taking only a uuid: the server would need to scan all domain directories to find which one contains the id. Feasible but a bit costly (though the number of directories is small). Or take a `type` parameter.

Tradeoffs:

- Single tool with `type`: simple, explicit, no scanning needed. Type enum: adr, req, uc, tsk, qa, prb, gol, rsk (and future ac).
- Single tool with uuid only: fewer parameters but needs id -> domain resolution. If ids are UUIDs generated independently per domain, theoretically a collision could occur (astronomically unlikely for v4 UUIDs, but still). ADR explicitly notes that the specmgr-assigned id is a "server-generated UUID string" used for "id -> file path" resolution. There may be an existing index file.

Also to consider: ADR has different update semantics — `update_section` (per-section replacement/deletion) and `update_frontmatter` (whole-object frontmatter replacement), plus `update_adr`? Wait, does ADR have a whole-body update? From the AGENTS.md bullet: adr/tools has 12 wrappers: get_adr, list_adr, create_adr, update_frontmatter, update_section, set_status, option\_\* (5), validate_adr. So ADR does NOT have a whole-body update — that's the divergence. ADR updates go section-by-section (preserving structure), while the other 7 domains do whole-body replacement.

So consolidating "all update commands" into one is tricky:

- The 7 non-ADR domains: identical shape (id, content) -> whole-body replacement, preserving id/type/status/created/version, bumping `updated`.
- ADR: no whole-body replacement exists. update_frontmatter + update_section + option\_\* are ADR-specific and cannot be consolidated into "content" replacement without losing ADR's section-level contract. So the consolidated update would either (a) only cover the 7 domains, or (b) also add a whole-body update_adr which contradicts ADR's design (plan §4/§5 section-level updates).

Also, the `set_status` family (set_status_req etc., 7 + generic set_status for ADR) has a similar consolidation opportunity, but that's a separate matter — worth mentioning.

Also, the MCP tool surface: each tool is a separate entry in the docs (docs/MCP.md is auto-generated), in server.py's docstring, and in tests. Removing 7 tools and adding 1 reduces the arsenal.

Another consideration: the MCP client (LLM) needs to know which tool to call. A single `update` with a `type` enum is actually easier for the LLM to use than 7 near-identical tools. This is a real usability win.

But there's a counter-consideration: the per-domain `update_<domain>` names are self-documenting in tool listing; the generic `update` with a type parameter requires the LLM to pass the right type. Since the user proposes `type` (e.g., rsk) + uuid, or uuid only, we should recommend one.

My opinion: I support the consolidation of the 7 whole-body updates into a single `update` tool with explicit `id` + `type` parameters (type makes domain resolution deterministic, avoids scanning all directories, avoids the theoretical UUID collision issue, and makes the tool contract explicit). The `uuid-only` variant requires building an id -> domain index or scanning; not worth it. ADR is out of scope (it has section-level updates by design — update_frontmatter/update_section/option\_\* remain).

Next, to ground the plan, let me explore the codebase:

- Look at src/biz/dfch/specmgr/ structure
- Look at one update implementation (e.g., req/tools)
- See how id resolution works (there's probably a shared helper for "resolve id to path")
- Check the docstring in server.py
- Check the tests for update tools
- Check for shared modules (e.g., a general helper for update)

Let me do exploration with parallel tool calls. I could also delegate to the explore agent to save context, but direct reads of a few files should be fine and faster. First let me look at the directory structure.

Plan:

1. List the src tree.
2. Read req/tools (the update tool), rsk/tools (the update tool), adr/tools (update_section/update_frontmatter), and the shared id resolution helper.
3. Read the relevant parts of server.py's docstring.
4. Check the tests for update tools.

Then, ask the user clarifying questions about the key tradeoffs:

- ADR: out of scope, or also add a whole-body update_adr?
- type parameter or uuid-only?
- Naming: a single `update` tool?
- Should we also consolidate set_status (adjacent)?
- Backward compatibility: keep the old tools as deprecated wrappers, or remove them outright?
- The feature folder naming: feat-NNN-slug — which issue number? Probably feat-0 for now.

Let me explore first.

**Tool: bash**

**Input:**

```json
{
  "command": "find src/biz/dfch/specmgr -type f -name \"*.py\" | sort"
}
```

**Output:**

```
src/biz/dfch/specmgr/adr/__init__.py
src/biz/dfch/specmgr/adr/prompts/create_adr.py
src/biz/dfch/specmgr/adr/prompts/create_adr_test.py
src/biz/dfch/specmgr/adr/prompts/__init__.py
src/biz/dfch/specmgr/adr/prompts/update_adr.py
src/biz/dfch/specmgr/adr/prompts/update_adr_test.py
src/biz/dfch/specmgr/adr/resources/adr_get.py
src/biz/dfch/specmgr/adr/resources/__init__.py
src/biz/dfch/specmgr/adr/tools/create_adr.py
src/biz/dfch/specmgr/adr/tools/get_adr.py
src/biz/dfch/specmgr/adr/tools/__init__.py
src/biz/dfch/specmgr/adr/tools/_io.py
src/biz/dfch/specmgr/adr/tools/list_adr.py
src/biz/dfch/specmgr/adr/tools/_lock.py
src/biz/dfch/specmgr/adr/tools/option_create.py
src/biz/dfch/specmgr/adr/tools/option_delete.py
src/biz/dfch/specmgr/adr/tools/option_list.py
src/biz/dfch/specmgr/adr/tools/option_read.py
src/biz/dfch/specmgr/adr/tools/option_update.py
src/biz/dfch/specmgr/adr/tools/_paths.py
src/biz/dfch/specmgr/adr/tools/set_status.py
src/biz/dfch/specmgr/adr/tools/update_frontmatter.py
src/biz/dfch/specmgr/adr/tools/update_section.py
src/biz/dfch/specmgr/adr/tools/validate_adr.py
src/biz/dfch/specmgr/cli.py
src/biz/dfch/specmgr/commands/adr_toc.py
src/biz/dfch/specmgr/commands/coverage_badge.py
src/biz/dfch/specmgr/commands/docs.py
src/biz/dfch/specmgr/commands/__init__.py
src/biz/dfch/specmgr/commands/mcp_docs.py
src/biz/dfch/specmgr/commands/mcp.py
src/biz/dfch/specmgr/commands/mdformat.py
src/biz/dfch/specmgr/commands/req_parse.py
src/biz/dfch/specmgr/commands/schema.py
src/biz/dfch/specmgr/commands/unused_code.py
src/biz/dfch/specmgr/commands/version.py
src/biz/dfch/specmgr/general/__init__.py
src/biz/dfch/specmgr/general/models/__init__.py
src/biz/dfch/specmgr/general/models/paged_result.py
src/biz/dfch/specmgr/general/models/summary.py
src/biz/dfch/specmgr/general/prompts/compact_history.py
src/biz/dfch/specmgr/general/prompts/__init__.py
src/biz/dfch/specmgr/general/resources/__init__.py
src/biz/dfch/specmgr/general/resources/iso25010.py
src/biz/dfch/specmgr/general/resources/version.py
src/biz/dfch/specmgr/general/tools/_doc_paths.py
src/biz/dfch/specmgr/general/tools/__init__.py
src/biz/dfch/specmgr/general/tools/mdformat.py
src/biz/dfch/specmgr/general/tools/_packaged_data.py
src/biz/dfch/specmgr/general/tools/_paging.py
src/biz/dfch/specmgr/general/tools/webfetch.py
src/biz/dfch/specmgr/gol/__init__.py
src/biz/dfch/specmgr/gol/models/v1/body.py
src/biz/dfch/specmgr/gol/models/v1/document.py
src/biz/dfch/specmgr/gol/models/v1/frontmatter.py
src/biz/dfch/specmgr/gol/models/v1/__init__.py
src/biz/dfch/specmgr/gol/models/v1/parser.py
src/biz/dfch/specmgr/gol/models/v1/summary.py
src/biz/dfch/specmgr/gol/models/v1/_util.py
src/biz/dfch/specmgr/gol/prompts/create_gol.py
src/biz/dfch/specmgr/gol/prompts/__init__.py
src/biz/dfch/specmgr/gol/prompts/update_gol.py
src/biz/dfch/specmgr/gol/resources/gol_example.py
src/biz/dfch/specmgr/gol/resources/gol_schema.py
src/biz/dfch/specmgr/gol/resources/gol_template.py
src/biz/dfch/specmgr/gol/resources/__init__.py
src/biz/dfch/specmgr/gol/tools/create_gol.py
src/biz/dfch/specmgr/gol/tools/delete_gol.py
src/biz/dfch/specmgr/gol/tools/get_gol_example.py
src/biz/dfch/specmgr/gol/tools/get_gol.py
src/biz/dfch/specmgr/gol/tools/get_gol_template.py
src/biz/dfch/specmgr/gol/tools/__init__.py
src/biz/dfch/specmgr/gol/tools/_io.py
src/biz/dfch/specmgr/gol/tools/list_gol.py
src/biz/dfch/specmgr/gol/tools/_lock.py
src/biz/dfch/specmgr/gol/tools/parse_gol.py
src/biz/dfch/specmgr/gol/tools/_paths.py
src/biz/dfch/specmgr/gol/tools/set_status_gol.py
src/biz/dfch/specmgr/gol/tools/update_gol.py
src/biz/dfch/specmgr/gol/tools/validate_gol.py
src/biz/dfch/specmgr/gol/tools/_write.py
src/biz/dfch/specmgr/__init__.py
src/biz/dfch/specmgr/__main__.py
src/biz/dfch/specmgr/models/adr/__init__.py
src/biz/dfch/specmgr/models/adr/v1/adr.py
src/biz/dfch/specmgr/models/adr/v1/body.py
src/biz/dfch/specmgr/models/adr/v1/frontmatter.py
src/biz/dfch/specmgr/models/adr/v1/__init__.py
src/biz/dfch/specmgr/models/adr/v1/mutations.py
src/biz/dfch/specmgr/models/adr/v1/option.py
src/biz/dfch/specmgr/models/adr/v1/parser.py
src/biz/dfch/specmgr/models/adr/v1/renderer.py
src/biz/dfch/specmgr/models/adr/v1/summary.py
src/biz/dfch/specmgr/models/adr/v1/_util.py
src/biz/dfch/specmgr/models/__init__.py
src/biz/dfch/specmgr/models/iso25010.py
src/biz/dfch/specmgr/models/md/alias_match.py
src/biz/dfch/specmgr/models/md/alias.py
src/biz/dfch/specmgr/models/md/alias_type.py
src/biz/dfch/specmgr/models/md/frontmatter.py
src/biz/dfch/specmgr/models/md/__init__.py
src/biz/dfch/specmgr/models/md/markdown_block_quote.py
src/biz/dfch/specmgr/models/md/markdown_code_block.py
src/biz/dfch/specmgr/models/md/markdown_comment.py
src/biz/dfch/specmgr/models/md/markdown_list_item.py
src/biz/dfch/specmgr/models/md/markdown_paragraph.py
src/biz/dfch/specmgr/models/md/markdown.py
src/biz/dfch/specmgr/models/md/_markdown.py
src/biz/dfch/specmgr/models/md/markdown_section1.py
src/biz/dfch/specmgr/models/md/markdown_section1_with_comment.py
src/biz/dfch/specmgr/models/md/markdown_section2.py
src/biz/dfch/specmgr/models/md/markdown_section2_with_comment.py
src/biz/dfch/specmgr/models/md/markdown_section3.py
src/biz/dfch/specmgr/models/md/markdown_section3_with_comment.py
src/biz/dfch/specmgr/models/md/markdown_section4.py
src/biz/dfch/specmgr/models/md/markdown_section4_with_comment.py
src/biz/dfch/specmgr/models/md/markdown_section5.py
src/biz/dfch/specmgr/models/md/markdown_section5_with_comment.py
src/biz/dfch/specmgr/models/md/markdown_section6.py
src/biz/dfch/specmgr/models/md/markdown_section6_with_comment.py
src/biz/dfch/specmgr/models/md/markdown_section.py
src/biz/dfch/specmgr/models/md/markdown_str.py
src/biz/dfch/specmgr/models/md/_util.py
src/biz/dfch/specmgr/models/version_info.py
src/biz/dfch/specmgr/_paths.py
src/biz/dfch/specmgr/prb/__init__.py
src/biz/dfch/specmgr/prb/models/__init__.py
src/biz/dfch/specmgr/prb/models/v1/body.py
src/biz/dfch/specmgr/prb/models/v1/document.py
src/biz/dfch/specmgr/prb/models/v1/frontmatter.py
src/biz/dfch/specmgr/prb/models/v1/__init__.py
src/biz/dfch/specmgr/prb/models/v1/parser.py
src/biz/dfch/specmgr/prb/models/v1/summary.py
src/biz/dfch/specmgr/prb/models/v1/_util.py
src/biz/dfch/specmgr/prb/prompts/create_prb.py
src/biz/dfch/specmgr/prb/prompts/__init__.py
src/biz/dfch/specmgr/prb/prompts/update_prb.py
src/biz/dfch/specmgr/prb/resources/__init__.py
src/biz/dfch/specmgr/prb/resources/prb_example.py
src/biz/dfch/specmgr/prb/resources/prb_schema.py
src/biz/dfch/specmgr/prb/resources/prb_template.py
src/biz/dfch/specmgr/prb/tools/create_prb.py
src/biz/dfch/specmgr/prb/tools/delete_prb.py
src/biz/dfch/specmgr/prb/tools/get_prb_example.py
src/biz/dfch/specmgr/prb/tools/get_prb.py
src/biz/dfch/specmgr/prb/tools/get_prb_template.py
src/biz/dfch/specmgr/prb/tools/__init__.py
src/biz/dfch/specmgr/prb/tools/_io.py
src/biz/dfch/specmgr/prb/tools/list_prb.py
src/biz/dfch/specmgr/prb/tools/_lock.py
src/biz/dfch/specmgr/prb/tools/parse_prb.py
src/biz/dfch/specmgr/prb/tools/_paths.py
src/biz/dfch/specmgr/prb/tools/set_status_prb.py
src/biz/dfch/specmgr/prb/tools/update_prb.py
src/biz/dfch/specmgr/prb/tools/validate_prb.py
src/biz/dfch/specmgr/prb/tools/_write.py
src/biz/dfch/specmgr/qa/__init__.py
src/biz/dfch/specmgr/qa/models/__init__.py
src/biz/dfch/specmgr/qa/models/v2/body.py
src/biz/dfch/specmgr/qa/models/v2/document.py
src/biz/dfch/specmgr/qa/models/v2/frontmatter.py
src/biz/dfch/specmgr/qa/models/v2/__init__.py
src/biz/dfch/specmgr/qa/models/v2/parser.py
src/biz/dfch/specmgr/qa/models/v2/question_answer.py
src/biz/dfch/specmgr/qa/models/v2/summary.py
src/biz/dfch/specmgr/qa/models/v2/_util.py
src/biz/dfch/specmgr/qa/prompts/create_qa.py
src/biz/dfch/specmgr/qa/prompts/__init__.py
src/biz/dfch/specmgr/qa/prompts/refine.py
src/biz/dfch/specmgr/qa/prompts/update_qa.py
src/biz/dfch/specmgr/qa/resources/__init__.py
src/biz/dfch/specmgr/qa/resources/qa_example.py
src/biz/dfch/specmgr/qa/resources/qa_schema.py
src/biz/dfch/specmgr/qa/resources/qa_template.py
src/biz/dfch/specmgr/qa/tools/create_qa.py
src/biz/dfch/specmgr/qa/tools/delete_qa.py
src/biz/dfch/specmgr/qa/tools/get_qa_example.py
src/biz/dfch/specmgr/qa/tools/get_qa.py
src/biz/dfch/specmgr/qa/tools/get_qa_template.py
src/biz/dfch/specmgr/qa/tools/__init__.py
src/biz/dfch/specmgr/qa/tools/_io.py
src/biz/dfch/specmgr/qa/tools/list_qa.py
src/biz/dfch/specmgr/qa/tools/_lock.py
src/biz/dfch/specmgr/qa/tools/parse_qa.py
src/biz/dfch/specmgr/qa/tools/_paths.py
src/biz/dfch/specmgr/qa/tools/set_status_qa.py
src/biz/dfch/specmgr/qa/tools/update_qa.py
src/biz/dfch/specmgr/qa/tools/validate_qa.py
src/biz/dfch/specmgr/qa/tools/_write.py
src/biz/dfch/specmgr/req/__init__.py
src/biz/dfch/specmgr/req/models/v1/body.py
src/biz/dfch/specmgr/req/models/v1/document.py
src/biz/dfch/specmgr/req/models/v1/frontmatter.py
src/biz/dfch/specmgr/req/models/v1/__init__.py
src/biz/dfch/specmgr/req/models/v1/parser.py
src/biz/dfch/specmgr/req/models/v1/summary.py
src/biz/dfch/specmgr/req/models/v1/_util.py
src/biz/dfch/specmgr/req/prompts/create_req.py
src/biz/dfch/specmgr/req/prompts/__init__.py
src/biz/dfch/specmgr/req/prompts/update_req.py
src/biz/dfch/specmgr/req/resources/__init__.py
src/biz/dfch/specmgr/req/resources/req_example.py
src/biz/dfch/specmgr/req/resources/req_schema.py
src/biz/dfch/specmgr/req/resources/req_template.py
src/biz/dfch/specmgr/req/tools/create_req.py
src/biz/dfch/specmgr/req/tools/delete_req.py
src/biz/dfch/specmgr/req/tools/get_req_example.py
src/biz/dfch/specmgr/req/tools/get_req.py
src/biz/dfch/specmgr/req/tools/get_req_template.py
src/biz/dfch/specmgr/req/tools/__init__.py
src/biz/dfch/specmgr/req/tools/_io.py
src/biz/dfch/specmgr/req/tools/list_req.py
src/biz/dfch/specmgr/req/tools/_lock.py
src/biz/dfch/specmgr/req/tools/parse_req.py
src/biz/dfch/specmgr/req/tools/_paths.py
src/biz/dfch/specmgr/req/tools/set_status_req.py
src/biz/dfch/specmgr/req/tools/update_req.py
src/biz/dfch/specmgr/req/tools/validate_req.py
src/biz/dfch/specmgr/req/tools/_write.py
src/biz/dfch/specmgr/rsk/__init__.py
src/biz/dfch/specmgr/rsk/models/__init__.py
src/biz/dfch/specmgr/rsk/models/v1/assessment.py
src/biz/dfch/specmgr/rsk/models/v1/body.py
src/biz/dfch/specmgr/rsk/models/v1/document.py
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py
src/biz/dfch/specmgr/rsk/models/v1/__init__.py
src/biz/dfch/specmgr/rsk/models/v1/parser.py
src/biz/dfch/specmgr/rsk/models/v1/summary.py
src/biz/dfch/specmgr/rsk/models/v1/_util.py
src/biz/dfch/specmgr/rsk/prompts/create_risk.py
src/biz/dfch/specmgr/rsk/prompts/__init__.py
src/biz/dfch/specmgr/rsk/prompts/update_risk.py
src/biz/dfch/specmgr/rsk/resources/__init__.py
src/biz/dfch/specmgr/rsk/resources/risk_matrix.py
src/biz/dfch/specmgr/rsk/resources/rsk_example.py
src/biz/dfch/specmgr/rsk/resources/rsk_schema.py
src/biz/dfch/specmgr/rsk/resources/rsk_template.py
src/biz/dfch/specmgr/rsk/resources/tara.py
src/biz/dfch/specmgr/rsk/tools/create_rsk.py
src/biz/dfch/specmgr/rsk/tools/delete_rsk.py
src/biz/dfch/specmgr/rsk/tools/get_rsk_example.py
src/biz/dfch/specmgr/rsk/tools/get_rsk.py
src/biz/dfch/specmgr/rsk/tools/get_rsk_template.py
src/biz/dfch/specmgr/rsk/tools/__init__.py
src/biz/dfch/specmgr/rsk/tools/_io.py
src/biz/dfch/specmgr/rsk/tools/list_rsk.py
src/biz/dfch/specmgr/rsk/tools/_lock.py
src/biz/dfch/specmgr/rsk/tools/parse_rsk.py
src/biz/dfch/specmgr/rsk/tools/_paths.py
src/biz/dfch/specmgr/rsk/tools/set_status_rsk.py
src/biz/dfch/specmgr/rsk/tools/update_rsk.py
src/biz/dfch/specmgr/rsk/tools/validate_rsk.py
src/biz/dfch/specmgr/rsk/tools/_write.py
src/biz/dfch/specmgr/server.py
src/biz/dfch/specmgr/tsk/__init__.py
src/biz/dfch/specmgr/tsk/models/__init__.py
src/biz/dfch/specmgr/tsk/models/v1/body.py
src/biz/dfch/specmgr/tsk/models/v1/document.py
src/biz/dfch/specmgr/tsk/models/v1/frontmatter.py
src/biz/dfch/specmgr/tsk/models/v1/__init__.py
src/biz/dfch/specmgr/tsk/models/v1/parser.py
src/biz/dfch/specmgr/tsk/models/v1/summary.py
src/biz/dfch/specmgr/tsk/models/v1/task_item.py
src/biz/dfch/specmgr/tsk/models/v1/_util.py
src/biz/dfch/specmgr/tsk/prompts/create_task.py
src/biz/dfch/specmgr/tsk/prompts/implement_task.py
src/biz/dfch/specmgr/tsk/prompts/__init__.py
src/biz/dfch/specmgr/tsk/prompts/update_task.py
src/biz/dfch/specmgr/tsk/resources/__init__.py
src/biz/dfch/specmgr/tsk/resources/tsk_example.py
src/biz/dfch/specmgr/tsk/resources/tsk_schema.py
src/biz/dfch/specmgr/tsk/resources/tsk_template.py
src/biz/dfch/specmgr/tsk/tools/create_tsk.py
src/biz/dfch/specmgr/tsk/tools/delete_tsk.py
src/biz/dfch/specmgr/tsk/tools/get_tsk_example.py
src/biz/dfch/specmgr/tsk/tools/get_tsk.py
src/biz/dfch/specmgr/tsk/tools/get_tsk_template.py
src/biz/dfch/specmgr/tsk/tools/__init__.py
src/biz/dfch/specmgr/tsk/tools/_io.py
src/biz/dfch/specmgr/tsk/tools/list_tsk.py
src/biz/dfch/specmgr/tsk/tools/_lock.py
src/biz/dfch/specmgr/tsk/tools/parse_tsk.py
src/biz/dfch/specmgr/tsk/tools/_paths.py
src/biz/dfch/specmgr/tsk/tools/set_status_tsk.py
src/biz/dfch/specmgr/tsk/tools/update_tsk.py
src/biz/dfch/specmgr/tsk/tools/validate_tsk.py
src/biz/dfch/specmgr/tsk/tools/_write.py
src/biz/dfch/specmgr/uc/__init__.py
src/biz/dfch/specmgr/uc/models/__init__.py
src/biz/dfch/specmgr/uc/models/v1/characteristic_information.py
src/biz/dfch/specmgr/uc/models/v1/extension_action.py
src/biz/dfch/specmgr/uc/models/v1/extension.py
src/biz/dfch/specmgr/uc/models/v1/extensions.py
src/biz/dfch/specmgr/uc/models/v1/__init__.py
src/biz/dfch/specmgr/uc/models/v1/main_success_scenario.py
src/biz/dfch/specmgr/uc/models/v1/open_issues.py
src/biz/dfch/specmgr/uc/models/v1/parser.py
src/biz/dfch/specmgr/uc/models/v1/related_information.py
src/biz/dfch/specmgr/uc/models/v1/related_use_cases.py
src/biz/dfch/specmgr/uc/models/v1/step.py
src/biz/dfch/specmgr/uc/models/v1/sub_variation.py
src/biz/dfch/specmgr/uc/models/v1/sub_variations.py
src/biz/dfch/specmgr/uc/models/v1/uc_diagram.py
src/biz/dfch/specmgr/uc/models/v1/use_case_frontmatter.py
src/biz/dfch/specmgr/uc/models/v1/use_case.py
src/biz/dfch/specmgr/uc/models/v2/document.py
src/biz/dfch/specmgr/uc/models/v2/frontmatter.py
src/biz/dfch/specmgr/uc/models/v2/__init__.py
src/biz/dfch/specmgr/uc/models/v2/parser.py
src/biz/dfch/specmgr/uc/models/v2/summary.py
src/biz/dfch/specmgr/uc/models/v2/use_case.py
src/biz/dfch/specmgr/uc/models/v2/_util.py
src/biz/dfch/specmgr/uc/resources/__init__.py
src/biz/dfch/specmgr/uc/resources/uc_example.py
src/biz/dfch/specmgr/uc/resources/uc_schema.py
src/biz/dfch/specmgr/uc/resources/uc_template.py
src/biz/dfch/specmgr/uc/tools/create_uc.py
src/biz/dfch/specmgr/uc/tools/delete_uc.py
src/biz/dfch/specmgr/uc/tools/get_uc_example.py
src/biz/dfch/specmgr/uc/tools/get_uc.py
src/biz/dfch/specmgr/uc/tools/get_uc_template.py
src/biz/dfch/specmgr/uc/tools/__init__.py
src/biz/dfch/specmgr/uc/tools/_io.py
src/biz/dfch/specmgr/uc/tools/list_uc.py
src/biz/dfch/specmgr/uc/tools/_lock.py
src/biz/dfch/specmgr/uc/tools/parse_uc.py
src/biz/dfch/specmgr/uc/tools/_paths.py
src/biz/dfch/specmgr/uc/tools/set_status_uc.py
src/biz/dfch/specmgr/uc/tools/update_uc.py
src/biz/dfch/specmgr/uc/tools/validate_uc.py
src/biz/dfch/specmgr/uc/tools/_write.py

```

**Tool: grep**

**Input:**

```json
{
  "pattern": "def (update|_resolve|resolve_id|_id_to_path|_find_by_id)",
  "include": "*.py",
  "path": "src"
}
```

**Output:**

```
Found 18 matches
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/tools/update_qa.py:
  Line 58: def update_qa(id: str, content: str) -> QaDocument:


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/prompts/update_qa.py:
  Line 61: def update_qa(id: str, instructions: str | None = None) -> str:


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/tools/update_frontmatter.py:
  Line 42: def update_frontmatter(id: str, frontmatter: AdrFrontmatter) -> Adr:


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/tools/update_section.py:
  Line 48: def update_section(id: str, key: str, value: str) -> Adr:


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/prompts/update_adr.py:
  Line 52: def update_adr(id: str, instructions: str | None = None) -> str:


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/prompts/update_adr_test.py:
  Line 60: def update_adr_test(id: str, instructions: str | None = None) -> str:


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/tools/update_prb.py:
  Line 57: def update_prb(id: str, content: str) -> PrbDocument:


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/tools/update_req.py:
  Line 57: def update_req(id: str, content: str) -> ReqDocument:


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/prompts/update_req.py:
  Line 60: def update_req(id: str, instructions: str | None = None) -> str:


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/prompts/update_prb.py:
  Line 70: def update_prb(id: str, instructions: str | None = None) -> str:


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/tools/update_rsk.py:
  Line 57: def update_rsk(id: str, content: str) -> RskDocument:


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/uc/tools/update_uc.py:
  Line 57: def update_uc(id: str, content: str) -> UcDocument:


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/adr/v1/mutations.py:
  Line 94: def update_section(adr: Adr, key: str, value: str) -> Adr:


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/prompts/update_risk.py:
  Line 64: def update_risk(id: str, instructions: str | None = None) -> str:


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/tools/update_gol.py:
  Line 57: def update_gol(id: str, content: str) -> GolDocument:


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/tools/update_tsk.py:
  Line 57: def update_tsk(id: str, content: str) -> TskDocument:


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/prompts/update_gol.py:
  Line 74: def update_gol(id: str) -> str:


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/prompts/update_task.py:
  Line 64: def update_task(id: str, instructions: str | None = None) -> str:

```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 37.2s)

_Thinking:_

Let's read a few key files to understand the structure of the update tool and how the ID→path resolution works:

1. req/tools/update_req.py (representative whole-body update)
2. req/tools/\_write.py and req/tools/\_io.py (shared helpers)
3. req/tools/\_paths.py
4. general/tools/\_doc_paths.py (the cross-domain path helper — interesting, this is in general/tools!)
5. server.py (docstring)

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/tools/update_req.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/tools/update_req.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """``@mcp.tool()`` wrapper: update_req (Task 3.13).
19: 
20: Same body-only ``content`` shape as ``create_req`` (Task 3.12), but against
21: an *existing* document: ``id``/``type``/``status``/``created``/``version``
22: are all read back from the file currently on disk and preserved unchanged;
23: only ``updated`` is bumped to the current timestamp. ``status`` is never
24: settable here -- see the dedicated ``set_status_req`` tool (Task 3.14).
25: 
26: Thin file-I/O/id-lookup adapter, re-reading and re-parsing the current
27: on-disk state before re-writing the full file; there is no in-memory cache
28: of a parsed :class:`~biz.dfch.specmgr.req.models.v1.ReqDocument` -- the
29: ``.md`` file itself is always the source of truth. The whole sequence runs
30: under ``req_lock(id)`` so a concurrent mutation against the same id cannot
31: interleave with it and cause a lost update (mirrors every ADR mutation
32: tool's own ``adr_lock`` usage).
33: """
34: 
35: from __future__ import annotations
36: 
37: from datetime import datetime
38: 
39: from ...models.md._markdown import format_text
40: from ...server import mcp
41: from ..models.v1 import ReqDocument, ReqFrontmatter, Requirement
42: from ._io import load_by_id
43: from ._lock import req_lock
44: from ._paths import req_base_dir
45: from ._write import write_req_file
46: 
47: 
48: @mcp.tool(
49:     name="update_req",
50:     title="Update requirement",
51:     description=(
52:         "Whole-body replace of an existing requirement's content, preserving its "
53:         "id/type/status/created/version; only `updated` changes. Use `set_status_req` to "
54:         "change status instead."
55:     ),
56: )
57: def update_req(id: str, content: str) -> ReqDocument:
58:     """Replace the body of the requirement identified by ``id``.
59: 
60:     ``content`` is body markdown only, same shape as :func:`.create_req.create_req`
61:     -- it must not carry a YAML frontmatter block. Validated the same way:
62:     ``Requirement.from_text(format_text(content))``, letting ``AssertionError``
63:     (structural failure) or ``pydantic.ValidationError`` (field/cross-field
64:     failure) propagate uncaught, with nothing written in either case.
65: 
66:     The existing file is read first (under ``req_lock(id)``) to resolve its
67:     path and current frontmatter; every frontmatter field except ``updated``
68:     is carried over unchanged -- ``status`` in particular is never settable
69:     through this tool.
70: 
71:     Parameters
72:     ----------
73:     id:
74:         The document's specmgr-assigned identifier.
75:     content:
76:         The replacement body markdown, with no frontmatter block.
77: 
78:     Returns
79:     -------
80:     ReqDocument
81:         The updated document. Raises :class:`._paths.ReqNotFoundError` if
82:         no requirement has this id.
83:     """
84:     body = Requirement.from_text(format_text(content))
85: 
86:     base_dir = req_base_dir()
87:     with req_lock(id):
88:         path, existing = load_by_id(base_dir, id)
89:         now = datetime.now().isoformat(timespec="microseconds")
90:         fm_data = existing.frontmatter.model_dump()
91:         fm_data["updated"] = now
92:         new_frontmatter = ReqFrontmatter(**fm_data)
93:         new_doc = ReqDocument(frontmatter=new_frontmatter, body=body)
94:         write_req_file(path, new_frontmatter, content)
95:     return new_doc

(End of file - total 95 lines)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/tools/_write.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/tools/_write.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """Shared frontmatter+body composition/write helper for ``create_req``/``update_req``
19: (Tasks 3.12/3.13).
20: 
21: Deliberately **not** part of ``req.tools._io`` -- that module's own docstring
22: rules out a ``write_req``/``render_req`` counterpart to ``read_req``, since
23: Task 3.9's design never renders a body back out from a parsed
24: :class:`~biz.dfch.specmgr.req.models.v1.ReqDocument` model (unlike
25: ``adr.tools._io.write_adr``, which does via ``render_adr``). What
26: :func:`write_req_file` does instead is a strictly narrower thing: combine an
27: already-constructed, already-validated
28: :class:`~biz.dfch.specmgr.req.models.v1.ReqFrontmatter` with the caller's own
29: already-validated *raw* body text (never reformatted/re-rendered) into one
30: file. Factored out of ``create_req.py`` into its own module so
31: ``update_req.py`` (Task 3.13) does not have to duplicate it.
32: """
33: 
34: from __future__ import annotations
35: 
36: from pathlib import Path
37: 
38: import frontmatter
39: 
40: from ..models.v1 import ReqFrontmatter
41: 
42: __all__ = ["write_req_file"]
43: 
44: 
45: def write_req_file(path: Path, frontmatter_: ReqFrontmatter, content: str) -> None:
46:     """Compose a full requirement file (frontmatter + body) and write it to ``path``.
47: 
48:     ``content`` is embedded verbatim -- it is never reformatted/re-rendered
49:     here. One caveat inherent to the underlying ``python-frontmatter``
50:     library, not specially handled here: its ``YAMLHandler`` strips trailing
51:     whitespace from ``content`` when serializing, so the written body may
52:     differ from ``content`` by trailing whitespace only, never in substance.
53: 
54:     Parameters
55:     ----------
56:     path:
57:         The destination file path.
58:     frontmatter_:
59:         The already-constructed, already-validated frontmatter to serialize
60:         as the file's YAML block.
61:     content:
62:         The raw body markdown, exactly as submitted by the caller.
63:     """
64:     post = frontmatter.Post(content=content, **frontmatter_.model_dump())
65:     text = frontmatter.dumps(post)
66:     if not text.endswith("\n"):
67:         text += "\n"
68:     path.write_text(text, encoding="utf-8")

(End of file - total 68 lines)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/_doc_paths.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/_doc_paths.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """Generic, doc-type-agnostic base directory resolution, filename slugification,
19: and id -> path lookup (plan Task 3.10).
20: 
21: Generalizes ``adr.tools._paths``'s shape into a single module shared across
22: document domains (REQ now, UC later) instead of a copy per domain: one root
23: env var (:data:`DOCS_DIR_ENV_VAR`, default :data:`DEFAULT_DOCS_ROOT`) holds
24: every doc type's own subdirectory (``{root}/{type_name}/``, e.g. ``docs/req/``
25: for ``type_name="req"``).
26: 
27: **ADR is deliberately left untouched** -- it keeps its own
28: ``SPECMGR_ADR_DIR``/``docs/adr`` env var and default (``adr.tools._paths``).
29: Migrating ADR onto this shared module is optional future cleanup, not
30: bundled into this change.
31: 
32: As with ``adr.tools._paths``, this module has no ``mcp``/file-write
33: dependency beyond read-only directory listing: :func:`doc_base_dir` never
34: creates the directory (a read-only tool shouldn't have that side effect),
35: only :func:`ensure_doc_base_dir` does. There is deliberately no in-memory
36: id -> path cache either -- every lookup re-scans the base directory and
37: re-parses each file, matching this codebase's "the on-disk file is the sole
38: source of truth" design.
39: """
40: 
41: from __future__ import annotations
42: 
43: import os
44: import re
45: from collections.abc import Callable, Iterator
46: from pathlib import Path
47: from typing import TypeVar
48: 
49: __all__ = [
50:     "DEFAULT_DOCS_ROOT",
51:     "DOCS_DIR_ENV_VAR",
52:     "DocNotFoundError",
53:     "doc_base_dir",
54:     "ensure_doc_base_dir",
55:     "find_doc_path_by_id",
56:     "iter_doc_paths",
57:     "slugify",
58: ]
59: 
60: #: Environment variable that overrides the shared documents root directory.
61: DOCS_DIR_ENV_VAR = "SPECMGR_DOCS_DIR"
62: 
63: #: Default documents root directory, relative to the current working directory.
64: DEFAULT_DOCS_ROOT = Path("docs")
65: 
66: #: Anything that isn't a lowercase ASCII letter or digit, run-collapsed.
67: _NON_ALNUM_RUN_PATTERN = re.compile(r"[^a-z0-9]+")
68: 
69: #: Maximum length of a slugified title (mirrors ``adr.tools._paths``'s filename scheme).
70: _SLUG_MAX_LENGTH = 60
71: 
72: #: Fallback slug used when a title has no alphanumeric characters at all.
73: _FALLBACK_SLUG = "doc"
74: 
75: #: Parsed-document type returned by a caller-supplied ``parse_fn``.
76: _DocT = TypeVar("_DocT")
77: 
78: 
79: class DocNotFoundError(LookupError):
80:     """No document file found matching the given id, under a given base directory."""
81: 
82: 
83: def _docs_root() -> Path:
84:     """Return the configured documents root directory, without creating it."""
85:     value = os.environ.get(DOCS_DIR_ENV_VAR)
86:     result = Path(value) if value else DEFAULT_DOCS_ROOT
87:     return result
88: 
89: 
90: def doc_base_dir(type_name: str) -> Path:
91:     """Return the base directory for ``type_name`` documents, without creating it.
92: 
93:     Reads :data:`DOCS_DIR_ENV_VAR` from the environment, falling back to
94:     :data:`DEFAULT_DOCS_ROOT`, then appends ``type_name`` as a subdirectory
95:     (e.g. ``docs/req`` for ``type_name="req"``). Read-only tools/resources
96:     use this so merely reading never has the side effect of creating the
97:     directory -- see :func:`ensure_doc_base_dir` for the write path.
98: 
99:     Parameters
100:     ----------
101:     type_name:
102:         The document type's subdirectory name, e.g. ``"req"``.
103: 
104:     Returns
105:     -------
106:     Path
107:         The resolved base directory for ``type_name`` documents.
108:     """
109:     assert isinstance(type_name, str), type(type_name)
110:     assert type_name.strip()
111: 
112:     result = _docs_root() / type_name
113:     return result
114: 
115: 
116: def ensure_doc_base_dir(type_name: str) -> Path:
117:     """Return the base directory for ``type_name`` documents, creating it if missing.
118: 
119:     Only a doc type's ``create_*`` tool should call this -- every other
120:     tool/resource uses the read-only :func:`doc_base_dir` instead.
121: 
122:     Parameters
123:     ----------
124:     type_name:
125:         The document type's subdirectory name, e.g. ``"req"``.
126: 
127:     Returns
128:     -------
129:     Path
130:         The resolved, now-guaranteed-to-exist base directory for
131:         ``type_name`` documents.
132:     """
133:     assert isinstance(type_name, str), type(type_name)
134:     assert type_name.strip()
135: 
136:     result = doc_base_dir(type_name)
137:     result.mkdir(parents=True, exist_ok=True)
138:     return result
139: 
140: 
141: def slugify(title: str) -> str:
142:     """Derive a filename-safe slug from a document title.
143: 
144:     Ported from ``adr.tools._paths.slugify`` unchanged: lowercases
145:     ``title``, collapses every run of non-``[a-z0-9]`` characters into a
146:     single ``-``, strips leading/trailing ``-``, truncates to
147:     :data:`_SLUG_MAX_LENGTH` characters (stripping a trailing ``-`` again in
148:     case the truncation lands mid-run), and falls back to
149:     :data:`_FALLBACK_SLUG` if the result would otherwise be empty (e.g. a
150:     title with no alphanumeric characters at all).
151: 
152:     Parameters
153:     ----------
154:     title:
155:         The document title to slugify.
156: 
157:     Returns
158:     -------
159:     str
160:         The filename-safe slug.
161:     """
162:     assert isinstance(title, str), type(title)
163: 
164:     slug = _NON_ALNUM_RUN_PATTERN.sub("-", title.lower()).strip("-")
165:     slug = slug[:_SLUG_MAX_LENGTH].strip("-")
166:     result = slug or _FALLBACK_SLUG
167:     return result
168: 
169: 
170: def iter_doc_paths(base_dir: Path) -> Iterator[Path]:
171:     """Yield every ``*.md`` file directly under ``base_dir``, sorted by name.
172: 
173:     Yields nothing (rather than raising) if ``base_dir`` does not exist.
174: 
175:     Parameters
176:     ----------
177:     base_dir:
178:         The directory to scan for ``*.md`` files.
179: 
180:     Returns
181:     -------
182:     Iterator[Path]
183:         An iterator over the matching, sorted paths.
184:     """
185:     assert isinstance(base_dir, Path), type(base_dir)
186: 
187:     if not base_dir.exists():
188:         return iter(())
189:     result = iter(sorted(base_dir.glob("*.md")))
190:     return result
191: 
192: 
193: def find_doc_path_by_id(
194:     base_dir: Path,
195:     id_: str,
196:     parse_fn: Callable[[str], _DocT],
197:     get_id_fn: Callable[[_DocT], str | None],
198: ) -> Path:
199:     """Resolve an ``id`` to its on-disk file path, for any doc type.
200: 
201:     Scans every ``*.md`` file under ``base_dir``, parsing each via
202:     ``parse_fn`` and comparing ``get_id_fn(parsed)`` against ``id_``. A file
203:     that fails to parse (``AssertionError`` or ``ValueError``, which
204:     ``pydantic.ValidationError`` and every parser-specific error in this
205:     codebase -- e.g. ``AdrParseError`` -- subclass) is silently skipped --
206:     one broken file must not prevent lookup of a different, valid id.
207: 
208:     Parameters
209:     ----------
210:     base_dir:
211:         The directory to scan for ``*.md`` files.
212:     id_:
213:         The id to look up.
214:     parse_fn:
215:         Parses a file's full text into a document object (e.g. ``parse_adr``,
216:         ``parse_req``).
217:     get_id_fn:
218:         Extracts the id (or ``None``) from a parsed document object (e.g.
219:         ``lambda doc: doc.frontmatter.id``).
220: 
221:     Returns
222:     -------
223:     Path
224:         The resolved file path.
225: 
226:     Raises
227:     ------
228:     DocNotFoundError
229:         If no file's parsed id matches ``id_``.
230:     """
231:     assert isinstance(base_dir, Path), type(base_dir)
232:     assert isinstance(id_, str), type(id_)
233:     assert id_.strip()
234: 
235:     for path in iter_doc_paths(base_dir):
236:         try:
237:             doc = parse_fn(path.read_text(encoding="utf-8"))
238:         except (AssertionError, ValueError):
239:             continue
240:         if get_id_fn(doc) == id_:
241:             return path
242:     raise DocNotFoundError(
243:         f"no document found with id {id_!r} under {base_dir}. The id must be the bare document UUID, without "
244:         f"a domain prefix."
245:     )

(End of file - total 245 lines)
</content>
```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 136.6s)

_Thinking:_

Now I understand the shared infrastructure. The 7 non-ADR domains all use `general/tools/_doc_paths.py`, using `doc_base_dir(type_name)`, and each has its own `_io.load_by_id`, `_write.write_*_file`, `_lock`.

Key insight: all 7 update tools are structurally identical:

1. Validate content with domain-specific `from_text(format_text(content))`
2. Under lock, `load_by_id(base_dir, id)`
3. Preserve frontmatter, update `updated`
4. `write_*_file(path, frontmatter, content)`
5. Return the new document

The differences are: the domain model class, the base directory name, the lock, the frontmatter type, and the write helper.

For ADR: it has its own directory (SPECMGR_ADR_DIR), its own \_paths, and the semantics of update are different (per-section + frontmatter + options). ADR does not have a whole-body update tool.

Now, options for a unified `update` tool:

**Option A: A single `update` tool with `id` + `type` parameters.**

- `type` is an enum: "req" | "uc" | "tsk" | "qa" | "prb" | "gol" | "rsk" (ADR excluded, or include it with different content semantics?).
- A dispatch dict maps type -> (base_dir, parse/validate, write, lock, frontmatter type).
- Delete the 7 per-domain update tools.

**Option B: A single `update` tool with `id` only.**

- Need to scan all domain directories to resolve id -> (type, path). Use `find_doc_path_by_id` against each domain directory in turn.
- The error message in `_doc_paths.py` is interesting: "The id must be the bare document UUID, without a domain prefix." — so the id is a bare UUID, and there's an established convention of no prefix.
- Cost: scan up to 7 directories (ADR's directory too?), parsing every file until a match. Each `get_*`/`list_*` tool already does a full directory scan, so this is consistent with the existing performance profile.
- Risk: UUID collision across domains is theoretically possible (independently generated v4 UUIDs) — practically zero, but in that case which one do we update? We'd need a defined order or a report. With explicit `type`, no ambiguity.

The user is asking for my opinion. I think Option A (`id` + `type`) is cleaner, but Option B (`id` only) is what the user is leaning toward ("or just `uuid`, because uuid is unique"). Let me consider which is better.

Arguments in favor of `type` + `id`:

- Deterministic, no scanning, no theoretical collision issue.
- The LLM client knows the type (it just did `create_rsk` / `get_rsk` / `list_rsk`).
- Explicit in tool parameters; self-documenting.
- Simpler error handling: "id not found under docs/rsk".

Arguments in favor of `id` only:

- One fewer parameter; the user's point that uuid is unique.
- But the server has to scan all domains to find which one owns the id — and this codebase has a deliberate "no in-memory id -> path cache" design, so it'll re-parse every file in every domain directory on every update. For a write path this is heavier (though still fine — directories are small).
- ADR has a separate directory scheme (SPECMGR_ADR_DIR), and the ADR frontmatter's `id` docstring explicitly says the id is "used to resolve id -> file path (plan §9a)". If ADR ids live in the same UUID space, a bare-uuid update tool would have to include ADR too — but ADR has no whole-body update semantics. So even the uuid-only tool can't cover ADR without adding new ADR semantics. That's a strong argument: the scope of "all update commands" includes ADR's update_frontmatter/update_section/option_update, which can't be unified into whole-body content replacement.

So the real design question is: what is the scope of the unification?

1. **Only the 7 whole-body updates** (req, uc, tsk, qa, prb, gol, rsk) → a single `update(id, type, content)` tool. ADR's tools are unchanged (its update surface is different by design — MADR section model).
2. **All updates including ADR** → would require a whole-body `update_adr` (breaking ADR's design philosophy), or a heterogeneous `update` tool whose `content` meaning depends on `type` (ugly contract).

I recommend scope 1.

And within scope 1, `id` + `type` vs `id` only:

- I'd recommend **`id` + `type`** for the reasons above, but I'll honestly present both and ask the user. Actually wait — let me think about what's best for the LLM consumer. When the LLM calls `update`, it always knows which domain it's working in (the previous tool calls were domain-specific). So `type` is zero extra cognitive cost. And a `type` enum with 7 values + future `ac` etc. is trivially extensible.

Hmm, but the user explicitly said "or just `uuid`, because uuid is unique". They're asking my opinion. Let me weigh it once more:

- Uniqueness: the UUIDs are server-generated v4, independent per domain. Unique in practice. But "in practice" isn't the same as "guaranteed" — and more importantly, the resolution mechanism has to *find* the owning domain, which means either a scan (all domain directories, parse every file) or an index. The scan approach: the error message "no document found with id X under {base_dir}" becomes "not found under any domain" — and if we don't find it we've done N× the work.
- There's also a subtle correctness point: `find_doc_path_by_id` skips unparseable files. In a multi-domain scan, a corrupted file in domain A doesn't block finding an id in domain B — fine.
- Cost-wise: each domain directory scan parses every file in that domain. `update_rsk` today parses every file in docs/rsk. A uuid-only `update` would parse every file in all 7 directories (until a match; worst case all 7). On a write path, this is N× slower than it needs to be, and N grows with each new domain (ac, ...). With `type`, cost stays constant.

So my recommendation: a single `update` tool with `id` + `type` + `content`, scoped to the 7 whole-body domains; ADR keeps its per-section tools; the 7 per-domain update\_\* tools get deleted; the per-domain prompts that reference update\_\* need updating (update_req prompt, update_gol, update_prb, update_qa, update_task, update_risk, and ADR's update_adr is unchanged); server.py docstring; the auto-generated docs/MCP.md; tests.

Wait — should I also consider whether `type` should include "adr" for uniformity, and the tool just rejects it with a clear error, or excludes it from the enum entirely? I think exclusion from the enum is cleaner (the enum documents what the tool can actually do). Pydantic/Litellm... the MCP tool decorator here takes a plain function with typed parameters — how does it build the JSON schema? `type` would probably be an enum via `Literal` or a str with validation. Let me check how the tool declares parameters — the MCP python SDK builds the schema from type hints. `Literal["req","uc",...]` works.

Also: there's a generic `set_status` (ADR) and 7 per-domain `set_status_*`. Should this feature include unifying status too? The user said "consolidate all update commands". I'll mention it as an adjacent option (scope question), but by default keep it out or ask.

Also naming: a tool named `update` at the top level. The MCP tool name is a flat string; other tools are `update_req` etc. The new one would be `update`. Fine.

Where to put it? The `general/tools/` package is "cross-cutting, non-domain-specific" — a natural home: `general/tools/update.py`. It'll need per-domain dispatch: import each domain's model/write/lock helpers. Check for circular imports: `general` is imported by... `server.py` imports all domains; do domains import `general`? Let me check: `general/models/paged_result.py` and `summary.py` are used by list tools (imported from domain tools). So domains already import from general → general importing from domains for dispatch would be circular! Need to check the actual imports.

Actually wait: does `req/tools/list_req.py` import from `general/models/summary.py`? Probably. If `general/tools/update.py` imports `req/tools/_io.py` etc., and `req/tools/__init__.py` imports list_req, and list_req imports general.models.summary (not general.tools), then general.tools.update → req.tools → (package __init__?) — Python imports the whole package, so importing `req.tools._io` will trigger `req/tools/__init__.py` and `req/__init__.py`. If any module in the req.tools package imports from `general.tools` (circular), boom. Let me check what req/tools/__init__.py and the \_io modules import.

Let me read:

- req/tools/__init__.py
- req/tools/\_io.py
- general/tools/__init__.py
- server.py (docstring)
- one more update tool to confirm identical shape (rsk/tools/update_rsk.py) — I'll trust the pattern.
- the update prompt (req/prompts/update_req.py) to see which tool names are referenced.

Also check tests: tests/ directory structure for update tests.

Now let me look at the shared infrastructure, imports (for circularity concerns), the server docstring, and tests.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/tools/_io.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/tools/_io.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """Thin file read helpers over ``parse_req`` (Task 3.11).
19: 
20: Read-only, unlike ``adr.tools._io``'s ``read_adr``/``write_adr`` pair: there
21: is no ``write_req``/``render_req`` counterpart here, since Task 3.9's design
22: settled on ``create_req``/``update_req`` (Tasks 3.12/3.13) persisting the
23: caller's already-validated body markdown byte-for-byte rather than rendering
24: it back out from a parsed model -- no renderer is needed for that shape, so
25: none is added speculatively here.
26: 
27: No ``mcp`` dependency here either -- these are plain file-I/O adapters, kept
28: separate from any future ``@mcp.tool()``-decorated function so they stay
29: independently testable.
30: """
31: 
32: from __future__ import annotations
33: 
34: from pathlib import Path
35: 
36: from ..models.v1 import ReqDocument, parse_req
37: from ._paths import find_req_path
38: 
39: __all__ = ["load_by_id", "read_req"]
40: 
41: 
42: def read_req(path: Path) -> ReqDocument:
43:     """Read and parse the requirement at ``path``.
44: 
45:     Parameters
46:     ----------
47:     path:
48:         The filesystem path to the requirement ``.md`` file.
49: 
50:     Returns
51:     -------
52:     ReqDocument
53:         The parsed, validated document.
54:     """
55:     assert isinstance(path, Path), type(path)
56: 
57:     result = parse_req(path.read_text(encoding="utf-8"))
58:     return result
59: 
60: 
61: def load_by_id(base_dir: Path, id_: str) -> tuple[Path, ReqDocument]:
62:     """Resolve ``id_`` under ``base_dir`` and read the matching requirement.
63: 
64:     Parameters
65:     ----------
66:     base_dir:
67:         The directory to scan for ``*.md`` files.
68:     id_:
69:         The id to look up.
70: 
71:     Returns
72:     -------
73:     tuple[Path, ReqDocument]
74:         The resolved file path and the parsed document -- callers that
75:         mutate the document need the path to write it back afterward.
76: 
77:     Raises
78:     ------
79:     ReqNotFoundError
80:         If no file matches (propagated from :func:`._paths.find_req_path`).
81:     """
82:     assert isinstance(base_dir, Path), type(base_dir)
83:     assert isinstance(id_, str), type(id_)
84:     assert id_.strip()
85: 
86:     path = find_req_path(base_dir, id_)
87:     result = (path, read_req(path))
88:     return result

(End of file - total 88 lines)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/tools/__init__.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/tools/__init__.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """MCP tool wrappers for requirements (mirrors ``uc/tools/``'s own shape).
19: 
20: ``parse_req`` reads a raw filepath, parses, and validates it into a structured
21: document model. ``get_req_example`` returns a complete, valid sample requirement
22: document as raw markdown (Task 3.6); ``get_req_template`` returns a document
23: with every field present but populated with short placeholder ("blind text")
24: content instead (Task 3.7) -- both read a packaged, build-guaranteed data file
25: rather than anything on the caller's filesystem. ``get_req`` (feat-7-various-
26: improvements Task 0.9) reads, parses, and returns a full requirement document
27: by id -- the sole id-based read path for REQ, replacing the former
28: ``specmgr://req/{id}`` resource (see ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).
29: ``list_req`` (feat-13-list-paging Task 2.2) returns one page of id/title/
30: status/ref summaries of every requirement, replacing the former
31: ``specmgr://req/list`` resource so that ``max_results``/``offset`` paging
32: parameters could be accepted (see
33: ``.specmgr/feat/feat-13-list-paging/README.md``). ``create_req`` (Task 3.12)
34: assigns a fresh id, builds the frontmatter itself, and writes a new document
35: (body markdown only, no frontmatter) under the requirement base directory
36: (``req.tools._paths``/``_io``). ``update_req`` (Task 3.13) replaces an
37: existing document's body the same way, preserving every frontmatter field
38: except ``updated``. ``set_status_req`` (Task 3.14) is the only path that
39: changes ``status``, also bumping ``updated``, leaving the body untouched.
40: ``delete_req`` (Task 3.15) is a registered stub -- always raises
41: ``NotImplementedError``, reserving the name for a future real
42: implementation. ``validate_req`` (Task 3.16) is a disk-free, id-free dry
43: run against a submitted ``content`` string, independent of the other
44: tools. Import this package to register all requirement tools at once::
45: 
46:     from biz.dfch.specmgr.req import tools  # noqa: F401 (side-effects only)
47: """
48: 
49: from .create_req import create_req
50: from .delete_req import delete_req
51: from .get_req import get_req
52: from .get_req_example import get_req_example
53: from .get_req_template import get_req_template
54: from .list_req import list_req
55: from .parse_req import parse_req
56: from .set_status_req import set_status_req
57: from .update_req import update_req
58: from .validate_req import validate_req
59: 
60: __all__ = [
61:     "create_req",
62:     "delete_req",
63:     "get_req",
64:     "get_req_example",
65:     "get_req_template",
66:     "list_req",
67:     "parse_req",
68:     "set_status_req",
69:     "update_req",
70:     "validate_req",
71: ]

(End of file - total 71 lines)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/__init__.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/__init__.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """MCP tool wrappers for general-purpose utilities (mirrors ``adr/tools/``'s shape).
19: 
20: ``mdformat`` -- a markdown document formatter that preserves YAML frontmatter
21: blocks (for ADR/UC files) and formats only the body markdown. ``webfetch`` --
22: a bearer-authenticated HTTP GET fetch restricted to a configured base URL.
23: Import this package to register all general tools at once::
24: 
25:     from biz.dfch.specmgr.general import tools  # noqa: F401 (side-effects only)
26: """
27: 
28: from .mdformat import mdformat
29: from .webfetch import webfetch
30: 
31: __all__ = [
32:     "mdformat",
33:     "webfetch",
34: ]

(End of file - total 34 lines)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/server.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/server.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """MCP server for ``biz-dfch-specmgr``.
19: 
20: Requires the ``mcp`` extra (``pip install biz-dfch-specmgr[mcp]``).
21: 
22: Registers the following resources and tools so far (plan §8, §9a):
23: 
24: Resources
25: ---------
26: specmgr://version --    Installed version number of the ``biz-dfch-specmgr`` package.
27: specmgr://adr/{id} --    Full ADR document for a given id (``.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md``).
28: specmgr://req/schema -- The generated REQ JSON Schema, read from a packaged data copy
29:                         (kept in sync with ``docs/req_schema.json``) so it works from a
30:                         real, non-editable install.
31: specmgr://req/example -- A complete, valid sample requirement document as raw markdown.
32: specmgr://req/template -- A requirement template (every field present, placeholder text)
33:                           as raw markdown.
34: specmgr://uc/schema --  The generated UC JSON Schema, read from a packaged data copy
35:                         (kept in sync with ``docs/uc_schema.json``) so it works from a
36:                         real, non-editable install.
37: specmgr://uc/example -- A complete, valid sample use case document as raw markdown.
38: specmgr://uc/template -- A use-case template (every field present, placeholder text)
39:                           as raw markdown.
40: specmgr://tsk/schema -- The generated TSK JSON Schema, read from a packaged data copy
41:                         (kept in sync with ``docs/tsk_schema.json``) so it works from a
42:                         real, non-editable install.
43: specmgr://tsk/example -- A complete, valid sample task list document as raw markdown.
44: specmgr://tsk/template -- A task list template (every field present, placeholder text)
45:                           as raw markdown.
46: specmgr://qa/schema --  The generated QA JSON Schema, read from a packaged data copy
47:                         (kept in sync with ``docs/qa_schema.json``) so it works from a
48:                         real, non-editable install.
49: specmgr://qa/example -- A complete, valid sample question-and-answer document as raw
50:                         markdown.
51: specmgr://qa/template -- A question-and-answer template (every field present,
52:                           placeholder text) as raw markdown.
53: specmgr://prb/schema -- The generated PRB JSON Schema, read from a packaged data copy
54:                          (kept in sync with ``docs/prb_schema.json``) so it works from a
55:                          real, non-editable install.
56: specmgr://prb/example -- A complete, valid sample problem statement document as raw
57:                          markdown.
58: specmgr://prb/template -- A problem statement template (every field present,
59:                            placeholder text) as raw markdown.
60: specmgr://gol/schema -- The generated GOL JSON Schema, read from a packaged data copy
61:                          (kept in sync with ``docs/gol_schema.json``) so it works from a
62:                          real, non-editable install.
63: specmgr://gol/example -- A complete, valid sample goal document as raw markdown.
64: specmgr://gol/template -- A goal template (every field present,
65:                            placeholder text) as raw markdown.
66: specmgr://rsk/schema -- The generated RSK JSON Schema, read from a packaged data copy
67:                         (kept in sync with ``docs/rsk_schema.json``) so it works from a
68:                         real, non-editable install.
69: specmgr://rsk/example -- A complete, valid sample risk document as raw markdown.
70: specmgr://rsk/template -- A risk template (every field present, placeholder text)
71:                            as raw markdown.
72: specmgr://rsk/tara --     The TARA risk-response framework: what TARA is (Transfer,
73:                            Accept, Reduce, Avoid), the four valid `## Strategy` words,
74:                            and when and how to apply each -- raw markdown domain-knowledge
75:                            guidance.
76: specmgr://rsk/risk-matrix -- The 5x5 risk matrix: probability/impact scale anchors, the
77:                            zone table, and the product thresholds (what 'high risk' and
78:                            'low risk' mean) -- raw markdown domain-knowledge guidance.
79: specmgr://iso25010 --   The ISO/IEC 25010:2023 product quality model's nine main
80:                         characteristics (and sub-characteristics), each with a description.
81: 
82: REQ has no ``specmgr://req/{id}`` resource, unlike ADR -- id-based reads go
83: through the ``get_req`` tool only (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).
84: UC has no ``specmgr://uc/{id}`` resource either, for the same reason -- id-based
85: reads go through the ``get_uc`` tool only. TSK has no ``specmgr://tsk/{id}``
86: resource either -- id-based reads go through the ``get_tsk`` tool only, and
87: there never was such a resource to remove in the first place. QA has no
88: ``specmgr://qa/{id}`` resource either, for the same reason -- id-based reads go
89: through the ``get_qa`` tool only. PRB has no ``specmgr://prb/{id}`` resource
90: either, for the same reason -- id-based reads go through the ``get_prb`` tool
91: only, and there is also no ``specmgr://prb/list`` resource -- ``list_prb``
92: ships as a paged tool from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).
93: GOL has no ``specmgr://gol/{id}`` resource either, for the same reason --
94: id-based reads go through the ``get_gol`` tool only, and there is also no
95:  ``specmgr://gol/list`` resource -- ``list_gol`` ships as a paged tool from
96:  day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13). RSK has no
97:  ``specmgr://rsk/{id}`` resource either, for the same reason -- id-based reads go
98:  through the ``get_rsk`` tool only, and there never was such a resource to
99:  remove in the first place.
100: 
101: Tools
102: -----
103: ADR tools (``adr/tools/``): ``get_adr``, ``list_adr``, ``create_adr``, ``update_frontmatter``,
104: ``update_section``, ``set_status``, ``option_list``, ``option_create``,
105: ``option_update``, ``option_read``, ``option_delete``, ``validate_adr``.
106: Use-case tools (``uc/tools/``): ``parse_uc``, ``get_uc``, ``list_uc``, ``get_uc_example``,
107: ``get_uc_template``, ``create_uc``, ``update_uc``, ``set_status_uc``, ``delete_uc``
108: (stub, not yet implemented), ``validate_uc``.
109: Requirement tools (``req/tools/``): ``parse_req``, ``get_req``, ``list_req``, ``get_req_example``,
110: ``get_req_template``, ``create_req``, ``update_req``, ``set_status_req``, ``delete_req``
111: (stub, not yet implemented), ``validate_req``.
112: Task list tools (``tsk/tools/``): ``parse_tsk``, ``get_tsk``, ``list_tsk``, ``get_tsk_example``,
113: ``get_tsk_template``, ``create_tsk``, ``update_tsk``, ``set_status_tsk``, ``delete_tsk``
114: (stub, not yet implemented), ``validate_tsk``.
115: QA tools (``qa/tools/``): ``parse_qa``, ``get_qa``, ``list_qa``, ``get_qa_example``,
116: ``get_qa_template``, ``create_qa``, ``update_qa``, ``set_status_qa``, ``delete_qa``
117: (stub, not yet implemented), ``validate_qa``.
118: Problem statement tools (``prb/tools/``): ``parse_prb``, ``get_prb``, ``list_prb``,
119: ``get_prb_example``, ``get_prb_template``, ``create_prb``, ``update_prb``,
120: ``set_status_prb``, ``delete_prb`` (stub, not yet implemented), ``validate_prb``.
121: Goal tools (``gol/tools/``): ``parse_gol``, ``get_gol``, ``list_gol``,
122: ``get_gol_example``, ``get_gol_template``, ``create_gol``, ``update_gol``,
123:  ``set_status_gol``, ``delete_gol`` (stub, not yet implemented), ``validate_gol``.
124:  Risk tools (``rsk/tools/``): ``parse_rsk``, ``get_rsk``, ``list_rsk``, ``get_rsk_example``,
125:  ``get_rsk_template``, ``create_rsk``, ``update_rsk``, ``set_status_rsk``, ``delete_rsk``
126:  (stub, not yet implemented), ``validate_rsk``.
127:  General tools (``general/tools/``): ``mdformat`` -- format markdown files in place,
128: preserving YAML frontmatter blocks; ``webfetch`` -- fetch a URL over HTTP GET with a
129: bearer token, restricted to a configured base URL (``SPECMGR_WEBFETCH_BASE_URL``,
130: ``SPECMGR_WEBFETCH_BEARER``).
131: 
132: Prompts
133: -------
134: ADR prompts (``adr/prompts/``): ``create_adr``, ``update_adr`` -- instructional
135: text guiding an LLM through the ADR tool sequence above (``.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md``
136: text guiding an LLM through the ADR tool sequence above (``.specmgr/feat/feat-9-doc-in-specmgr/adr-tool-plan.md``
137: §11).
138: Requirement prompts (``req/prompts/``): ``create_req``, ``update_req`` --
139: instructional text guiding an LLM through the REQ tool sequence above (Task 3.19).
140: Task list prompts (``tsk/prompts/``): ``create_task``, ``update_task`` -- instructional
141: text guiding an LLM through the TSK tool sequence above, plus ``implement_task`` --
142: reads an existing task list via ``get_tsk``, builds a ``TodoWrite`` list from its
143: items, and uses the ``question`` tool to resolve ambiguity before proceeding.
144: QA prompts (``qa/prompts/``): ``create_qa``, ``update_qa``, plus ``refine`` --
145: appends a fresh batch of unanswered interview questions (each with an empty
146: `_(awaiting response)_` placeholder) to an existing QA document, for
147: ``Elicitation Context`` or one or more of the nine ISO/IEC 25010:2023 quality
148: characteristics.
149: Problem statement prompts (``prb/prompts/``): ``create_prb``, ``update_prb`` --
150: instructional text guiding an LLM through a ``TodoWrite`` + ``question``-tool-
151: driven 5W2H interview flow, including agent-synthesized ``Summary``/``Gap``
152: text.
153: Goal prompts (``gol/prompts/``): ``create_gol``, ``update_gol`` --
154: instructional text guiding an LLM through a ``TodoWrite`` +
155: ``question``-tool-driven interview flow over the goal's mandatory
156: ``statement``/``Source`` fields and its optional sections.
157: Risk prompts (``rsk/prompts/``): ``create_risk``, ``update_risk`` -- instructional
158: text guiding an LLM through the RSK tool sequence above.
159: General prompts (``general/prompts/``): ``compact_history`` -- guides rotating
160: older ``### Recent Updates`` entries out of any `.specmgr` feature folder's
161: ``README.md`` into an optional sibling ``history.md``, per ADR
162: e369ee2e-3353-4f92-991c-6367d76d832e.
163: 
164: Modules are grouped domain-first
165: (ADR ece4554b-725c-4f76-bc04-5d2b760363d2: "Organize the codebase by
166: document-type domain"): each document
167: domain (``adr``, ``uc``, ``req``, ``tsk``, ``qa``, ``prb``, ``gol``, ``rsk``, and later ``ac``) is a
168: top-level package with its own ``tools``/``prompts``/``resources`` sub-packages,
169: self-registered via the domain package's own ``__init__.py``. Cross-cutting, non-domain-specific
170: tools/resources/prompts (e.g. ``specmgr://version``/``specmgr://iso25010`` resources,
171: the ``mdformat`` tool, or the ``compact_history`` prompt) stay under the top-level
172: ``general`` package instead (``general.tools``/``general.resources``/``general.prompts``).
173: Add a new domain by
174: creating its top-level package and importing it at the bottom of this
175: module, next to the existing ``adr``/``general``/``gol``/``prb``/``qa``/``req``/``rsk``/``tsk``/``uc``
176: imports, so its ``@mcp.tool()`` / ``@mcp.prompt()`` / ``@mcp.resource()``
177: decorators actually run. ``req``, ``tsk``, ``qa``, ``prb``, ``gol``, and ``rsk`` each
178: register ``tools``, ``resources``, and ``prompts``; ``general`` now also
179: registers all three; ``uc`` registers ``tools`` and ``resources`` only -- it
180: has no ``prompts`` sub-package yet.
181: """
182: 
183: from __future__ import annotations
184: 
185: from collections.abc import AsyncGenerator
186: from contextlib import asynccontextmanager
187: 
188: from mcp.server import MCPServer
189: 
190: 
191: @asynccontextmanager
192: async def _lifespan(_server: MCPServer) -> AsyncGenerator[None, None]:
193:     """Placeholder lifespan: no shared state to initialise yet."""
194:     yield
195: 
196: 
197: mcp = MCPServer(
198:     name="specmgr",
199:     instructions="An artifact manager for system specifications.",
200:     lifespan=_lifespan,
201: )
202: 
203: # ---------------------------------------------------------------------------
204: # Resource/tool/prompt registration (side-effect: registers everything on
205: # mcp). Every domain package here (including the cross-cutting `general`
206: # package, which in turn imports its own `resources`/`tools` sub-packages)
207: # must be imported for its @mcp.tool()/@mcp.prompt()/@mcp.resource()
208: # decorators to actually run.
209: # ---------------------------------------------------------------------------
210: 
211: from . import adr, general, gol, prb, qa, req, rsk, tsk, uc  # noqa: E402, F401

(End of file - total 211 lines)
</content>
```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 24.6s)

_Thinking:_

Next, let's check the prompts that reference the update tool, and check for circular import risks: `general/tools/update.py` will need to import the per-domain write/lock/io helpers. Do the per-domain tools import anything from `general.tools`? Let me check what the domain tools are importing from general: `general/models/summary.py` and `general/models/paged_result.py` (models, not tools). So if `general/tools/update.py` imports `req/tools/_io.py`, `req/tools/_write.py`, `req/tools/_lock.py`, `req/tools/_paths.py`, and `req/models/v1` — the import chain is: `general.tools.update` → `req.tools._io` → (package init `req/tools/__init__.py`) → `req.tools.create_req` → … Does any of the req.tools modules import `general.tools`? Let me grep for it.

Also, each domain has its own `_lock.py` (req_lock, etc.). And each domain's `_paths.py` has `req_base_dir`, `find_req_path`, and `ReqNotFoundError`.

So, to check the shape of the other 6 update tools and their per-domain helpers, let me grep for `from ...general` and `from ..general` inside the domain packages, and read rsk/tools/update_rsk.py and one of the per-domain `_paths.py` (req/tools/\_paths.py). Also check the prompts (req/prompts/update_req.py, etc.) to see what tool names are referenced, and take a look at the tests directory too.

**Tool: grep**

**Input:**

```json
{
  "pattern": "from \\.\\.\\.general|from \\.\\.general|general\\.tools|general import",
  "include": "*.py",
  "path": "src/biz/dfch/specmgr"
}
```

**Output:**

```
Found 100 matches (more matches available)
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/tools/get_qa_example.py:
  Line 30: from ...general.tools._packaged_data import read_packaged_text


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/tools/create_qa.py:
  Line 41: from ...general.tools._doc_paths import slugify


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/tools/get_qa_template.py:
  Line 31: from ...general.tools._packaged_data import read_packaged_text


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/tools/_paths.py:
  Line 20: A thin, QA-specific layer over the generic ``general.tools._doc_paths``

  Line 39: from ...general.tools._doc_paths import (

  Line 57: #: The doc-type subdirectory name passed to ``general.tools._doc_paths``

  Line 65:     A separate class from ``general.tools._doc_paths.DocNotFoundError``, not

  Line 76:     Thin wrapper over ``general.tools._doc_paths.doc_base_dir(QA_TYPE_NAME)``


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/tools/list_qa.py:
  Line 36: from ...general.models import PagedResult

  Line 37: from ...general.tools._paging import normalize_paging, paginate

  Line 73:         ``general.tools._paging.DEFAULT_MAX_RESULTS`` when not given (``None``);

  Line 75:         :func:`~biz.dfch.specmgr.general.tools._paging.normalize_paging`).


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/tools/_lock.py:
  Line 28: Not generalized into ``general.tools`` alongside ``_doc_paths.py`` -- the id


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/prompts/refine.py:
  Line 42: ``general.tools._packaged_data.read_packaged_text`` -- the same

  Line 57: from ...general.tools._packaged_data import read_packaged_text


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/server.py:
  Line 172: ``general`` package instead (``general.tools``/``general.resources``/``general.prompts``).


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/prompts/create_qa.py:
  Line 41: ``general.tools._packaged_data.read_packaged_text``, rather than as an

  Line 53: from ...general.tools._packaged_data import read_packaged_text


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/tools/_lock.py:
  Line 27: Not generalized into ``general.tools`` alongside ``_doc_paths.py`` -- the id


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/prompts/update_qa.py:
  Line 37: ``general.tools._packaged_data.read_packaged_text``, rather than as an

  Line 49: from ...general.tools._packaged_data import read_packaged_text


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/resources/qa_example.py:
  Line 25: tool import the shared, doc-type-agnostic ``general.tools._packaged_data``

  Line 35: from ...general.tools._packaged_data import read_packaged_text


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/tools/list_gol.py:
  Line 34: from ...general.models import PagedResult

  Line 35: from ...general.tools._paging import normalize_paging, paginate

  Line 70:         ``general.tools._paging.DEFAULT_MAX_RESULTS`` when not given (``None``);

  Line 72:         :func:`~biz.dfch.specmgr.general.tools._paging.normalize_paging`).


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/resources/qa_template.py:
  Line 25: tool import the shared, doc-type-agnostic ``general.tools._packaged_data``

  Line 35: from ...general.tools._packaged_data import read_packaged_text


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/tools/_paths.py:
  Line 20: A thin, goal-specific layer over the generic ``general.tools._doc_paths``

  Line 39: from ...general.tools._doc_paths import (

  Line 57: #: The doc-type subdirectory name passed to ``general.tools._doc_paths``

  Line 65:     A separate class from ``general.tools._doc_paths.DocNotFoundError``, not

  Line 75:     Thin wrapper over ``general.tools._doc_paths.doc_base_dir(GOL_TYPE_NAME)``


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/tools/get_gol_example.py:
  Line 30: from ...general.tools._packaged_data import read_packaged_text


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/tools/get_prb_example.py:
  Line 30: from ...general.tools._packaged_data import read_packaged_text


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/resources/qa_schema.py:
  Line 21: (``qa/data/qa_schema.json``, via ``general.tools._packaged_data.read_packaged_text``)

  Line 46: from ...general.tools._packaged_data import read_packaged_text


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/tools/create_gol.py:
  Line 38: from ...general.tools._doc_paths import slugify


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/tools/get_gol_template.py:
  Line 31: from ...general.tools._packaged_data import read_packaged_text


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/prompts/create_gol.py:
  Line 48: ``general.tools._packaged_data.read_packaged_text``, rather than as an

  Line 60: from ...general.tools._packaged_data import read_packaged_text


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/prompts/update_gol.py:
  Line 49: ``general.tools._packaged_data.read_packaged_text``, rather than as an

  Line 61: from ...general.tools._packaged_data import read_packaged_text


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/tools/_paths.py:
  Line 21: ``general.tools._doc_paths`` module, rather than a second hand-written copy

  Line 39: from ...general.tools._doc_paths import (

  Line 57: #: The doc-type subdirectory name passed to ``general.tools._doc_paths``

  Line 65:     A separate class from ``general.tools._doc_paths.DocNotFoundError``, not

  Line 76:     Thin wrapper over ``general.tools._doc_paths.doc_base_dir(PRB_TYPE_NAME)``


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/tools/_lock.py:
  Line 27: Not generalized into ``general.tools`` alongside ``_doc_paths.py`` -- the id


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/tools/create_prb.py:
  Line 38: from ...general.tools._doc_paths import slugify


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/resources/gol_template.py:
  Line 26: ``general.tools._packaged_data`` helper directly, so neither sub-package

  Line 36: from ...general.tools._packaged_data import read_packaged_text


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/_paging.py:
  Line 20: Mirrors ``general.tools._doc_paths``'s shape: a single module shared across


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/__init__.py:
  Line 25:     from biz.dfch.specmgr.general import tools  # noqa: F401 (side-effects only)


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/tools/get_prb_template.py:
  Line 31: from ...general.tools._packaged_data import read_packaged_text


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/resources/gol_schema.py:
  Line 21: (``gol/data/gol_schema.json``, via ``general.tools._packaged_data.read_packaged_text``)

  Line 23: from an editable/source checkout (``general.tools._doc_paths``'s own

  Line 47: from ...general.tools._packaged_data import read_packaged_text


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/tools/list_adr.py:
  Line 34: from ...general.models import PagedResult

  Line 35: from ...general.tools._paging import normalize_paging, paginate

  Line 69:         ``general.tools._paging.DEFAULT_MAX_RESULTS`` when not given (``None``);

  Line 71:         :func:`~biz.dfch.specmgr.general.tools._paging.normalize_paging`).


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/tools/list_prb.py:
  Line 34: from ...general.models import PagedResult

  Line 35: from ...general.tools._paging import normalize_paging, paginate

  Line 71:         ``general.tools._paging.DEFAULT_MAX_RESULTS`` when not given (``None``);

  Line 73:         :func:`~biz.dfch.specmgr.general.tools._paging.normalize_paging`).


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/resources/gol_example.py:
  Line 25: tool import the shared, doc-type-agnostic ``general.tools._packaged_data``

  Line 35: from ...general.tools._packaged_data import read_packaged_text


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/tools/_packaged_data.py:
  Line 44: mirroring ``general.tools._doc_paths``'s own placement (Task 3.10) -- neither


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/md/_markdown.py:
  Line 88:     MCP tool (`general.tools.mdformat`) and the `mdformat` CLI command


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/models/paged_result.py:
  Line 56:         ``general.tools._paging.normalize_paging``).


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/prompts/__init__.py:
  Line 28:     from biz.dfch.specmgr.general import prompts  # noqa: F401 (side-effects only)


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/prompts/update_adr_test.py:
  Line 35: ``general.tools._packaged_data.read_packaged_text``, rather than as an

  Line 47: from ...general.tools._packaged_data import read_packaged_text


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/prompts/compact_history.py:
  Line 40: every call via ``general.tools._packaged_data.read_packaged_text`` --

  Line 52: from ...general.tools._packaged_data import read_packaged_text


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/prompts/create_adr.py:
  Line 33: ``general.tools._packaged_data.read_packaged_text``, rather than as an

  Line 46: from ...general.tools._packaged_data import read_packaged_text


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/prompts/create_adr_test.py:
  Line 40: ``general.tools._packaged_data.read_packaged_text``, rather than as an

  Line 53: from ...general.tools._packaged_data import read_packaged_text


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/prompts/update_adr.py:
  Line 28: ``general.tools._packaged_data.read_packaged_text``, rather than as an

  Line 40: from ...general.tools._packaged_data import read_packaged_text


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/adr/v1/summary.py:
  Line 26: ``general.models``) transitively imports ``general.tools``, which imports


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/resources/__init__.py:
  Line 29:     from biz.dfch.specmgr.general import resources  # noqa: F401 (side-effects only)


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/resources/iso25010.py:
  Line 22: ``general.tools._packaged_data.read_packaged_text``) and parses it into a


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/resources/prb_example.py:
  Line 25: tool import the shared, doc-type-agnostic ``general.tools._packaged_data``

  Line 35: from ...general.tools._packaged_data import read_packaged_text


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/resources/prb_schema.py:
  Line 21: (``prb/data/prb_schema.json``, via ``general.tools._packaged_data.read_packaged_text``)

  Line 45: from ...general.tools._packaged_data import read_packaged_text


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/models/iso25010.py:
  Line 100:         via `general.tools._packaged_data.read_packaged_text`).


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/prompts/update_prb.py:
  Line 44: ``general.tools._packaged_data.read_packaged_text``, rather than as an

  Line 56: from ...general.tools._packaged_data import read_packaged_text


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/resources/prb_template.py:
  Line 25: tool import the shared, doc-type-agnostic ``general.tools._packaged_data``

  Line 35: from ...general.tools._packaged_data import read_packaged_text


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/prompts/create_prb.py:
  Line 49: ``general.tools._packaged_data.read_packaged_text``, rather than as an

  Line 61: from ...general.tools._packaged_data import read_packaged_text


/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/tools/list_rsk.py:
  Line 40: from ...general.models import PagedResult

  Line 41: from ...general.tools._paging import normalize_paging, paginate

  Line 79:         ``general.tools._paging.DEFAULT_MAX_RESULTS`` when not given (``None``);


(Results truncated. Consider using a more specific path or pattern.)
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/tools/_paths.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/tools/_paths.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """Requirement base directory resolution and id -> path lookup (Task 3.11).
19: 
20: A thin, requirement-specific layer over the generic
21: ``general.tools._doc_paths`` module (Task 3.10), rather than a second
22: hand-written copy of ``adr.tools._paths`` -- the base-directory/id-lookup
23: plumbing is identical in shape, only the parsed document type and its id
24: accessor differ.
25: 
26: Mirrors ``adr.tools._paths``'s read-only/write split: :func:`req_base_dir`
27: never creates the directory (a read-only tool shouldn't have that side
28: effect), only :func:`ensure_req_base_dir` does, for the eventual
29: ``create_req`` tool (Task 3.12). There is deliberately no in-memory id ->
30: path cache either -- every lookup re-scans the base directory and re-parses
31: each file, matching this codebase's "the on-disk file is the sole source of
32: truth" design.
33: """
34: 
35: from __future__ import annotations
36: 
37: from collections.abc import Iterator
38: from pathlib import Path
39: 
40: from ...general.tools._doc_paths import (
41:     DocNotFoundError,
42:     doc_base_dir,
43:     ensure_doc_base_dir,
44:     find_doc_path_by_id,
45:     iter_doc_paths,
46: )
47: from ..models.v1 import ReqDocument, parse_req
48: 
49: __all__ = [
50:     "REQ_TYPE_NAME",
51:     "ReqNotFoundError",
52:     "ensure_req_base_dir",
53:     "find_req_path",
54:     "iter_req_paths",
55:     "req_base_dir",
56: ]
57: 
58: #: The doc-type subdirectory name passed to ``general.tools._doc_paths``
59: #: (``{docs root}/req/``, e.g. ``docs/req``).
60: REQ_TYPE_NAME = "req"
61: 
62: 
63: class ReqNotFoundError(LookupError):
64:     """No requirement file found matching the given id.
65: 
66:     A separate class from ``general.tools._doc_paths.DocNotFoundError``, not
67:     a subclass of it -- the same relationship ``adr.tools._paths.AdrNotFoundError``
68:     has to nothing generic, so callers can keep catching a requirement-specific
69:     exception type without depending on the generic module's own exception.
70:     """
71: 
72: 
73: def req_base_dir() -> Path:
74:     """Return the configured requirement base directory, without creating it.
75: 
76:     Thin wrapper over ``general.tools._doc_paths.doc_base_dir(REQ_TYPE_NAME)``
77:     -- see that function's own docstring for the env var/default it reads.
78: 
79:     Returns
80:     -------
81:     Path
82:         The resolved requirement base directory.
83:     """
84:     result = doc_base_dir(REQ_TYPE_NAME)
85:     return result
86: 
87: 
88: def ensure_req_base_dir() -> Path:
89:     """Return the configured requirement base directory, creating it if missing.
90: 
91:     Only ``create_req`` (Task 3.12) should call this -- every other
92:     tool/resource uses the read-only :func:`req_base_dir` instead.
93: 
94:     Returns
95:     -------
96:     Path
97:         The resolved, now-guaranteed-to-exist requirement base directory.
98:     """
99:     result = ensure_doc_base_dir(REQ_TYPE_NAME)
100:     return result
101: 
102: 
103: def iter_req_paths() -> Iterator[Path]:
104:     """Yield every requirement ``*.md`` file under :func:`req_base_dir`, sorted by name.
105: 
106:     Yields nothing (rather than raising) if the base directory does not exist.
107: 
108:     Returns
109:     -------
110:     Iterator[Path]
111:         An iterator over the matching, sorted paths.
112:     """
113:     result = iter_doc_paths(req_base_dir())
114:     return result
115: 
116: 
117: def _get_req_id(doc: ReqDocument) -> str | None:
118:     """Extract the id from a parsed :class:`ReqDocument` (``find_doc_path_by_id``'s ``get_id_fn``)."""
119:     result = doc.frontmatter.id
120:     return result
121: 
122: 
123: def find_req_path(base_dir: Path, id_: str) -> Path:
124:     """Resolve an ``id`` to its on-disk file path under ``base_dir``.
125: 
126:     Scans every ``*.md`` file under ``base_dir``, parsing each via
127:     :func:`~biz.dfch.specmgr.req.models.v1.parse_req` and comparing
128:     ``frontmatter.id`` against ``id_``. A file that fails to parse
129:     (``AssertionError``/``pydantic.ValidationError``) is silently skipped --
130:     one broken file must not prevent lookup of a different, valid id.
131:     Mirrors ``adr.tools._paths.find_adr_path``'s own skip-on-parse-failure
132:     rule.
133: 
134:     Parameters
135:     ----------
136:     base_dir:
137:         The directory to scan for ``*.md`` files.
138:     id_:
139:         The id to look up.
140: 
141:     Returns
142:     -------
143:     Path
144:         The resolved file path.
145: 
146:     Raises
147:     ------
148:     ReqNotFoundError
149:         If no file's ``frontmatter.id`` matches ``id_``.
150:     """
151:     assert isinstance(base_dir, Path), type(base_dir)
152:     assert isinstance(id_, str), type(id_)
153:     assert id_.strip()
154: 
155:     try:
156:         result = find_doc_path_by_id(base_dir, id_, parse_req, _get_req_id)
157:     except DocNotFoundError as ex:
158:         raise ReqNotFoundError(
159:             f"no requirement found with id {id_!r}. The id must be the bare document UUID, without a domain "
160:             f"prefix (use '<uuid>', not 'req-<uuid>')."
161:         ) from ex
162:     return result

(End of file - total 162 lines)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/prompts/update_req.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/prompts/update_req.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """``@mcp.prompt()``: update_req (Task 3.19).
19: 
20: Returns instructional text -- not itself a tool call -- that guides an LLM
21: through revising an existing Requirement (REQ) document by id, using the
22: existing ``req/tools/`` surface (``get_req``, ``update_req``,
23: ``set_status_req``, ``validate_req``). Unlike an earlier revision of this
24: prompt, step 1 no longer points at a ``specmgr://req/{id}`` resource -- that
25: resource was removed in favor of the ``get_req`` tool (feat-7-various-
26: improvements Task 0.9, ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).
27: 
28: Unlike ``adr.prompts.update_adr``, there is no ``update_frontmatter``/
29: ``option_*`` equivalent here: REQ's lifecycle surface (Task 3.9's design) is
30: deliberately small -- a whole-body replace (``update_req``) plus a single,
31: dedicated status-change path (``set_status_req``) -- so the tool-mapping
32: section below is correspondingly shorter.
33: 
34: The actual instructional text lives in its own packaged data file,
35: ``req/data/req_update_instructions.md``, read fresh on every call via
36: ``general.tools._packaged_data.read_packaged_text``, rather than as an
37: inline Python string constant. Placeholders use ``string.Template``
38: (``$id``/``$instructions``), not ``str.format``, precisely so the
39: instructions file itself is free to use plain, unescaped ``{...}`` braces
40: for markdown headings it narrates to the LLM without those colliding with
41: this module's own substitution.
42: """
43: 
44: from __future__ import annotations
45: 
46: from string import Template
47: 
48: from ...general.tools._packaged_data import read_packaged_text
49: from ...server import mcp
50: 
51: 
52: @mcp.prompt(
53:     name="update_req",
54:     title="Update a requirement",
55:     description=(
56:         "Guides the LLM through revising an existing requirement by id: reading current "
57:         "state, applying the requested change with the right tool, and validating."
58:     ),
59: )
60: def update_req(id: str, instructions: str | None = None) -> str:
61:     """Return instructional text for revising the requirement identified by ``id``.
62: 
63:     Parameters
64:     ----------
65:     id:
66:         The existing document's specmgr-assigned identifier.
67:     instructions:
68:         Free-text description of the requested change. When absent, the
69:         returned instructions tell the LLM to ask the user first rather
70:         than guessing.
71: 
72:     Returns
73:     -------
74:     str
75:         Instructional text (auto-wrapped as a single ``UserMessage`` by
76:         the MCP SDK), not itself a tool call.
77:     """
78:     template = Template(read_packaged_text("req", "update_instructions", "md"))
79:     return template.substitute(
80:         id=id,
81:         instructions=instructions or "(not given -- ask the user before making any change)",
82:     )

(End of file - total 82 lines)
</content>
```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 74.7s)

_Thinking:_

Next, I'll check the following:

1. Packaged instruction data files (e.g., `req/data/req_update_instructions.md`) — these reference tool names, so they'll need updating.
2. Tests for update tools.
3. Circular import check: `general/tools/update.py` will import the per-domain `_io`/`_write`/`_lock`/`_paths`/models. Domain tool modules import from `...general.tools._packaged_data`, `...general.tools._doc_paths`, `...general.tools._paging` — all submodules of general.tools. Importing `general.tools.update` triggers `general/tools/__init__.py`, which imports `.mdformat` and `.webfetch` — no circularity with the domains. Then `update.py` imports `req.tools._io` → triggers `req/tools/__init__.py` → imports all of req's tool modules → those import `...server` (mcp), and… wait, does `req/tools/update_req.py` import `from ...server import mcp`? Yes! And server.py imports the domain packages at the end. Circular import risk: `server.py` → `req/__init__.py` → `req.tools` → `req.tools.update_req` → `...server` (mcp). This works today because by the time the domain packages are imported at the end of server.py, the `mcp` object is already defined in server.py (imported modules find `mcp` in the partially-initialized server module — Python handles this. Because `from ...server import mcp` is executed after the `mcp = MCPServer(...)` line has run).

Now, if we add `general/tools/update.py` which imports domain tool submodules: server.py imports `general` (within the import line `from . import adr, general, gol, ...`) — the order in that import line: `adr, general, gol, prb, qa, req, rsk, tsk, uc`. Python imports them left to right: first `adr` → adr's tools import `...server` (partially initialized — no problem, mcp is already defined). Next `general` → `general/tools/__init__.py` → if `update.py` is in there, it imports `req.tools._io` → `req/tools/__init__.py` → … → `req.tools.update_req` → `from ...server import mcp` → server module is partially initialized but `mcp` exists → no problem. Also `req.tools.list_req` → `...general.models` → no problem. And `req.prompts` is imported by `req/__init__.py` — wait, does req/__init__.py import prompts? Let me check. Probably yes.

But there's a subtler issue: `general.tools.update` imports `req.tools` (the package) — when `general` is imported (before `req` in the import line), `req.tools.__init__` gets imported early. This triggers registration of all req tools — earlier than the current order, but registration order shouldn't matter (the mcp tool registry is probably a dict/list, and docs generation might depend on order? The `specmgr mcp-docs` command generates docs/MCP.md — the order might be registration order or sorted order; needs attention but probably fine).

Actually, wait — let me check `models/adr/v1/summary.py` line 26: "transitively imports `general.tools`, which imports …" — this is an existing note about import chains. Let me read this to understand the known circularity issue.

Alternatively, to avoid importing domain *tool* packages, `general/tools/update.py` could import only from domain *model* packages and `general.tools._doc_paths`, and re-implement the small write/lock steps. But the locks are in domain `tools/_lock.py` (e.g., `req_lock`) — the note in `_lock.py`'s docstring says "Not generalized into general.tools … the id …". The lock is a per-domain function that takes an id. The write helpers (`write_req_file`) are in `tools/_write.py`. So the consolidated update tool needs: models (from_text, Frontmatter, Document), write helpers, locks, base_dir, load_by_id (find + read).

Options:

- A: `general/tools/update.py` imports each domain's tools submodule (side-effect import of the entire `req.tools` package — including the `@mcp.tool` registration of the tools we're about to delete; not a problem if done after deletion, but for domains whose tools remain, the package import re-registers… no wait — registration happens when the module is imported, and `server.py` will import the domain packages anyway. Importing `req.tools` from `general.tools.update` during `general`'s import just moves the registration earlier. The `mcp` object must exist — it does (defined before the import line). OK.
- B: Put the consolidated `update` tool in its own new top-level module or in `general/tools/`, and import per-domain *private helpers* directly by module path (e.g., `from ...req.tools._io import load_by_id`). Even `from ...req.tools._io import ...` triggers execution of `req/tools/__init__.py` first (importing a submodule imports the parent package). So same side effect as A.

So either way, the consolidated update module transitively imports all 7 domain tool packages. That's fine — server.py imports them all anyway. Just be careful with import order in server.py's import line: `general` is second (after `adr`). When `general.tools.update` imports `req.tools`, `req.tools.update_req` does `from ...server import mcp` — the server module is mid-import (the `from . import adr, general, ...` line is executing), but the name `mcp` has already been bound in the server module's namespace (lines 197–201 run before line 211). `from ...server import mcp` does getattr on the partially-initialized module — works as long as `mcp` is already bound. It is. This is exactly the same mechanism the domain tools already rely on today (adr.tools.\* also imports `...server`, and `adr` is imported first, so it's proven).

Hmm, wait, actually there's a subtle point: when Python imports `biz.dfch.specmgr.server`, it executes top to bottom. At line 211 `from . import adr, general, ...` — importing the `adr` package runs `adr/__init__.py`, which probably imports `adr.tools`, `adr.prompts`, `adr.resources`. Those modules do `from ...server import mcp` — at that point `biz.dfch.specmgr.server` is in `sys.modules` (partially initialized) and has the `mcp` attribute → works. Then `general` → `general/tools/__init__` → `update.py` → `from ...req.tools._io import load_by_id` → imports the `req` package → `req/__init__.py` → `req.tools` → all tool modules → `from ...server import mcp` → works. Then the import line continues to `gol, prb, qa, req...` — `req` is already in sys.modules (fully initialized) → skipped.

Another consideration: does `req/__init__.py` import `req.prompts`? And `req.prompts.update_req` (the prompt) imports `...general.tools._packaged_data` — by that point `general.tools` is fully initialized… wait, no: `general/__init__.py` might import the subpackages in some order. If `general/__init__.py` imports `general.tools` first, and `general.tools.update` (inside `general/tools/__init__.py`) imports `req` → `req.prompts` → `from ...general.tools._packaged_data import read_packaged_text` — at that point the `general.tools` package is partially initialized (its `__init__` is executing `from .update import update`… hmm, depends on the order within `__init__`). If `general/tools/__init__.py` is like:

```
from .mdformat import mdformat
from .webfetch import webfetch
from .update import update  # new
```

Then during the execution of `from .update import update`, the `general.tools` module object exists in sys.modules with only the attributes bound up to that point (mdformat, webfetch, and the private modules that were imported earlier? no — `_packaged_data` hasn't been imported yet unless mdformat/webfetch imported it). `req.prompts.update_req` does `from ...general.tools._packaged_data import read_packaged_text` — this imports the *submodule* `general.tools._packaged_data` directly. Python's import system handles this: it finds the parent `general.tools` (in sys.modules, partial), then imports the `general.tools._packaged_data` submodule fresh — works even during partial initialization, because `from package.submodule import name` triggers a full import of `package.submodule` if it's not yet in sys.modules. The only thing that fails is `from general.tools import _packaged_data` (attribute access on a partial module) — but the code uses `from ...general.tools._packaged_data import read_packaged_text`, i.e., submodule import form → safe.

To be safe, let me check `general/__init__.py` and `req/__init__.py`.

Also, the existing note at `models/adr/v1/summary.py` line 26 — let me read it. It says something about a chain where general.models imports general.tools… actually, it says "(`general.models`) transitively imports `general.tools`, which imports …". Let me read that docstring for known pitfalls.

After that, I'll check the tests: ls tests/ to see the structure of the update tests.

Also, I'll check the `data/` instruction files that reference the tool names — glob for `*_update_instructions.md`.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/__init__.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/__init__.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """General-purpose (cross-cutting, not domain-specific) tools, resources, and
19: prompts.
20: 
21: This package provides tools, resources, and prompts that apply to any markdown
22: file in the system, regardless of document type (ADR, use case, etc.), or that
23: are not specific to any single document domain at all (e.g. the server
24: version). It complements the domain-specific packages (``adr``, ``req``,
25: ``uc``).
26: 
27: ``tools`` (e.g. ``mdformat``, ``webfetch``) operate on raw markdown files or
28: external URLs and are registered as ``@mcp.tool()`` functions. ``resources``
29: (e.g. ``version``, ``iso25010``) are registered as ``@mcp.resource()``
30: functions. ``prompts`` (e.g. ``compact_history``) return instructional text
31: and are registered as ``@mcp.prompt()`` functions. Import this package to
32: register all general tools, resources, and prompts against the shared ``mcp``
33: application instance at once::
34: 
35:     from biz.dfch.specmgr import general  # noqa: F401 (side-effects only)
36: """
37: 
38: from . import prompts, resources, tools  # noqa: F401
39: 
40: __all__ = [
41:     "prompts",
42:     "resources",
43:     "tools",
44: ]

(End of file - total 44 lines)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/__init__.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/__init__.py</path>
<type>file</type>
<content>
1: """Requirement (REQ) domain -- requirement specifications.
2: 
3: This is a domain-first package containing models, tools, prompts, and resources
4: for managing requirement documents.
5: 
6: Import this package to register all requirement tools/prompts/resources against
7: the shared ``mcp`` application instance at once::
8: 
9:     from biz.dfch.specmgr import req  # noqa: F401 (side-effects only)
10: 
11: ``tools`` (``parse_req``, ``get_req``, ``list_req``, ``get_req_example``,
12: ``get_req_template``, ``create_req``, ``update_req``, ``set_status_req``,
13: ``delete_req``, ``validate_req``), ``resources`` (``specmgr://req/schema``,
14: ``specmgr://req/example``, ``specmgr://req/template``), and ``prompts``
15: (``create_req``, ``update_req``) all exist. Unlike ADR, REQ has no
16: ``specmgr://req/{id}`` resource -- id-based reads go through the ``get_req``
17: tool only (ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). Likewise, the former
18: ``specmgr://req/list`` resource was replaced by the ``list_req`` tool, so
19: that paging parameters could be accepted (feat-13-list-paging).
20: """
21: 
22: from . import prompts, resources, tools  # noqa: F401
23: 
24: __all__ = [
25:     "prompts",
26:     "resources",
27:     "tools",
28: ]

(End of file - total 28 lines)
</content>
```

**Tool: glob**

**Input:**

```json
{
  "pattern": "src/biz/dfch/specmgr/**/data/*.md"
}
```

**Output:**

```
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/data/qa_create_instructions.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/data/qa_template.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/data/qa_update_instructions.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/data/qa_example.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/qa/data/qa_refine_instructions.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/data/adr_create_test_instructions.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/data/adr_create_instructions.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/data/adr_update_test_instructions.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/data/adr_update_instructions.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/data/general_compact_history_instructions.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/general/data/general_iso25010.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/data/tsk_template.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/data/tsk_update_instructions.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/data/tsk_create_instructions.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/data/tsk_example.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/tsk/data/tsk_implement_instructions.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/data/rsk_risk_matrix.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/data/rsk_create_instructions.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/data/rsk_template.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/data/rsk_example.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/data/rsk_tara.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/rsk/data/rsk_update_instructions.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/data/prb_template.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/data/prb_create_instructions.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/data/prb_update_instructions.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/prb/data/prb_example.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/data/gol_example.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/data/gol_create_instructions.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/data/gol_template.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/gol/data/gol_update_instructions.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/uc/data/uc_template.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/uc/data/uc_example.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/data/req_template.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/data/req_example.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/data/req_create_instructions.md
/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/data/req_update_instructions.md
```

**Tool: bash**

**Input:**

```json
{
  "command": "ls tests/ && ls tests/ 2>/dev/null | head -5; find tests -name \"*update*\" -type d -o -name \"*update*\" -type f | sort"
}
```

**Output:**

```
__init__.py
__pycache__
adr
commands
feat-5-md-model-parser
feat-6-requirement-artifact
fixtures
general
gol
models
prb
qa
req
resources
rsk
test_cli.py
test_package.py
test_paths.py
tsk
uc
__init__.py
__pycache__
adr
commands
feat-5-md-model-parser
tests/adr/prompts/__pycache__/test_update_adr.cpython-313.pyc
tests/adr/prompts/__pycache__/test_update_adr_test.cpython-313.pyc
tests/adr/prompts/test_update_adr.py
tests/adr/prompts/test_update_adr_test.py
tests/adr/tools/__pycache__/test_option_update.cpython-313.pyc
tests/adr/tools/__pycache__/test_update_frontmatter.cpython-313.pyc
tests/adr/tools/__pycache__/test_update_section.cpython-313.pyc
tests/adr/tools/test_option_update.py
tests/adr/tools/test_update_frontmatter.py
tests/adr/tools/test_update_section.py
tests/gol/prompts/__pycache__/test_update_gol.cpython-313.pyc
tests/gol/prompts/test_update_gol.py
tests/gol/tools/__pycache__/test_update_gol.cpython-313.pyc
tests/gol/tools/test_update_gol.py
tests/prb/prompts/__pycache__/test_update_prb.cpython-313.pyc
tests/prb/prompts/test_update_prb.py
tests/prb/tools/__pycache__/test_update_prb.cpython-313.pyc
tests/prb/tools/test_update_prb.py
tests/qa/prompts/__pycache__/test_update_qa.cpython-313.pyc
tests/qa/prompts/test_update_qa.py
tests/qa/tools/__pycache__/test_update_qa.cpython-313.pyc
tests/qa/tools/test_update_qa.py
tests/req/prompts/__pycache__/test_update_req.cpython-313.pyc
tests/req/prompts/test_update_req.py
tests/req/tools/__pycache__/test_update_req.cpython-313.pyc
tests/req/tools/test_update_req.py
tests/rsk/prompts/__pycache__/test_update_risk.cpython-313.pyc
tests/rsk/prompts/test_update_risk.py
tests/rsk/tools/__pycache__/test_update_rsk.cpython-313.pyc
tests/rsk/tools/test_update_rsk.py
tests/tsk/prompts/__pycache__/test_update_task.cpython-313.pyc
tests/tsk/prompts/test_update_task.py
tests/tsk/tools/__pycache__/test_update_tsk.cpython-313.pyc
tests/tsk/tools/test_update_tsk.py
tests/uc/tools/__pycache__/test_update_uc.cpython-313.pyc
tests/uc/tools/test_update_uc.py

```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 22.9s)

_Thinking:_

Now I have a good grasp of the overall picture. Let me check a few more details:

1. Check the data instruction file (req_update_instructions.md) and look at the tool references that need to be updated.
2. Check how the per-domain `validate_*` / `create_*` differ — the unified update needs per-domain dispatch: content validation (domain-specific `X.from_text`), frontmatter reconstruction, write helper.
3. Check `_lock.py` (req) — the lock function is per-domain.
4. Check the feature folder conventions — new features use `.specmgr/feat/feat-NNN-slug/README.md` from a template. What is the latest feat number? ls .specmgr/feat/.
5. Check the tests for update tools to get a sense of scale (one test file).

Let me batch the reads together and run them.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/data/req_update_instructions.md"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/data/req_update_instructions.md</path>
<type>file</type>
<content>
1: You are revising an existing Requirement (REQ) document, id: $id
2: 
3: Requested change: $instructions
4: 
5: Follow this sequence exactly. Do not write raw markdown yourself beyond
6: the body content you pass to `update_req` -- every change to the
7: document goes through the specmgr MCP tools listed below.
8: 
9: ## 1. Read current state first
10: Call `get_req(id)` to load the document's current frontmatter and body.
11: Never assume prior state -- the on-disk file is always the source of
12: truth and may have been hand-edited since you last saw it.
13: 
14: ## 2. If no change was specified
15: If "Requested change" above says "(not given)", ask the user what they
16: want to change before calling any write tool.
17: 
18: ## 3. Map the requested change to the right tool
19: - A change to the body -- the requirement statement, `description`,
20:   `characteristics`, `level`, `priority`, `tags`, `source`,
21:   `related_artifacts`, `more_information`, or `notes` -- ->
22:   `update_req(id, content)`. `content` is body markdown only (no
23:   frontmatter block) and is a **whole-body replace**: read the current
24:   body first (step 1) and carry forward every section you are not
25:   intentionally changing, or it will be dropped. `id`/`type`/`status`/
26:   `created`/`version` are preserved automatically regardless of what you
27:   submit; only `updated` changes.
28: - A change to `status` -> `set_status_req(id, status)` instead --
29:   `update_req` never accepts or changes `status`. `status` must be one
30:   of: draft, proposed, accepted, superseded, deprecated, rejected,
31:   implemented.
32: 
33: ## 4. Check the schema, and validate before writing if useful
34: Fetch `specmgr://req/schema` to confirm field names and constraints
35: before drafting the replacement body. Optionally call
36: `validate_req(content, full=False)` beforehand to dry-run the new body
37: without writing anything -- `update_req` already performs the same
38: validation internally, so this step is never required, only a
39: convenience.

(End of file - total 39 lines)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/tools/_lock.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/tools/_lock.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """Per-document in-process lock guarding requirement mutations.
19: 
20: Ported from ``adr.tools._lock.adr_lock`` unchanged except for naming -- see
21: that module's own docstring for the full rationale (the read-modify-write
22: race a mutating tool's ``load_by_id`` -> mutate -> write sequence is exposed
23: to when an MCP host dispatches two overlapping calls against the same id).
24: ``update_req`` (Task 3.13) and any future requirement mutation tool
25: (``set_status_req``, Task 3.14) wrap their whole sequence in
26: ``with req_lock(id):``.
27: 
28: Not generalized into ``general.tools`` alongside ``_doc_paths.py`` (Task
29: 3.10) -- the id -> path lookup plumbing was generalized because it was
30: already shared, read-only, dependency-light code; a lock, by contrast, is a
31: mutation-time correctness primitive that was never part of Task 3.9's
32: recorded design discussion. Kept as its own small, REQ-specific module for
33: now, mirroring ADR's own non-generalized precedent; migrating both onto one
34: shared module remains optional future cleanup.
35: """
36: 
37: from __future__ import annotations
38: 
39: import threading
40: from collections.abc import Iterator
41: from contextlib import contextmanager
42: 
43: __all__ = ["req_lock"]
44: 
45: #: Guards creation of/lookup into `_locks` -- held only for the instant it
46: #: takes to get-or-create a per-id lock, never for the duration of a
47: #: mutation itself.
48: _registry_lock = threading.Lock()
49: 
50: #: One lock per requirement id, created lazily on first use and never
51: #: removed -- the id space is small and long-lived relative to a server
52: #: process's lifetime, so there is no meaningful growth/cleanup concern here.
53: _locks: dict[str, threading.Lock] = {}
54: 
55: 
56: def _lock_for(id_: str) -> threading.Lock:
57:     """Return the (lazily created) lock instance for ``id_``."""
58:     with _registry_lock:
59:         lock = _locks.get(id_)
60:         if lock is None:
61:             lock = threading.Lock()
62:             _locks[id_] = lock
63:         return lock
64: 
65: 
66: @contextmanager
67: def req_lock(id_: str) -> Iterator[None]:
68:     """Serialize the read-modify-write mutation sequence for requirement ``id_``.
69: 
70:     Every mutating tool wraps its whole ``load_by_id`` -> mutate -> write
71:     sequence in ``with req_lock(id):`` so two concurrent calls targeting the
72:     same id run one after another instead of interleaving, preventing the
73:     lost-update race described in this module's docstring.
74:     """
75:     lock = _lock_for(id_)
76:     with lock:
77:         yield

(End of file - total 77 lines)
</content>
```

**Tool: bash**

**Input:**

```json
{
  "command": "ls .specmgr/feat/ && ls .specmgr/"
}
```

**Output:**

```
feat-10-add-artifact-type-tasklist
feat-12-qa-artifact
feat-13-list-paging
feat-14-qa-v2-adjacent-qa
feat-15-add-artifact-type-risk
feat-16-problem-statement
feat-18-goal
feat-4-use-cases
feat-5-md-model-parser
feat-6-requirement-artifact
feat-7-various-improvements
feat-8-coverage-badge
feat-9-doc-in-specmgr
_template
conventions.md
feat

```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 25.5s)

_Thinking:_

Now I've got a pretty complete picture of the whole thing. A few more things I should check quickly:

1. Scale of the update tool's tests (e.g., test_update_req.py) — to estimate the amount of test work.
2. Check how `create_*` tools and `validate_*` tools differ per domain — the unified `update` needs per-domain dispatch for: (a) content validation via `X.from_text(format_text(content))`, (b) reconstructing the frontmatter, (c) the write helper `write_X_file`. All of these exist per domain.

Also worth noting: each domain's `set_status_*` tools use the same `load_by_id` + lock + write pattern. And the `update_*` tools are identical except for the model types.

Let me quickly check the test file sizes, and for example take a look at the imports in rsk's update to confirm the shape is identical. I might also check `commands/mcp_docs.py` to understand the order in which the docs/MCP.md generation happens (tool order in the docs).

Actually, let me quickly estimate the test file sizes and count the number of update tests.

**Tool: bash**

**Input:**

```json
{
  "command": "wc -l tests/req/tools/test_update_req.py tests/rsk/tools/test_update_rsk.py tests/uc/tools/test_update_uc.py src/biz/dfch/specmgr/rsk/tools/update_rsk.py src/biz/dfch/specmgr/uc/tools/update_uc.py src/biz/dfch/specmgr/gol/tools/update_gol.py && grep -rn \"update_req\\|update_uc\\|update_tsk\\|update_qa\\|update_prb\\|update_gol\\|update_rsk\" src/biz/dfch/specmgr --include=\"*.py\" -l | sort"
}
```

**Output:**

```
  164 tests/req/tools/test_update_req.py
  200 tests/rsk/tools/test_update_rsk.py
  199 tests/uc/tools/test_update_uc.py
   95 src/biz/dfch/specmgr/rsk/tools/update_rsk.py
   95 src/biz/dfch/specmgr/uc/tools/update_uc.py
   95 src/biz/dfch/specmgr/gol/tools/update_gol.py
  848 total
src/biz/dfch/specmgr/gol/__init__.py
src/biz/dfch/specmgr/gol/prompts/__init__.py
src/biz/dfch/specmgr/gol/prompts/update_gol.py
src/biz/dfch/specmgr/gol/tools/__init__.py
src/biz/dfch/specmgr/gol/tools/_io.py
src/biz/dfch/specmgr/gol/tools/_lock.py
src/biz/dfch/specmgr/gol/tools/set_status_gol.py
src/biz/dfch/specmgr/gol/tools/update_gol.py
src/biz/dfch/specmgr/gol/tools/validate_gol.py
src/biz/dfch/specmgr/gol/tools/_write.py
src/biz/dfch/specmgr/prb/__init__.py
src/biz/dfch/specmgr/prb/prompts/__init__.py
src/biz/dfch/specmgr/prb/prompts/update_prb.py
src/biz/dfch/specmgr/prb/tools/__init__.py
src/biz/dfch/specmgr/prb/tools/_io.py
src/biz/dfch/specmgr/prb/tools/_lock.py
src/biz/dfch/specmgr/prb/tools/set_status_prb.py
src/biz/dfch/specmgr/prb/tools/update_prb.py
src/biz/dfch/specmgr/prb/tools/validate_prb.py
src/biz/dfch/specmgr/prb/tools/_write.py
src/biz/dfch/specmgr/qa/__init__.py
src/biz/dfch/specmgr/qa/prompts/__init__.py
src/biz/dfch/specmgr/qa/prompts/refine.py
src/biz/dfch/specmgr/qa/prompts/update_qa.py
src/biz/dfch/specmgr/qa/tools/create_qa.py
src/biz/dfch/specmgr/qa/tools/__init__.py
src/biz/dfch/specmgr/qa/tools/_io.py
src/biz/dfch/specmgr/qa/tools/_lock.py
src/biz/dfch/specmgr/qa/tools/set_status_qa.py
src/biz/dfch/specmgr/qa/tools/update_qa.py
src/biz/dfch/specmgr/qa/tools/validate_qa.py
src/biz/dfch/specmgr/qa/tools/_write.py
src/biz/dfch/specmgr/req/__init__.py
src/biz/dfch/specmgr/req/prompts/__init__.py
src/biz/dfch/specmgr/req/prompts/update_req.py
src/biz/dfch/specmgr/req/tools/create_req.py
src/biz/dfch/specmgr/req/tools/__init__.py
src/biz/dfch/specmgr/req/tools/_io.py
src/biz/dfch/specmgr/req/tools/_lock.py
src/biz/dfch/specmgr/req/tools/set_status_req.py
src/biz/dfch/specmgr/req/tools/update_req.py
src/biz/dfch/specmgr/req/tools/validate_req.py
src/biz/dfch/specmgr/req/tools/_write.py
src/biz/dfch/specmgr/rsk/__init__.py
src/biz/dfch/specmgr/rsk/prompts/update_risk.py
src/biz/dfch/specmgr/rsk/tools/__init__.py
src/biz/dfch/specmgr/rsk/tools/_io.py
src/biz/dfch/specmgr/rsk/tools/_lock.py
src/biz/dfch/specmgr/rsk/tools/set_status_rsk.py
src/biz/dfch/specmgr/rsk/tools/update_rsk.py
src/biz/dfch/specmgr/rsk/tools/validate_rsk.py
src/biz/dfch/specmgr/rsk/tools/_write.py
src/biz/dfch/specmgr/server.py
src/biz/dfch/specmgr/tsk/__init__.py
src/biz/dfch/specmgr/tsk/models/v1/body.py
src/biz/dfch/specmgr/tsk/prompts/update_task.py
src/biz/dfch/specmgr/tsk/tools/__init__.py
src/biz/dfch/specmgr/tsk/tools/_io.py
src/biz/dfch/specmgr/tsk/tools/_lock.py
src/biz/dfch/specmgr/tsk/tools/set_status_tsk.py
src/biz/dfch/specmgr/tsk/tools/update_tsk.py
src/biz/dfch/specmgr/tsk/tools/validate_tsk.py
src/biz/dfch/specmgr/tsk/tools/_write.py
src/biz/dfch/specmgr/uc/__init__.py
src/biz/dfch/specmgr/uc/tools/create_uc.py
src/biz/dfch/specmgr/uc/tools/__init__.py
src/biz/dfch/specmgr/uc/tools/_io.py
src/biz/dfch/specmgr/uc/tools/_lock.py
src/biz/dfch/specmgr/uc/tools/set_status_uc.py
src/biz/dfch/specmgr/uc/tools/update_uc.py
src/biz/dfch/specmgr/uc/tools/validate_uc.py
src/biz/dfch/specmgr/uc/tools/_write.py

```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 270.3s)

_Thinking:_

Now I have the full picture. Let me summarize my analysis and present my view + plan along with some confirmation questions.

**Current state:**

- 7 near-identical full-body update tools: `update_req`, `update_uc`, `update_tsk`, `update_qa`, `update_prb`, `update_gol`, `update_rsk`. Each is 95 lines, with the signature `update_X(id: str, content: str) -> XDocument`, and the logic is: validate the body with the domain's `from_text(format_text(content))`, then under the domain's lock, run `load_by_id`, preserve the frontmatter (updating `updated`), and `write_X_file`.
- ADR is structurally different: `update_frontmatter` (full replacement of frontmatter), `update_section` (per-section replacement/deletion), `option_update`, `set_status`. ADR has no full-body update — by design (MADR's section model, plan §4/§5).
- Per-domain `set_status_*` (7 of them) + a generic `set_status` (ADR) — same consolidation opportunity, but a separate concern.
- Shared infrastructure already exists: `general/tools/_doc_paths.py` (generic base dir + id→path search), and per-domain thin layers `_paths`/`_io`/`_write`/`_lock`.
- Per-domain `update_*` prompts + packaged instruction `.md` files that reference tool names (e.g. `req_update_instructions.md` says "pass to `update_req`", "`update_req(id, content)`").
- Tests: per-domain `tests/<domain>/tools/test_update_<domain>.py` (roughly 164–200 lines each).
- `server.py` docstring is the authoritative list, `docs/MCP.md` is auto-generated.
- Latest feature: feat-18. So this feature will be `feat-19-...` or `feat-0-...` depending on whether there's a GitHub issue.

**My view:**
The idea is good for the 7 full-body domains — those tools are literally the same function with the type substituted in. Consolidating to a single `update` tool:

- Reduces the tool surface from 7 → 1 (and future domains like `ac` won't add another update tool).
- Makes the MCP surface easier for LLM clients: one tool with a `type` enum instead of 7 near-duplicate tools.
- Is consistent with existing patterns (general/tools hosts cross-cutting tools; `set_status` is already ADR-generic… well, actually not, ADR has `set_status` and the others have `set_status_X`).

**The `uuid`-only idea — I'm not a fan.** Reasons:

1. Ids are v4 UUIDs generated independently per domain. Uniqueness is *practical* but not *guaranteed* — if a collision happens, the server has to pick a domain arbitrarily. With `type`, there's no ambiguity by construction.
2. To resolve uuid → domain, the server has to scan all 7 (and growing) domain directories, parsing every file, until a match. This codebase has an explicit "no id cache, the file on disk is the source of truth" design, so that scan cost lands on the *write* path, and grows with every new domain. The error message in `_doc_paths.py` ("The id must be the bare document UUID, without a domain prefix") shows that the no-prefix convention was a deliberate decision — it's fine to keep the id bare, but the *tool* still needs the domain.
3. The LLM client always already knows the domain (it just called `get_rsk`/`create_rsk`/`list_rsk`), so `type` costs nothing cognitively, and makes the call auditable.
4. ADR: even uuid-only can't absorb ADR's update tools, because ADR's update semantics are per-section/full-frontmatter, not full-body. So the "just uuid" tool still needs either a `type` for ADR or to exclude ADR — if we're excluding ADR anyway, there's no benefit to dropping `type` for the rest.

**Scope decision — ADR is out.** The 7 full-body updates get consolidated. ADR keeps `update_frontmatter`/`update_section`/`option_*`/`set_status` (those are a different, deliberate contract — a full-body `update_adr` would bypass the section-level replacement semantics that the MADR plan defines).

**Recommended shape:**

```
update(id: str, type: Literal["req","uc","tsk","qa","prb","gol","rsk"], content: str) -> dict/str
```

Hmm, one design question: the return value. Currently each `update_X` returns a typed `XDocument`. A consolidated tool can't have 7 different return types in one signature — the MCP tool would return the domain model (the SDK serializes via pydantic). The return type annotation could be `object`/`Any`… this codebase's conventions (conventions.md: mandatory type hints) — the cleanest is: return the domain document (annotated as a union `ReqDocument | UcDocument | ... | RskDocument`), or return a smaller uniform result (e.g. the updated document's frontmatter + confirmation). Union type hints work with pydantic, but the MCP SDK's schema generation for a 7-way union of complex models might bloat the tool schema… actually, the return type isn't part of the JSON schema (only the input is), so a union annotation is fine for the MCP schema, and the runtime value serializes as-is.

Alternatively, keep it simple: annotate as `-> object`, or use a union. I'll propose a union type (self-documenting) — or actually, what does the MCP SDK do with the return value? It serializes the result to text (json) for the tool result. A union annotation doesn't affect the schema. Let me suggest the union; the implementer can confirm.

**Dispatch implementation:** A new module `general/tools/update.py` (the cross-cutting home per AGENTS.md), holding a per-domain descriptor table:

```python
_UPDATERS: dict[
    str, callable
]  # or a small dataclass: validate(content)->body, frontmatter class, write helper, lock, base_dir, error type
```

Each entry wires up the existing per-domain private helpers (`load_by_id`, `write_X_file`, `X_lock`, `X.from_text`, `XFrontmatter`). The 7 `update_X` tool modules get deleted; each domain's `tools/__init__.py` drops the import; `set_status_X` and the rest of the domain tools keep using the same private helpers (no change).

**Circular import note:** `general/tools/update.py` imports the `req.tools._io` etc. submodules → triggers each domain's `tools/__init__` → all domain tools re-register `@mcp.tool()` earlier than today (during `general`'s import, which sits before `req`/`rsk`/etc. in server.py's import line). This works today's way (`adr`'s tools already import `...server` while the server module is still partially initialized — the `mcp` name is bound before the import line). The one thing to verify during implementation: the ordering in `general/tools/__init__.py` (if we import `.update` alongside `.mdformat`/`.webfetch`, does any domain's prompt chain import `general.tools._packaged_data` in the `from general.tools import _packaged_data` attribute form? No — every existing usage is the `from ...general.tools._packaged_data import read_packaged_text` submodule form, which is safe even mid-initialization). Worth a test: import `server` fresh in a subprocess.

**Collateral changes:**

- Per-domain `update_X` prompts: the instruction files reference `update_X` tool names (e.g. req_update_instructions.md line 6, lines 22–27). Either (a) keep the per-domain prompts and just update the text to point to `update(id, type, content)`, or (b) consolidate the 7 update prompts into a single `update` prompt as well (the prompts are also near-duplicates: same structure, different schema resource name and status tool name). The user's request is "consolidate all update commands" — commands = tools. But prompts are the same story. My view: consolidating the 7 update prompts into a single generic `update` prompt with a `type` parameter is the natural companion move, and reduces 6 more entries. However, the prompt text differs per domain (which sections exist, which `specmgr://X/schema` resource, the status enum is shared but the tool name is per-domain: `set_status_X`). Hmm, the per-domain instruction files also name-check domain-specific body sections (req names `level`, `priority`, …). A generic update prompt can keep that generic: "read the current body, map the change to a full-body replacement via `update(id, type, content)`, fetch `specmgr://{type}/schema`…". The `specmgr://req/schema`-style resources are uniformly named per type — so the generic text can use `{type}`. This is doable, but the text quality drops a bit. Or keep the prompts per-domain (they're cheap and give domain-tailored guidance). I should ask the user's preference here. My recommendation: tools consolidated now; keep the prompts per-domain but update the text (smaller change, keeps domain-specific guidance). Optionally consolidate prompts as a follow-up. Actually wait — if the `update_X` *prompts* stay but the `update_X` *tools* disappear, the prompt text needs rewriting either way. A minimal rewrite: replace references to `update_X(id, content)` with `update(id, type="X", content)`.

- `server.py` docstring: update the tool list (delete 7 lines, add `update` under General tools).

- `docs/MCP.md`: regenerated by `specmgr mcp-docs` (pre-commit covers drift).

- AGENTS.md: the per-domain bullets list `update_req` etc. → update the status paragraph.

- `models/adr/v1/summary.py` line 26 docstring mentions the import chain — check if it still holds.

- CHANGELOG.md [Unreleased].

- ADR? This is a tool-surface change, but it's not really architecture-level… per AGENTS.md: "a decision belongs in a full ADR if it's at the architecture/structure level, affects multiple features, or the whole repo, or overturns/supersedes a prior ADR." Consolidating the update tools is at the tool-surface/structure level, affects every domain, and establishes a new convention for future domains (`ac` will use the generic `update` instead of adding `update_ac`). That's an architectural-level convention change → I think it deserves an ADR (a short one). Or at least a "Decisions Made" entry in the feature README. The "domain-first" ADR (ece4554b) is the governing structure decision; this feature modifies the *tool* convention, not the package layout. Borderline. My recommendation: feature README + a "Decisions Made" entry, plus a short ADR if the user wants to record the `type`-dispatch convention. Ask the user.

- Tests: delete the 7 `test_update_X.py` (~1300 lines total), add `tests/general/tools/test_update.py` covering: each of the 7 types dispatches to the correct directory/model; preserves frontmatter, updates `updated`; status is not modifiable; validation failure writes nothing; unknown id raises a domain-specific NotFound; type/id mismatch (id not in that type's directory) → clear error. Plus a server import-order smoke test.

**Also adjacent (out of scope unless requested):** consolidating the 7 `set_status_X` + ADR's `set_status` into a single `set_status(id, type, status)` — the exact same shape of duplication. And `delete_*` (stubs), `get_*`, `validate_*` (disk-free dry run, same consolidation candidate), `create_*` (not identical — each returns a different doc; though structurally the same pattern). The user said "update commands" specifically; I'll flag `set_status` as the natural follow-up in the same style (or include it if the user wants — the consolidation mechanism is reusable).

**Naming:** tool name `update` (flat MCP namespace) — no collision with existing names. The module is `general/tools/update.py`.

**Backward compatibility:** this is a library with a published PyPI release (v0.2.1) + an MCP registry. Removing `update_req` etc. is a breaking change for existing MCP clients. Options: (a) delete outright (breaking, minor/major version bump), (b) keep the old tools as thin deprecated wrappers for one release. Ask the user. Given that the MCP server is the primary consumer (LLM clients, no versioned API contract beyond the tool list) and the repo is pre-1.0 (0.2.x), a clean break with a major/minor note in the CHANGELOG seems reasonable, but a deprecation wrapper is cheap (each is ~10 lines reusing the dispatcher). My view: since it's 0.x, delete outright; but ask.

**Feature folder:** `.specmgr/feat/feat-NNN-consolidate-update-tool/` (NNN = the GitHub issue number if there is one, else 0). Latest is feat-18.

OK, before I present the plan I should ask confirmation questions. The main open questions:

1. Scope: only the 7 full-body updates (ADR keeps its per-section tools) — or also include ADR in some way? (My recommendation: exclude ADR.)
2. Signature: `update(id, type, content)` (my recommendation) vs `update(id, content)` which scans directories to find the domain.
3. Should the 7 per-domain `update_*` prompts also be consolidated into a single generic prompt, or kept per-domain with updated text (my recommendation: keep per-domain, update text)?
4. Include `set_status_*` consolidation in this feature, or as a follow-up?
5. Breaking change: remove the old tools outright, or leave deprecated wrappers?
6. ADR doc, or just a feature README decision entry?

I could bundle these into a `question` tool call with multiple questions. The plan-mode reminder says "ask the user confirmation questions, or solicit their opinion on trade-offs." Let me present my view concisely and ask 3–5 questions.

Per the system prompt, my answer should be concise (\<4 lines unless detail is asked) — but plan mode with a design question warrants a structured answer. The instructions say to be concise; I'll present a compact view + a question list. Keep it tight.

Draft:

**My view:** Good idea for the 7 full-body update tools (req/uc/tsk/qa/prb/gol/rsk) — they are literally the same function with the type substituted (each 95 lines, `update_X(id, content)` → validate body, preserve frontmatter, bump `updated`, write). Consolidating to one `update` tool reduces 7 tools to 1 and future domains (`ac`) won't add more.

Two caveats:

1. **ADR can't be included in the consolidation**: its update surface is per-section (`update_frontmatter`/`update_section`/`option_*`), by design (MADR) — there's no full-body update. So the "all update commands" scope is really "the 7 full-body ones."
2. **I recommend `type` + `id` over uuid-only**: the uuids are v4s generated independently per domain — practically unique but not guaranteed; resolving a bare uuid requires scanning all domain directories (parsing every file) on the *write* path, and the cost grows with each new domain; the LLM client already knows the domain from its prior calls; and ADR's exclusion makes uuid-only no simpler.

And the questions. Let me ask via the question tool — multiple questions in a single call.

Questions:

1. Signature: (a) `update(id, type, content)` with type a 7-value enum [recommended]; (b) `update(id, content)` — scan all domains to find the owner.
2. Scope: (a) just the 7 full-body tools [recommended]; (b) 7 + consolidate the 7 `set_status_X` + ADR's `set_status` into `set_status(id, type, status)` in the same feature; (c) 7 + set_status as a documented follow-up.
3. Old tools: (a) delete outright (breaking, 0.x) [recommended]; (b) leave deprecated thin wrappers for one release.
4. Prompts: (a) keep the 7 per-domain `update_*` prompts, rewrite the text to call `update(type=...)` [recommended]; (b) consolidate to a single generic `update` prompt too.
5. ADR doc: (a) a short ADR recording the `type`-dispatch convention [recommended?]; (b) just the feature README "Decisions Made".

Hmm, that's 5 questions; the question tool supports multiple. I could maybe consolidate: Q2 and Q3 are both scope-ish. I'll keep 5 — they're quick to answer.

Actually, on #5: per AGENTS.md guidance ("affects multiple features or the whole repo" → ADR; "if in doubt, write the ADR"), the consolidated update tool is a repo-wide convention that future domains must follow. My recommendation: write a short ADR. But the user may prefer the lighter option. I'll leave it as a question.

Before finalizing, one more check — how does the MCP tool schema handle `Literal` types? The `mcp` python SDK (FastMCP-style, `MCPServer` — this is the newer `mcp` package, the low-level `mcp.server.MCPServer` from the SDK?). server.py uses `from mcp.server import MCPServer`. Tools are registered with `@mcp.tool(name=..., title=..., description=...)` and the SDK builds the input schema from type hints (probably via pydantic). A `Literal[...]` should produce an enum in the schema. I won't verify deeply; the implementer can confirm with a `mcp-docs` output check. Actually, it's worth a quick check whether any existing tools use Literal or unions… `specmgr_set_status`'s `status` is just `str`. I'll note it in the plan as a "verify schema generation for Literal" item.

I'll write the response: a compact view, then the questions.

I've reviewed the codebase. Here's my take, grounded in what's actually there:

**The idea is solid for 7 of the 8 domains.** `update_req`/`update_uc`/`update_tsk`/`update_qa`/`update_prb`/`update_gol`/`update_rsk` are literally the same 95-line function with types swapped: validate body via the domain's `from_text`, `load_by_id` under the domain lock, preserve all frontmatter except `updated`, `write_X_file`. The shared plumbing (`general/tools/_doc_paths.py`) already exists. One `update` tool with a `type` enum removes 6 near-duplicate tools, and the future `ac` domain adds none.

**Two important caveats:**

1. **ADR cannot join the consolidation.** Its update surface is section-level by design (`update_frontmatter`, `update_section`, `option_*`) — there is no whole-body `update_adr`, and the MADR plan deliberately makes whole-section replace the contract. So "all update commands" really means "the seven whole-body ones."

2. **I'd recommend `update(id, type, content)` over uuid-only.** The UUIDs are server-generated v4s *independently per domain* — practically unique, not guaranteed. Resolving a bare uuid means scanning all seven (and growing) domain directories, re-parsing every file, on the **write** path — and that cost grows with each new domain. The LLM client always knows the domain anyway (it just called `get_rsk`/`create_rsk`). And since ADR is out regardless, uuid-only doesn't even simplify the ADR case.

Implementation would live in `general/tools/update.py` (the cross-cutting home per AGENTS.md) with a small per-domain dispatch table reusing each domain's existing `_io`/`_write`/`_lock`/`_paths` helpers; the seven `update_X` tool modules get deleted. Circular-import risk is low (domain tools already import the partially-initialized `server` module today) but needs a fresh-import smoke test, since `general` imports before the domains in `server.py:211`.

Before I write the full plan, a few decisions:

**Tool: question**

**Input:**

```json
{
  "questions": [
    {
      "question": "Signature of the consolidated tool?",
      "header": "Signature",
      "options": [
        {
          "label": "id + type + content (Recommended)",
          "description": "type is a 7-value enum (req/uc/tsk/qa/prb/gol/rsk). Deterministic, no directory scanning, no theoretical UUID collision."
        },
        {
          "label": "id + content only",
          "description": "Scan all domain directories to find which one owns the id. One fewer parameter, but write-path scan cost grows per domain."
        }
      ]
    },
    {
      "question": "How far does this feature reach?",
      "header": "Scope",
      "options": [
        {
          "label": "Seven whole-body updates only (Recommended)",
          "description": "update_* tools consolidated; set_status_* and everything else untouched. ADR keeps its section-level tools."
        },
        {
          "label": "Updates + set_status_* too",
          "description": "Also merge the seven set_status_X + ADR's set_status into set_status(id, type, status) — same duplication pattern, same dispatch table."
        }
      ]
    },
    {
      "question": "What happens to the existing update_X tools?",
      "header": "Old tools",
      "options": [
        {
          "label": "Delete outright (Recommended)",
          "description": "Breaking change, but the package is 0.x and the MCP tool list is the only contract. Simplest surface."
        },
        {
          "label": "Keep as deprecated wrappers",
          "description": "Thin ~10-line wrappers calling the dispatcher, marked deprecated in CHANGELOG, removed next release."
        }
      ]
    },
    {
      "question": "The seven per-domain update_X *prompts* (narrated interview flows with packaged instruction .md files) — consolidate or keep?",
      "header": "Prompts",
      "options": [
        {
          "label": "Keep per-domain, rewrite text (Recommended)",
          "description": "Each domain keeps its tailored prompt (names its own schema resource, body sections, status tool); text updated to call update(id, type, content)."
        },
        {
          "label": "Consolidate into one generic update prompt",
          "description": "Also 7→1, but loses domain-specific guidance (e.g. req's level/priority section names) unless it becomes generic prose."
        }
      ]
    },
    {
      "question": "Document the decision as a formal ADR or just in the feature README?",
      "header": "ADR",
      "options": [
        {
          "label": "Short ADR (Recommended)",
          "description": "Establishes a repo-wide convention future domains (ac) must follow — 'whole-body updates go through the generic update tool', per AGENTS.md's 'when in doubt, write the ADR'."
        },
        {
          "label": "Feature README only",
          "description": "Record it in the feature's Decisions Made log; no docs/adr/ entry."
        }
      ]
    }
  ]
}
```

**Output:**

```
User has answered your questions: "Signature of the consolidated tool?"="id + type + content (Recommended)", "How far does this feature reach?"="Updates + set_status_* too", "What happens to the existing update_X tools?"="Delete outright (Recommended)", "The seven per-domain update_X *prompts* (narrated interview flows with packaged instruction .md files) — consolidate or keep?"="Keep per-domain, rewrite text (Recommended)", "Document the decision as a formal ADR or just in the feature README?"="Short ADR (Recommended)". You can now continue with the user's answers in mind.
```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 61.0s)

_Thinking:_

User's choices:

1. `update(id, type, content)` — a 7-value enum.
2. Scope: also consolidate `set_status_*` (the 7 per-domain ones + ADR's `set_status`) into a single `set_status(id, type, status)`.
3. Delete old tools entirely (both the update_X family and the set_status_X family? — "Delete entirely" was about update_X. For set_status, ADR already has a generic `set_status`, so consolidating means adding "adr" to the type enum and deleting the 7 `set_status_X` tools. The existing `set_status` name (ADR) gets replaced by a generic `set_status(id, type, status)` that includes type="adr". This is a breaking rename/signature change for ADR clients — worth noting.)
4. Keep per-domain prompts, rewrite the text.
5. A short ADR.

OK, before writing the plan, let me verify the details of the set_status family:

- Read one `set_status_X` tool (req/tools/set_status_req.py) to confirm the shape.
- Read ADR's set_status (adr/tools/set_status.py) — its signature: `set_status(id, status, superseded_by=None)`? From the MCP tool schema in the system prompt: `specmgr_set_status` has id, status, superseded_by (optional). Per-domain ones: id, status. So the generic version needs `superseded_by` — only meaningful for ADR. In a unified `set_status(id, type, status, superseded_by=None)`: if type != "adr" and superseded_by is given → error? Or ignore? Design decision: allow `superseded_by` only for adr (validate: if type != "adr", raise if superseded_by is not None). Also status enum values: ADR's status values include "superseded by X" strings, while the 7 domains use draft/proposed/accepted/superseded/deprecated/rejected/implemented? From req_update_instructions.md: "status must be one of the following: draft, proposed, accepted, superseded, deprecated, rejected, implemented." So ADR has 6 + the superseded-by variant, the others have 7 (including implemented). Let me check the frontmatter models to verify the exact status sets.

Also check what each set_status_X does: load_by_id, set frontmatter.status, update the `updated` timestamp, write, return the doc.

Also check the `set_status` prompt? Is there a set_status prompt? I didn't see one — the prompts are create_X/update_X (and tsk's implement_task, qa's refine, general's compact_history). OK.

Things to read:

- req/tools/set_status_req.py
- adr/tools/set_status.py
- the frontmatter models to check the status Literal sets (req, adr, rsk frontmatter).

Also for the plan: tests to delete/update: tests/<domain>/tools/test_update\_<domain>.py (7 files) + test_set_status\_<domain>.py (7 files)? Check for the existence of the set_status tests. Also the prompts tests reference the instruction text — tests/<domain>/prompts/test_update\_<domain>.py will need text updates.

Also check how the ADR frontmatter's status is validated (per the schema in the system prompt: "superseded by .+" regex). And check whether each domain's frontmatter has the same 7-value Literal.

Also: the `set_status` consolidation needs the type enum = 8 values (including adr). And update's type enum = 7 values (excluding adr). Hmm — should we include "adr" in update's enum for symmetry? No — update has no whole-body semantics for ADR. Keep 7 values. But this asymmetry is worth documenting in the ADR.

Wait — actually, should I reconsider including "adr" in `update` with a clear error? No — an enum that lists unsupported values is bad. Keep 7 values.

Let me also check mcp_docs generation to understand docs/MCP.md and whether tool ordering matters.

And check the ADRs in `docs/adr/` — how ADRs are written (numbering scheme, filenames), so I can spec the "short ADR" step. Let me look at docs/adr/README.md and one example ADR. Actually, the ADRs are created by specmgr's create_adr tool — the plan can just say "create the ADR with specmgr_create_adr" — but in plan mode I just describe the content.

Let me batch the reads:

1. req/tools/set_status_req.py
2. adr/tools/set_status.py
3. req/models/v1/frontmatter.py (status set)
4. rsk/models/v1/frontmatter.py (status set — might differ?)
5. ls docs/adr/ (filename scheme)
6. Check for existence of set_status tests: find tests -name "*set_status*"

All five decisions noted. Let me verify the `set_status` family's shapes (it now joins the scope) and the ADR conventions before writing the plan.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/tools/set_status_req.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/req/tools/set_status_req.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """``@mcp.tool()`` wrapper: set_status_req (Task 3.14).
19: 
20: The only path that changes a requirement's ``status`` -- mirrors
21: ``adr.tools.set_status``, minus the ``superseded_by``-composition special
22: case: :class:`~biz.dfch.specmgr.req.models.v1.ReqFrontmatter.status` has no
23: ``"superseded by ..."`` pattern, just the closed seven-value set
24: (``draft``/``proposed``/``accepted``/``superseded``/``deprecated``/
25: ``rejected``/``implemented``). Neither ``create_req`` nor ``update_req``
26: accept a ``status`` argument at all -- this is the sole entry point.
27: 
28: Thin file-I/O/id-lookup adapter, re-reading and re-parsing the current
29: on-disk state before re-writing the full file; there is no in-memory cache
30: of a parsed :class:`~biz.dfch.specmgr.req.models.v1.ReqDocument` -- the
31: ``.md`` file itself is always the source of truth. The whole sequence runs
32: under ``req_lock(id)`` so a concurrent mutation against the same id cannot
33: interleave with it and cause a lost update.
34: """
35: 
36: from __future__ import annotations
37: 
38: from datetime import datetime
39: 
40: import frontmatter
41: 
42: from ...server import mcp
43: from ..models.v1 import ReqDocument, ReqFrontmatter
44: from ._io import load_by_id
45: from ._lock import req_lock
46: from ._paths import req_base_dir
47: from ._write import write_req_file
48: 
49: 
50: @mcp.tool(
51:     name="set_status_req",
52:     title="Set requirement status",
53:     description="The only path that changes a requirement's status. Also bumps `updated`.",
54: )
55: def set_status_req(id: str, status: str) -> ReqDocument:
56:     """Replace the status of the requirement identified by ``id``.
57: 
58:     Reconstructs the frontmatter via :class:`ReqFrontmatter`'s own
59:     constructor (not ``model_copy``), so ``status``'s closed-set validator
60:     actually runs -- an invalid ``status`` raises ``pydantic.ValidationError``
61:     uncaught, and nothing is written. Also bumps ``updated`` to the current
62:     timestamp; every other frontmatter field (``id``/``type``/``created``/
63:     ``version``) is carried over unchanged. The body is never touched --
64:     its raw, on-disk markdown (not a render of the parsed model) is read
65:     back and re-persisted verbatim, so this tool cannot introduce any
66:     render-fidelity drift into the body at all.
67: 
68:     Parameters
69:     ----------
70:     id:
71:         The document's specmgr-assigned identifier.
72:     status:
73:         The new status. Must be one of the seven values
74:         :class:`~biz.dfch.specmgr.req.models.v1.ReqFrontmatter.status`
75:         accepts.
76: 
77:     Returns
78:     -------
79:     ReqDocument
80:         The updated document. Raises :class:`._paths.ReqNotFoundError` if
81:         no requirement has this id.
82:     """
83:     base_dir = req_base_dir()
84:     with req_lock(id):
85:         path, existing = load_by_id(base_dir, id)
86:         raw_body = frontmatter.loads(path.read_text(encoding="utf-8")).content  # type: ignore[union-attr]
87: 
88:         now = datetime.now().isoformat(timespec="microseconds")
89:         fm_data = existing.frontmatter.model_dump()
90:         fm_data["status"] = status
91:         fm_data["updated"] = now
92:         new_frontmatter = ReqFrontmatter(**fm_data)
93:         new_doc = ReqDocument(frontmatter=new_frontmatter, body=existing.body)
94:         write_req_file(path, new_frontmatter, raw_body)
95:     return new_doc

(End of file - total 95 lines)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/tools/set_status.py"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/src/biz/dfch/specmgr/adr/tools/set_status.py</path>
<type>file</type>
<content>
1: # Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
2: #
3: # This program is free software: you can redistribute it and/or modify
4: # it under the terms of the GNU Affero General Public License as published
5: # by the Free Software Foundation, either version 3 of the License, or
6: # (at your option) any later version.
7: #
8: # This program is distributed in the hope that it will be useful,
9: # but WITHOUT ANY WARRANTY; without even the implied warranty of
10: # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
11: # GNU Affero General Public License for more details.
12: #
13: # You should have received a copy of the GNU Affero General Public License
14: # along with this program.  If not, see <https://www.gnu.org/licenses/>.
15: #
16: # SPDX-License-Identifier: AGPL-3.0-or-later
17: 
18: """``@mcp.tool()`` wrapper: set_status (plan §8, §9a, §10 item 4).
19: 
20: Thin file-I/O/id-lookup adapter over ``models.adr.v1.mutations.set_status``:
21: re-reads and re-parses the current on-disk state, then re-renders and
22: re-writes the full file; there is no in-memory cache of a parsed
23: :class:`Adr` (plan §7, §9a): the ``.md`` file itself is always the source
24: of truth. The whole sequence runs under ``_lock.adr_lock(id)`` so a
25: concurrent mutation against the same id cannot interleave with it and
26: cause a lost update.
27: 
28: ``models.adr.v1.mutations`` is imported qualified (as ``mutations``)
29: because the pure, in-memory operation it delegates to shares this
30: wrapper's own name.
31: """
32: 
33: from __future__ import annotations
34: 
35: from ...models.adr import Adr
36: from ...models.adr.v1 import mutations
37: from ...server import mcp
38: from ._io import load_by_id, write_adr
39: from ._lock import adr_lock
40: from ._paths import adr_base_dir
41: 
42: 
43: @mcp.tool(
44:     name="set_status",
45:     title="Set ADR Status",
46:     description="Narrow convenience wrapper over a frontmatter update for the common status-change case.",
47: )
48: def set_status(id: str, status: str, superseded_by: str | None = None) -> Adr:
49:     """Replace the status of the ADR identified by ``id``.
50: 
51:     Delegates to ``models.adr.v1.mutations.set_status``: when
52:     ``superseded_by`` is given, ``status`` is composed as
53:     ``f"superseded by {superseded_by}"`` instead of being used verbatim.
54: 
55:     Parameters
56:     ----------
57:     id:
58:         The document's specmgr-assigned identifier.
59:     status:
60:         The new status. Ignored if ``superseded_by`` is given.
61:     superseded_by:
62:         When given, composes the ``"superseded by ..."`` status string.
63: 
64:     Returns
65:     -------
66:     Adr
67:         The updated document.
68:     """
69:     base_dir = adr_base_dir()
70:     with adr_lock(id):
71:         path, adr = load_by_id(base_dir, id)
72:         new_adr = mutations.set_status(adr, status, superseded_by)
73:         write_adr(path, new_adr)
74:     return new_adr

(End of file - total 74 lines)
</content>
```

**Tool: bash**

**Input:**

```json
{
  "command": "grep -rn \"Literal\\|status\" src/biz/dfch/specmgr/req/models/v1/frontmatter.py src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py src/biz/dfch/specmgr/models/adr/v1/frontmatter.py | grep -i \"status\\|literal\" | head -30; echo ---; find tests -name \"*set_status*\" -o -name \"*update_*\" | grep -v pycache | sort; echo ---; ls docs/adr/ | head -30"
}
```

**Output:**

```
src/biz/dfch/specmgr/req/models/v1/frontmatter.py:21:subtype of `MarkdownFrontmatter` that restricts `type` to a fixed ``Literal["req"]``
src/biz/dfch/specmgr/req/models/v1/frontmatter.py:22:and narrows the free-form ``status`` to an appropriate closed vocabulary for requirements.
src/biz/dfch/specmgr/req/models/v1/frontmatter.py:27:from typing import Literal
src/biz/dfch/specmgr/req/models/v1/frontmatter.py:33:#: Fixed, closed set of accepted ``status`` values for requirements -- ADR's six plus
src/biz/dfch/specmgr/req/models/v1/frontmatter.py:55:        default-less ``str`` field to a ``Literal["req"] = "req"``, so a document
src/biz/dfch/specmgr/req/models/v1/frontmatter.py:57:    status:
src/biz/dfch/specmgr/req/models/v1/frontmatter.py:62:        ``_default_blank_status_to_draft`` validator, which runs before this one).
src/biz/dfch/specmgr/req/models/v1/frontmatter.py:71:    type: Literal["req"] = "req"  # type: ignore
src/biz/dfch/specmgr/req/models/v1/frontmatter.py:73:    @field_validator("status")
src/biz/dfch/specmgr/req/models/v1/frontmatter.py:75:    def _validate_status(cls, value: str) -> str:
src/biz/dfch/specmgr/req/models/v1/frontmatter.py:77:            raise ValueError(f"status must be one of {sorted(_ALLOWED_STATUSES)}, got {value!r}")
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py:22:``Literal["rsk"]`` and narrows the free-form ``status`` to a purpose-fit
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py:28:closed-set validator. So `status` is redeclared with a ``"open"`` default and
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py:29:this class adds a `mode="before"` validator (``_default_blank_status_to_open``)
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py:31:inherited ``_default_blank_status_to_draft`` (Pydantic applies child-class
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py:38:from typing import Literal
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py:45:#: Fixed, closed set of accepted ``status`` values for risks -- a purpose-fit
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py:61:#: Default ``status`` value when the key is absent or blank -- the starting
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py:74:        default-less ``str`` field to a ``Literal["rsk"] = "rsk"``, so a document
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py:76:    status:
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py:80:        ``"open"`` (``_default_blank_status_to_open`` below, which runs
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py:81:        before the base's ``_default_blank_status_to_draft``).
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py:90:    type: Literal["rsk"] = "rsk"  # type: ignore
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py:91:    status: str = DEFAULT_RSK_STATUS
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py:93:    @field_validator("status", mode="before")
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py:95:    def _default_blank_status_to_open(cls, value: object) -> object:
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py:96:        """Map an absent/blank ``status`` to ``"open"`` (not the base's ``"draft"``).
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py:98:        Runs before the base's inherited ``_default_blank_status_to_draft``
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py:105:    @field_validator("status")
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py:107:    def _validate_status(cls, value: str) -> str:
---
tests/adr/prompts/test_update_adr.py
tests/adr/prompts/test_update_adr_test.py
tests/adr/tools/test_set_status.py
tests/adr/tools/test_update_frontmatter.py
tests/adr/tools/test_update_section.py
tests/gol/prompts/test_update_gol.py
tests/gol/tools/test_set_status_gol.py
tests/gol/tools/test_update_gol.py
tests/prb/prompts/test_update_prb.py
tests/prb/tools/test_set_status_prb.py
tests/prb/tools/test_update_prb.py
tests/qa/prompts/test_update_qa.py
tests/qa/tools/test_set_status_qa.py
tests/qa/tools/test_update_qa.py
tests/req/prompts/test_update_req.py
tests/req/tools/test_set_status_req.py
tests/req/tools/test_update_req.py
tests/rsk/prompts/test_update_risk.py
tests/rsk/tools/test_set_status_rsk.py
tests/rsk/tools/test_update_rsk.py
tests/tsk/prompts/test_update_task.py
tests/tsk/tools/test_set_status_tsk.py
tests/tsk/tools/test_update_tsk.py
tests/uc/tools/test_set_status_uc.py
tests/uc/tools/test_update_uc.py
---
23a14195-339c-48af-99d2-97c9964041ae-use-iso-8601-for-all-dates-and-times.md
3159caf2-4beb-43f2-9f5d-8f46be0211af-adopt-icontract-as-the-design-by-contract-library-for-specmg.md
33c5ab08-ff58-4c73-8c32-23abaf3838e3-filesystem-is-the-sole-source-of-truth-no-in-memory-id-to-do.md
3bf0326f-065a-424c-a2b9-87e5d5bcfa99-extract-mcp-singleton-into-its-own-module-to-break-domain-se.md
4c6119c9-532f-4629-8977-108e78304f48-parse-validate-render-pipeline-library-choices-no-ast-preser.md
71fd95d7-07f2-466f-81aa-d29b7e3ef34c-generic-update-section-key-value-with-deletion-sentinel-and.md
737858a9-7796-4f01-ae35-5afc1c707818-use-pre-commit-hooks-for-local-quality-gates.md
7531106b-074b-4bd8-a83a-e433d01676e2-expose-listing-and-by-id-reads-as-mcp-resources-in-addition.md
832cd6c1-ef8a-4bfc-990e-a610823f61ae-generic-heading-mapped-markdown-to-pydantic-parsing-with-dec.md
898bfcd0-85f9-462f-93a8-747bda4166c8-author-and-edit-adrs-only-through-mcp-structured-tools-never.md
8cf940c5-3100-485c-a12d-14b59b631712-id-filename-addressing-scheme-server-generated-uuid-id-slug.md
9c687bb1-8ee7-41c8-84ec-07606356bc73-enforce-doc-generation-lint-and-tests-locally-via-pre-commit.md
9d3800cf-b3b4-4d46-8b68-3573d932b1c8-detect-unreferenced-code-with-vulture-not-snakefood-enforced.md
README.md
bbf412a7-965e-4435-8669-c338407d73b7-frontmatter-extension-fields-id-version-with-whole-object-fu.md
bc5e18ad-6bbf-4265-bae4-3e34984a2d29-generic-base-frontmatter-model-for-markdown-document-types-m.md
c73e4f9d-81f3-495d-bd3a-f660ab992ed3-base-the-adr-template-on-madr-4-0-0.md
cb5a2d5f-7020-4c6e-b28d-a38d17b23243-use-conventional-commits-for-commit-messages.md
d54abe50-a2c5-44f8-8bfe-11ea634b6f87-pros-and-cons-of-the-options-as-a-derived-container-with-a-d.md
ddd038f0-ae16-4f4b-beef-df06f7ed226f-prompt-surface-narrated-guidance-plus-step-gated-test-varian.md
ddfb1109-422d-4507-8dbc-dc5e4bec9614-expose-id-based-req-document-reads-as-a-tool-get-req-not-a-r.md
e11421d3-cc1d-487b-af32-ee4093422712-use-architecture-decision-records-adrs-to-document-design-de.md
e369ee2e-3353-4f92-991c-6367d76d832e-organize-development-artifacts-in-specmgr-with-feature.md
ec9f5262-9912-49d0-903f-fcfb54f28c13-expose-domain-list-as-paged-mcp-tools-list-domain-not-resour.md
ece4554b-725c-4f76-bc04-5d2b760363d2-organize-the-codebase-by-document-type-domain-domain-first-h.md

```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 124.6s)

_Thinking:_

Important findings regarding the integration of `set_status`:

1. The per-domain `set_status_X(id, status)` — the 7-value status set differs per domain:

   - REQ: draft/proposed/accepted/superseded/deprecated/rejected/implemented
   - RSK: its own closed set (default is "open"!) — purpose-fit, e.g. open/closed/... needs confirmation.
   - ADR: 6 values + composition of "superseded by ..." via the `superseded_by` parameter.
   - The other domains (uc/tsk/qa/prb/gol): probably the same as REQ, or their own purpose-fit sets.

   Therefore, the integrated `set_status(id, type, status, superseded_by=None)`:

   - Validation of `status` happens per-domain via reconstruction of each domain's Frontmatter (existing behavior — an invalid status raises pydantic.ValidationError). This carries over as-is through dispatch: just set `fm_data["status"] = status` and reconstruct with the domain's Frontmatter class.
   - ADR's special case: composition of `superseded_by` → delegates to `mutations.set_status(adr, status, superseded_by)`. For non-ADR types, `superseded_by` must be rejected (e.g. ValueError: "superseded_by is only supported for type='adr'").
   - Body handling differs: the domain version re-reads the raw body via `frontmatter.loads(...).content` and writes it as-is; ADR uses `write_adr` (render_adr from the parsed model). Per-domain dispatch preserves each behavior.

2. The existing generic `set_status` (ADR) name collides with the new integrated name. Plan: replace `adr/tools/set_status.py` with the generic `general/tools/set_status.py`; the type enum for `set_status` is 8 values (including "adr"); `update`'s type enum is 7 values (no "adr"). Breaking change: the ADR `set_status(id, status, superseded_by)` signature changes to `set_status(id, type, status, superseded_by=None)` — parameter order: to keep it clean, go with `id, type, status, superseded_by`.

   Hmm, wait — parameter order `type` vs `status`: for symmetry with `update(id, type, content)`, use `set_status(id, type, status, superseded_by=None)`.

3. Also, the RSK status vocabulary differs (default is "open"). Let me quickly check which status set each domain has… the frontmatter docstring said "ADR's 6 values plus" (req). rsk has its own "purpose-fit" set. For the plan, it's sufficient to state that per-domain validation is preserved via each domain's Frontmatter class; the integrated tool's docstring can refer to each domain's set. Strictly speaking, no need to enumerate all the sets, but it's useful for prompt text. Let me quickly grep the \_ALLOWED_STATUSES constants for each domain.

4. Test files that need to be deleted: 7 test_update_X.py + 7 test_set_status_X.py + tests/adr/tools/test_set_status.py (replaced by general tests). 7 prompt test files test_update_X.py (prompt text assertions — updated, not deleted).

5. ADR file naming: UUID + slug. Created with `specmgr_create_adr` (MCP tool). There's also ADR 898bfcd0 "Author and edit ADRs only through MCP structured tools, never..." — good, creating the ADR via the tool is mandatory.

Also, let me check how `commands/mcp_docs.py` generates docs/MCP.md — whether the tool order comes from registration order. And the `_ALLOWED_STATUSES` set for each domain. Then I'll write the plan.

Actually, one more consideration regarding `update`'s dispatch table: each domain has a different "body class with from_text" (Requirement.from_text, Goal.from_text, Risk.from_text, UseCase?, TaskList?, ProblemStatement?, QaDocument?). And a different Document class, Frontmatter class, write helper, lock, base dir, NotFound error. The descriptor approach is a small dataclass or tuple:

```python
@dataclass(frozen=True)
class _Updater:
    type_name: str
    body_cls: type  # .from_text for validation
    frontmatter_cls: type  # reconstruction
    document_cls: type  # return value
    base_dir_fn: Callable[[], Path]
    load_by_id: Callable[[Path, str], tuple[Path, Any]]
    write_fn: Callable[[Path, Any, str], None]
    lock: Callable[[str], AbstractContextManager[None]]
```

Return type annotation: a union of the 8 document types for `update` (7) / `set_status`.

For `set_status`, the per-domain operation differs subtly: the domain version writes the raw body as-is; ADR renders via the model. So the descriptor also needs a `mutate_fn(existing, status, superseded_by)`, or simply keep 2 code paths (adr vs the 7). Simpler: a dispatch dict mapping type -> small adapter function that encapsulates the whole read-modify-write under the lock. The tool function itself: validate type, dispatch, done. The adapter is a private module-level function (not an mcp tool). This is clean:

```python
def _update_req(id_: str, content: str) -> ReqDocument: ...  # same body as today's update_req, minus the decorator


...


def update(id: str, type: DocType, content: str) -> Union:
    return _DISPATCH[type](id, content)
```

The adapters could even live in the domain packages (e.g. move the current bodies of the `update_req` functions into plain functions in `req/tools/update_req.py`? No — we're deleting those modules). Options: put the adapters in `general/tools/update.py` (importing per-domain helpers) — one file, about 7×10 lines + dispatch. Or leave a small `req/tools/_update_impl.py`? AGENTS.md's domain-first rule: domain-specific code belongs in the domain package. But these adapters are thin glue for a cross-cutting tool. I want to put them all in `general/tools/update.py` and `general/tools/set_status.py` — 2 new modules, the 7 `update_X.py` deleted, the 7 `set_status_X.py` deleted, `adr/tools/set_status.py` deleted. The private helpers (`_io`, `_write`, `_lock`, `_paths`) remain in the domain and continue to be used by `create_X`, `get_X`, `validate_X` (no changes), and now also used from general.

Hmm wait, after deletion, does `update_X`'s logic become orphaned in each domain's `_write`/`_lock`? No — `create_X` still uses `_write`/`_lock`/`_paths`, and `set_status` moves to general but `load_by_id` etc. are still used. OK.

Vulture check: `ensure_req_base_dir` etc. are still used by create. No problem.

Another detail: the 7 domains' `tools/__init__.py` exports `update_req` etc. in `__all__` and in the docstring — update them. Domain package `__init__.py` docstrings also mention the tool list (e.g. req/__init__.py line 12) — update. server.py docstring — update. AGENTS.md — update (Status section enumerates per-domain tools). docs/MCP.md — regenerate.

Prompt text: 7 instruction files (req_update_instructions.md etc.) reference the `update_X` and `set_status_X` tool names — rewrite to `update(id, type="X", content)` / `set_status(id, type="X", status)`. The prompt tests (tests/<domain>/prompts/test_update_X.py) assert on the rendered text — update accordingly. Also, `qa/prompts/refine.py`'s instruction file (qa_refine_instructions.md) probably references update_qa? It appends questions — probably calls update_qa. Need to check the reference. tsk's implement_task probably doesn't. Also, ADR prompt files (adr_update_instructions.md, adr_update_test_instructions.md) reference ADR tools — no change (ADR tools remain).

Also check `docs/req_schema.json` etc. — no change (models are unchanged).

Feature folder: `.specmgr/feat/feat-NNN-consolidate-update-set-status/README.md` from the `_template/v1/README.md`. NNN: the user should know the issue number; latest is feat-18 → probably feat-19. I'll note "feat-NNN (issue number TBD; use 0 if there's no issue)".

CHANGELOG \[Unreleased\]: breaking changes: removal of 14 tools (7 update_X + 7 set_status_X), signature change of ADR set_status, addition of 2 tools (update, set_status). Version: currently 0.2.x — a breaking change at 0.x typically → 0.3.0 (minor bump) per 0.x convention, but per AGENTS.md the version bump is done at release time; note it in the plan (bump to 0.3.0 at release).

ADR: "Consolidate whole-body update and status-change tools into generic type-dispatched update/set_status" — decision: a single cross-domain tool with explicit `type` (not uuid-only), ADR excluded from `update` (section-level contract) but included in `set_status` with the superseded_by special case. Supersedes nothing; relates to ece4554b (domain-first layout) and the plan.

Verification steps:

- ruff format/check, pylint, vulture (watch out for newly orphaned helpers — e.g. if something is only referenced from deleted tests… `_write` is still used by create; no problem).
- Full unittest suite.
- `specmgr docs` + `specmgr mcp-docs`? Wait — is there a `specmgr mcp-docs` command? AGENTS.md says "docs/MCP.md is auto-generated (via `specmgr mcp-docs`)". The commands directory has mcp_docs.py. Yes.
- Fresh-import smoke test: `python -c "import biz.dfch.specmgr.server"` in a clean venv + verify the registered tool list includes `update`/`set_status` and does not include the 14 deleted ones.
- Check docs/adr/README.md regeneration (adr-toc) after adding the ADR.

Test plan details for the new `tests/general/tools/test_update.py` and `test_set_status.py`:

- Per-domain parameterized: create a doc via the domain's create tool (or fixture), call update(id, type, content) → file is rewritten, frontmatter is preserved, updated is bumped, status is unchanged.
- Invalid content → raises, file is unchanged.
- Unknown id → domain's NotFoundError (or the generic DocNotFoundError?) — decision: preserve per-domain error types via dispatch (each adapter raises its own XNotFoundError, as today). Hmm — but the MCP layer surfaces the exception text to the client anyway; preserving per-domain types is the minimum change. OK: adapter = today's function body as-is, so error behavior is unchanged.
- update with type="adr" → impossible (not in the enum) — schema level.
- set_status: per-domain status vocabulary is enforced (e.g. status "implemented" on rsk → ValidationError, since rsk's set is different… need to check rsk's set).
- set_status(type="adr", superseded_by="X") composes "superseded by X"; set_status(type="req", superseded_by=...) → error.

Let me quickly check rsk's allowed statuses and the other domains' sets, plus check qa_refine_instructions.md for update_qa references. Then I'll write the plan. Also, to know how tool names are listed in docs/MCP.md, I'll check how `mcp_docs` generates (order).

**Tool: bash**

**Input:**

```json
{
  "command": "grep -rn \"_ALLOWED_STATUSES\\s*=\\|ALLOWED.*STATUS.*=\\|DEFAULT_.*STATUS\\s*=\" src/biz/dfch/specmgr/*/models src/biz/dfch/specmgr/models --include=\"*.py\" -A3 | grep -v \"^--$\" | head -60; echo ===; grep -n \"update_qa\\|set_status\" src/biz/dfch/specmgr/qa/data/qa_refine_instructions.md; echo ===; grep -rn \"update_\\|set_status\" src/biz/dfch/specmgr/*/data/*update*.md | grep -o \"update_[a-z]*\\|set_status_[a-z]*\" | sort | uniq -c"
}
```

**Output:**

```
src/biz/dfch/specmgr/gol/models/v1/frontmatter.py:42:_ALLOWED_STATUSES = frozenset(
src/biz/dfch/specmgr/gol/models/v1/frontmatter.py-43-    {
src/biz/dfch/specmgr/gol/models/v1/frontmatter.py-44-        "draft",
src/biz/dfch/specmgr/gol/models/v1/frontmatter.py-45-        "proposed",
src/biz/dfch/specmgr/prb/models/v1/frontmatter.py:43:_ALLOWED_STATUSES = frozenset(
src/biz/dfch/specmgr/prb/models/v1/frontmatter.py-44-    {
src/biz/dfch/specmgr/prb/models/v1/frontmatter.py-45-        "draft",
src/biz/dfch/specmgr/prb/models/v1/frontmatter.py-46-        "active",
src/biz/dfch/specmgr/qa/models/v2/frontmatter.py:46:_ALLOWED_STATUSES = frozenset(
src/biz/dfch/specmgr/qa/models/v2/frontmatter.py-47-    {
src/biz/dfch/specmgr/qa/models/v2/frontmatter.py-48-        "draft",
src/biz/dfch/specmgr/qa/models/v2/frontmatter.py-49-        "active",
src/biz/dfch/specmgr/req/models/v1/frontmatter.py:35:_ALLOWED_STATUSES = frozenset(
src/biz/dfch/specmgr/req/models/v1/frontmatter.py-36-    {
src/biz/dfch/specmgr/req/models/v1/frontmatter.py-37-        "draft",
src/biz/dfch/specmgr/req/models/v1/frontmatter.py-38-        "proposed",
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py:50:_ALLOWED_STATUSES = frozenset(
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py-51-    {
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py-52-        "open",
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py-53-        "mitigating",
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py:64:DEFAULT_RSK_STATUS = "open"
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py-65-
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py-66-
src/biz/dfch/specmgr/rsk/models/v1/frontmatter.py-67-class RskFrontmatter(MarkdownFrontmatter):
src/biz/dfch/specmgr/tsk/models/v1/frontmatter.py:38:_ALLOWED_STATUSES = frozenset(
src/biz/dfch/specmgr/tsk/models/v1/frontmatter.py-39-    {
src/biz/dfch/specmgr/tsk/models/v1/frontmatter.py-40-        "draft",
src/biz/dfch/specmgr/tsk/models/v1/frontmatter.py-41-        "active",
src/biz/dfch/specmgr/uc/models/v2/frontmatter.py:43:_ALLOWED_STATUSES = frozenset({"draft", "proposed", "accepted", "deprecated", "superseded"})
src/biz/dfch/specmgr/uc/models/v2/frontmatter.py-44-
src/biz/dfch/specmgr/uc/models/v2/frontmatter.py-45-
src/biz/dfch/specmgr/uc/models/v2/frontmatter.py-46-class UcFrontmatter(MarkdownFrontmatter):
src/biz/dfch/specmgr/models/md/frontmatter.py:50:DEFAULT_STATUS = "draft"
src/biz/dfch/specmgr/models/md/frontmatter.py-51-
src/biz/dfch/specmgr/models/md/frontmatter.py-52-
src/biz/dfch/specmgr/models/md/frontmatter.py-53-class MarkdownFrontmatter(BaseModel):
===
8:the body content you pass to `update_qa` -- every change to the document
78:`update_qa` is a whole-body replace: carry forward every section of the
82:append the new placeholder pairs from step 4. Call `update_qa(id,
86:Once `update_qa` succeeds, tell the user:
===
      2 set_status_gol
      2 set_status_prb
      1 set_status_qa
      1 set_status_req
      1 set_status_rsk
      1 set_status_tsk
      1 update_adr
      4 update_frontmatter
      4 update_gol
     37 update_instructions
      4 update_prb
      4 update_qa
      4 update_req
      4 update_rsk
      3 update_section
      5 update_test
      4 update_tsk

```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 165.0s)

_Thinking:_

Confirmed:

- The status vocabulary differs by domain (req has 7 values, rsk has open/mitigating/..., uc has 5 values, prb/qa/tsk/gol have their own). Per-domain frontmatter validation needs to be preserved → resolved via dispatch that reconstructs each domain's Frontmatter class.
- The ADR prompt files (adr_update_instructions.md) reference update_frontmatter/update_section/update_adr — no changes (ADR tools are preserved).
- The 7 domain update-instruction files reference the `update_X` and `set_status_X` names, and additionally qa_refine_instructions.md also references `update_qa` (3–4 places). Therefore the rewrite targets are the 7 `*_update_instructions.md` + `qa_refine_instructions.md`.

Now I have all the info I need to write the plan. Let me structure it:

**Feature: feat-NNN-consolidate-mutation-tools** (the NNN from the GitHub issue; use 0 if none exists)

01. Create the feature folder from `.specmgr/_template/v1/README.md`.
02. Create a short ADR via specmgr_create_adr: "Generic type-dispatched update/set_status mutation tools for cross-domain document types" — decision: `update(id, type, content)` for the 7 whole-body domains; `set_status(id, type, status, superseded_by?)` for 8 domains (including adr); explicit `type` rather than uuid-only; delete the old tools; keep the ADR section-level tools.
03. New `general/tools/update.py`: 7 private adapters (porting the function bodies from each domain's `update_X` as-is, each preserving its lock/load/write/error semantics) + a dispatch table + an `@mcp.tool(name="update")` with a `Literal` type parameter. Return-type annotation = a union of the 7 document models.
04. New `general/tools/set_status.py`: 8 adapters (7 domain ports + ADR port that includes the superseded_by composition) + a `@mcp.tool(name="set_status")` with `Literal` of 8 values + optional `superseded_by`; if superseded_by is non-None and type != "adr", raise ValueError.
05. Delete: `req/tools/update_req.py`, `uc/tools/update_uc.py`, `tsk/tools/update_tsk.py`, `qa/tools/update_qa.py`, `prb/tools/update_prb.py`, `gol/tools/update_gol.py`, `rsk/tools/update_rsk.py`, the 7 `set_status_X.py` files, `adr/tools/set_status.py`.
06. Update each domain's `tools/__init__.py` (imports + `__all__` + docstrings) and the domain `__init__.py` docstrings (the tool list in req/__init__.py etc.).
07. Update `general/tools/__init__.py` (register the 2 new tools).
08. Import-order check: `general` is imported 2nd in server.py's import line; the new module pulls in all domain tool packages early — add a fresh-import smoke test (`python -c "from biz.dfch.specmgr import server"` and verify the registered tool names). Note that the existing `from ...server import mcp` pattern is already proven.
09. Rewrite the 7 `*_update_instructions.md` + `qa_refine_instructions.md`: replace `update_X(id, content)` → `update(id, type="X", content)`, `set_status_X(id, status)` → `set_status(id, type="X", status)`; keep the domain-specific guidance.
10. server.py docstring: update the tool list (remove 7×2 + ADR's set_status; add `update` and `set_status` under General tools; adjust the per-domain lines).
11. Tests: delete the 14 `test_update_X.py`/`test_set_status_X.py` tool tests (8 including adr's test_set_status); add `tests/general/tools/test_update.py` and `test_set_status.py` parameterized per type; update the 7 prompt tests that assert on the instruction text.
12. Regenerate: `specmgr mcp-docs` (docs/MCP.md), `specmgr adr-toc` (docs/adr/README.md), `specmgr docs` (docs/api). Run pre-commit gates: ruff format/check, vulture, pylint, full unittest.
13. CHANGELOG \[Unreleased\]: breaking-change entry.
14. Update AGENTS.md's Status section (per-domain tool list; note the generic mutation tools under general/).

Validation/verification section: full test suite, fresh-import smoke test, mcp-docs drift check.

Open items/assumptions:

- `type` parameter name — note: `type` shadows the builtin; the codebase's conventions? Existing code uses `type` as a frontmatter field name. The MCP tool parameter name `type` is fine on the client side; on the Python side, either rename to `type_` inside the function (convention: models use `type_`?) and use the decorator alias… hmm. The mcp SDK builds the schema from the function signature; parameter name `type` becomes the JSON schema name "type". The shadowing of the builtin `type` is a lint concern (A002 is flake8-builtins, not enabled by default in ruff). The codebase asserts `isinstance(type_name, str)` etc. To be safe: name the parameter `type` in the signature (schema correctness) — or verify how the mcp SDK handles the name. Keep the plan simple: the parameter is `type` (matches the frontmatter field and the client-facing vocabulary); ruff's defaults don't flag builtin shadowing; if it does, use `# noqa`. Actually, let me check the ruff config in pyproject to see the enabled rules. A minor implementation detail — I'll note it.

- Union return type: `ReqDocument | UcDocument | ...` — verify the mcp SDK can serialize all 7 (it json-encodes the result; pydantic models → model_dump). Existing tools already return typed models, so no problem.

- Whether the `update`/`set_status` adapters should be placed in `general/tools/` or kept in each domain: I chose `general/tools/` with imports of domain private helpers. Circular imports: `general.tools.update` → `req.tools._io` → `req.tools.__init__` → all of req's tool modules → `...server` (mcp is already bound, OK) and `req.prompts` → `...general.tools._packaged_data` (submodule import, safe mid-initialization). I'm fairly confident, but I'll note that a smoke test is required.

Let me quickly check the ruff rules in pyproject to address the `type` parameter naming… actually, that's an implementation detail; I'll just add a one-liner to the plan. No, since I'm recommending the parameter name `type`, let me just quickly check to be safe.

One last detail — ruff's rule config, since the new tool's parameter will be named `type` (builtin shadowing):

**Tool: bash**

**Input:**

```json
{
  "command": "grep -A30 \"\\[tool.ruff\" pyproject.toml | head -45"
}
```

**Output:**

```
[tool.ruff]
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "W"]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["E501"]
# vulture whitelist: bare name/attribute references are intentional (see whitelist.py).
"whitelist.py" = ["F821"]

[tool.pylint.format]
max-line-length = 120

[tool.setuptools]
include-package-data = true

[tool.setuptools.packages.find]
where = ["src"]
namespaces = true

[tool.setuptools.package-data]
"biz.dfch.specmgr" = [
    "py.typed"
]
"biz.dfch.specmgr.adr" = [
    "data/*.md"
]
"biz.dfch.specmgr.gol" = [
    "data/*.md",
    "data/*.json"
]
"biz.dfch.specmgr.prb" = [
    "data/*.md",
    "data/*.json"
]
"biz.dfch.specmgr.qa" = [

```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 92.6s)

_Thinking:_

Ruff only selects E/F/W — no builtin-shadowing rules (A002 is flake8-builtins, not included). So the `type` parameter is lint-clean.

That's everything I need. Let me write the plan. Should keep it structured but concise. The plan will be presented as text (plan mode — no writing to files). Since the user asked "what do you think?" and I've already conveyed my opinion and gotten an answer, now is the time to present the final plan.

Plan structure:

1. Feature folder + ADR
2. New generic tools (update, set_status)
3. Removals
4. Documentation/text updates (prompts, instruction data files, server.py docstring, AGENTS.md, CHANGELOG)
5. Tests
6. Regeneration + validation gates
7. Explicit non-goals

Keep it concise.

Ruff only runs E/F/W, so a `type` parameter is lint-clean. Here's the full plan.

---

## Plan: consolidate `update_*` / `set_status_*` into generic type-dispatched tools

### 0. Decisions (locked via your answers)

- `update(id, type, content)` — `type: Literal["req","uc","tsk","qa","prb","gol","rsk"]` (no `adr`: ADR's contract is section-level, deliberately no whole-body replace).
- `set_status(id, type, status, superseded_by=None)` — `type` covers all **8** domains incl. `adr`; `superseded_by` (the `"superseded by X"` composition) accepted only for `type="adr"`, rejected with a `ValueError` otherwise.
- Old tools **deleted outright** (breaking; 0.x). Per-domain prompts kept, text rewritten. Short ADR written.

### 1. Artifacts first

1. `.specmgr/feat/feat-NNN-consolidate-mutation-tools/README.md` from `.specmgr/_template/v1/README.md` (NNN = GitHub issue number, `0` if none).
2. ADR via `specmgr_create_adr`: *"Generic type-dispatched mutation tools for cross-domain documents"* — decision: explicit `type` parameter over bare-uuid resolution (per-domain v4 UUIDs not guaranteed-unique; uuid-only would force all-directory scans on the write path, cost growing per domain); ADR excluded from `update` but included in `set_status`; future domains (`ac`) add a dispatch entry instead of a new tool.

### 2. New code — `general/tools/` (the cross-cutting home per AGENTS.md)

3. `general/tools/update.py` — private adapter functions whose bodies are the seven current `update_X` function bodies **verbatim** (each keeps its own `X_lock`, `load_by_id`, frontmatter carry-over + `updated` bump, `write_X_file`, domain-specific `XNotFoundError`), a dispatch table keyed by `type`, and:
   ```python
   @mcp.tool(name="update", ...)
   def update(id: str, type: Literal[...7 values...], content: str) -> ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument | GolDocument | RskDocument
   ```
4. `general/tools/set_status.py` — same pattern with eight adapters: the seven domain bodies verbatim (raw-body re-read + per-domain `XFrontmatter` reconstruction, so each domain's closed status vocabulary still validates — req: 7 values, rsk: `open`/`mitigating`/…, uc: 5 values, etc.) plus the ADR body (delegates to `models.adr.v1.mutations.set_status` for `superseded_by` composition).
5. Register both in `general/tools/__init__.py` (add to imports + `__all__`).

**Import-order caveat:** `general` is imported 2nd in `server.py:211`, so these modules pull every domain `tools`/`prompts` package in earlier than today. This reuses the already-proven `from ...server import mcp` partial-init pattern (domain tools do it today), and all `general.tools._packaged_data` imports use the safe submodule form — but a fresh-process smoke test is mandatory (step 10).

### 3. Deletions (15 modules)

6. Delete `update_req/uc/tsk/qa/prb/gol/rsk.py` from the six `tools/` dirs, the seven `set_status_*.py`, and `adr/tools/set_status.py` (replaced by the generic one). Private helpers (`_io`/`_write`/`_lock`/`_paths`) **stay** in each domain — `create_*`/`get_*`/`validate_*` and the new adapters all use them.

### 4. Docstring / text updates

07. Each domain `tools/__init__.py` (imports, `__all__`, docstring tool list) and each domain `__init__.py` docstring (e.g. `req/__init__.py:12`).
08. `server.py` module docstring (the authoritative list): drop the 7 `update_X`, 7 `set_status_X`, ADR `set_status`; add `update` + `set_status` under "General tools".
09. Packaged instruction files — rewrite tool references, keep domain-specific guidance:
    - 7 × `{domain}_update_instructions.md`: `update_req(id, content)` → `update(id, type="req", content)`, `set_status_req(...)` → `set_status(id, type="req", status)` (also fix the status-enum prose where vocabularies differ, e.g. rsk/uc).
    - `qa/data/qa_refine_instructions.md` (references `update_qa` in 3 places).
    - ADR instruction files untouched (their tools remain).
10. `AGENTS.md` Status section: per-domain bullets lose `update_X`/`set_status_X`; `general/` bullet gains the two mutation tools.
11. `CHANGELOG.md` `[Unreleased]`: breaking — removed 14 tools, ADR `set_status` signature change (`id, status, superseded_by` → `id, type, status, superseded_by`), added 2 generic tools.

### 5. Tests

12. Delete 15 tool-test files: 7 × `tests/{domain}/tools/test_update_*.py`, 7 × `test_set_status_*.py`, `tests/adr/tools/test_set_status.py`.
13. Add `tests/general/tools/test_update.py` + `test_set_status.py`, parameterized per type: frontmatter preserved / `updated` bumped / body replaced; invalid content → raises, file untouched; unknown id → domain-specific `NotFoundError`; status vocabulary enforced per domain; `superseded_by` composition for `adr` and rejection for non-`adr`.
14. Update 7 × `tests/{domain}/prompts/test_update_*.py` for the rewritten instruction text.
15. New smoke test: fresh-import `biz.dfch.specmgr.server`, assert registered tool names contain `update`/`set_status` and none of the 14 removed names.

### 6. Regenerate + gates

16. `uv run --frozen specmgr mcp-docs` (docs/MCP.md), `specmgr adr-toc` (docs/adr/README.md), `specmgr docs` (docs/api/ + GENERATED.md).
17. Full gates: `ruff format --check && ruff check`, `pylint $(git ls-files '*.py')`, `vulture src/ whitelist.py --min-confidence 60` (watch for newly orphaned symbols), `python -m unittest discover -v -s tests -t . -p "test_*.py"`.

### Non-goals

- No change to ADR's section-level tools (`update_frontmatter`/`update_section`/`option_*`), no whole-body `update_adr`.
- No consolidation of `create_*`/`get_*`/`validate_*`/`delete_*` (different shapes; `delete_*` are stubs).
- No version bump in this feature (done at release, per AGENTS.md — would land as `0.3.0`).

Want me to adjust anything — e.g. the feature slug, or start executing once you drop me out of plan mode?

---

## User

You shall create a feature from that with phases as it is described in an ADR (about work units). Every phase must have a complete test cycle. We do not want to test only at the end. And the feature shall be orchestrated by the Phase-Orchestrator agent and implemented by Phase-Implementer agent. Go over the plan and adjust if necessary.

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 164.9s)

_Thinking:_

The user is asking me for the following:

1. Create a feature (i.e., a feature folder `.specmgr/feat/feat-NNN-*/README.md`) from the plan, including phases as described in an ADR about work units.
2. Attach a complete test cycle to every phase — don't just test at the end.
3. This feature will be orchestrated by the Phase Orchestrator agent and implemented by the Phase Implementer agent.
4. Review the plan and adjust if necessary.

Wait — there's a contradiction here: plan mode is read-only. The user is saying "create a feature from it" — but in plan mode I can't write files. Hmm. The user's message is an instruction to adjust the plan so that the feature creation (with phases) is part of the plan, and to orchestrate with the Phase Orchestrator / Phase Implementer agents. The system reminder says plan mode is active and strictly no edits. So what I should do is:

- Look for the ADR about work units (phases) — which ADR is it? "as described in an ADR (about work units)". Let me search the ADRs in docs/adr/ for one about work units / phases / feature plans. There's ADR e369ee2e "Organize development artifacts in .specmgr with feature-driven work units" — this is about work units! The user probably means this one: feature-driven work units, a single README.md containing plan + progress.
- Also check `.specmgr/conventions.md` and the feature template `.specmgr/_template/v1/README.md` to see how phases are structured.
- Check existing feature READMEs (e.g., feat-18-goal, feat-15-add-artifact-type-risk) to see the phase structure actually in use — phases with a progress section, "current status", "recent updates".
- Check the Phase Orchestrator / Phase Implementer agents — these are agents available in this environment (task tool: phase-implementer "implements exactly one phase of the `.specmgr/feat/<id>/README.md` plan end-to-end — code, tests, end-of-phase quality gate, updating the plan's progress section — then stops and reports. Driven by phase-orchestrator, not intended to be selected directly."). So the workflow is: I (or the user) drive the Phase Orchestrator, and the Phase Orchestrator spawns Phase Implementers per phase. The feature README needs to be structured so that Phase Implementers can pick up each phase: phase definition, acceptance criteria, test cycle per phase.

So my job right now: refine the plan as follows:

1. First step (Phase 0 or just a setup step): create the feature folder + README with the phase breakdown, and create the ADR.
2. Break the work into phases, each with a complete test cycle (not just at the end).
3. Adjust the earlier plan to fit the phase structure.
4. Then (after plan mode ends) orchestrate with Phase Orchestrator → Phase Implementer.

Let me read the ADR about work units (e369ee2e), the template, conventions.md, and one or two recent feature READMEs to align the phase structure with the actual convention.

Things to read:

- docs/adr/e369ee2e-3353-4f92-991c-6367d76d832e-organize-development-artifacts-in-specmgr-with-feature.md
- .specmgr/\_template/v1/README.md
- .specmgr/conventions.md
- .specmgr/feat/feat-18-goal/README.md (recent, with phases)
- possibly .specmgr/feat/feat-15-add-artifact-type-risk/README.md

Let me run these in parallel.

Let me review the work-units ADR, the feature template, and recent feature READMEs to shape the phase structure correctly.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/docs/adr/e369ee2e-3353-4f92-991c-6367d76d832e-organize-development-artifacts-in-specmgr-with-feature.md"
}
```

**Output:**

````
<path>/home/user/src/biz.dfch.SpecMgr/docs/adr/e369ee2e-3353-4f92-991c-6367d76d832e-organize-development-artifacts-in-specmgr-with-feature.md</path>
<type>file</type>
<content>
1: ---
2: status: accepted
3: date: '2026-08-05'
4: decision-makers: dfch
5: id: e369ee2e-3353-4f92-991c-6367d76d832e
6: version: 1.0.0
7: ---
8: 
9: # Organize development artifacts in `.specmgr` with feature-driven work units
10: 
11: ## Context and Problem Statement
12: 
13: The project maintains two documentation folders with an unclear split: `docs/` — published, generated documentation (API docs, ADRs, specifications), which reflects the current state of the project — and `doc/` — development progress notes, planning artifacts, research, which has no clear ongoing purpose once this ADR's structure exists. As part of adopting this ADR's outcome, `doc/` is dissolved: its content is migrated (manually, see Consequences) into the new structure below, and the `doc/` folder is retired. Development artifacts (plans, progress tracking, work-unit status) need a structured, agent-friendly location that is: (1) separate from published documentation (`docs/`); (2) organized by feature/work-unit for easy agent reference; (3) generic enough to serve as a template for future projects using specmgr as a toolkit.
14: 
15: ## Decision Drivers
16: 
17: - Agent-friendly reference paths: agents should reference specific feature paths inline (e.g., "See `.specmgr/feat/feat-001-adr-toc/README.md`"), keeping agent instructions lean and focused
18: - Toolkit reusability: structure should be generic enough for future projects adopting specmgr as a toolkit — the folder name itself (`.specmgr/`) is chosen for this reason, following the convention of tool-named dotfolders like `.github/`, `.vscode/`, `.docker/`
19: - Clear separation of concerns: development artifacts must be distinct from published documentation
20: - Version control and auditability: development progress should be tracked in git with full history
21: 
22: ## Considered Options
23: 
24: - Single README.md per feature containing both plan and progress
25: - Separate README.md (plan) and progress.md (status) per feature
26: 
27: ## Decision Outcome
28: 
29: **Chosen option: "Option 1: .specmgr structure"** — a single `README.md` per feature combining plan and progress, with an optional sibling `history.md` for rotating out older `Recent Updates` entries. Every feature `README.md` also carries a minimal YAML frontmatter block (`id`, `version`, `status`, `created`, `updated` — see that option's "Frontmatter" note for details). There is no separate `GitHub Issue` field or body line: the issue number is the `NNN` infix already embedded in `id` (the folder name, `feat-NNN-slug`) itself.
30: 
31: This is preferred over Option 2 (separate `README.md`/`progress.md`) for its simplicity: one file per feature, no cross-file cross-referencing needed to see the full feature story, and the single canonical Task List (status inline per task) removes the Implementation Plan/Execution Plan duplication that Option 2 still carries. See "Pros and Cons of the Options" below for the full tradeoff analysis, and that option's "Open Questions" for points intentionally left open for later decisions.
32: 
33: ### Consequences
34: 
35: **Positive:**
36: - Agents can reference specific feature paths inline, keeping instructions lean and focused
37: - Clear separation: agents only read what's relevant to their task
38: - Structure is reusable for future projects adopting specmgr as a toolkit
39: - Development progress is version-controlled and auditable
40: - The `.specmgr/` folder (and its `feat/` work units) is committed to git like any other tracked path in the repo — no `.gitignore` exclusion — so history and review apply to it the same way they do to `docs/` and source code
41: 
42: **Negative:**
43: - Adds another top-level folder to the repo structure
44: - Requires discipline to keep progress sections updated (hand-maintained, not auto-generated)
45: - Migrating `doc/`'s existing content (e.g. `doc/adr-tool-plan.md`, `doc/refactor-domain.md`) into the new structure is done manually, one file at a time, once this ADR is adopted — no automated migration tooling is planned
46: 
47: **Numbering convention:**
48: - `feat-NNN-slug` — `NNN` is the GitHub issue number for feature work tied to an issue. There is no separate `github_issue` frontmatter field or body line: `id` (the folder name itself) is the single source of truth for the issue number, read by parsing its `NNN` infix.
49: - Work started without a GitHub issue yet uses `feat-0-slug` (issue number `0`) until/unless an issue is later opened for it
50: 
51: **ADR vs. feature-level "Decisions Made" log:**
52: A decision belongs in a full ADR (under `docs/adr/`) if it: (a) is architecture/structure-level and affects more than one feature or the repo as a whole, (b) would be relevant to someone joining the project later trying to understand why something is the way it is, or (c) reverses/supersedes a previous ADR. A decision belongs in the feature's own "Decisions Made" log instead if it: (a) is scoped entirely to that one feature's implementation details, (b) wouldn't need to be found by searching ADRs later, and (c) doesn't constrain future features. Tie-breaker: if in doubt, write the ADR — it is cheap to write and already indexed by `adr-toc`, so overuse is low-cost, while under-use risks losing a decision in a feature folder no one will grep later.
53: 
54: ### Confirmation
55: 
56: For now, confirmation that new `feat-NNN-slug/README.md` files follow the chosen structure/template is done manually via PR review. Automated enforcement (e.g. a `specmgr feat-*` validation tool mirroring `validate_adr`) is deferred to future work, consistent with the other deferred-tooling items noted in the chosen option's Open Questions.
57: 
58: ## Pros and Cons of the Options
59: 
60: ### Option 1: .specmgr structure
61: 
62: ```
63: .specmgr/
64: ├── feat/                          # Feature work units
65: │   └── feat-NNN-slug/             # One folder per GitHub issue
66: │       ├── README.md              # Feature plan + progress (mandatory)
67: │       └── history.md             # Archived older "Recent Updates" entries (optional)
68: └── (other dirs as needed)
69: ```
70: 
71: **File purposes:**
72: - `README.md` — Single file containing both the feature plan (requirements, acceptance criteria, task list, scope, dependencies, design notes) and progress tracking (current state, blockers, decisions made during implementation, links to related ADRs or PRs)
73: - `history.md` — Optional sibling file. Holds older `Recent Updates` entries once `README.md` grows too long; `README.md` keeps only recent entries and links back to this file for anything older.
74: 
75: **Frontmatter:** Every feature `README.md` carries a YAML frontmatter block, mandatory fields `id` (the `feat-NNN-slug` folder name itself, not a generated UUID — unlike ADR frontmatter's server-generated `id`), `version` (semver, starts at `1.0.0`), `status` (`planning` | `in-progress` | `review` | `done`), and `created`/`updated` (`YYYY-MM-DD`, `updated` bumped on every substantive edit). There is no separate `GitHub Issue` field, in frontmatter or body: the issue number is the `NNN` infix already embedded in `id` (i.e. the folder name, `feat-NNN-slug`) — `0` means no issue yet — so it is derived by reading `id`, never duplicated as its own field.
76: 
77: **Template: README.md**
78: 
79: ```markdown
80: ---
81: id: feat-NNN-slug
82: version: 1.0.0
83: status: planning
84: created: YYYY-MM-DD
85: updated: YYYY-MM-DD
86: ---
87: 
88: # Feature: [Feature Title]
89: 
90: ## Plan
91: 
92: ### Overview
93: 
94: Brief description of what this feature does and why it matters.
95: 
96: ### Requirements
97: 
98: - REQ-001: [Functional requirement]
99: - REQ-002: [Non-functional requirement]
100: - REQ-003: [Constraint or dependency]
101: 
102: ### Acceptance Criteria
103: 
104: - [ ] ACC-001: Verifies REQ-001 — [testable condition]
105: - [ ] ACC-002: Verifies REQ-002 — [testable condition]
106: - [ ] ACC-003: Verifies REQ-003 — [testable condition]
107: 
108: ### Scope
109: 
110: What is included in this feature:
111: - Item 1
112: - Item 2
113: 
114: What is explicitly out of scope:
115: - Item A
116: - Item B
117: 
118: ### Dependencies
119: 
120: - Depends on: [other feat-NNN-slug, ADR id, or external]
121: - Blocks: [other feat-NNN-slug]
122: 
123: ### Design Notes
124: 
125: Any architectural decisions, patterns, or design rationale relevant to this feature.
126: 
127: ### Related ADRs
128: 
129: - [ADR id]: [Title]
130: - [ADR id]: [Title]
131: 
132: ### Task List
133: 
134: Single, canonical breakdown of work phases and tasks. Status lives on the
135: task itself — there is no separate "planned" vs. "executed" list to keep in
136: sync; a task's line *is* its current status. Update it in place as work
137: progresses (edit, don't duplicate).
138: 
139: #### Phase 1: [Phase name]
140: - [x] Task 1.1: [description] — depends on: none — status: done (2026-08-01)
141: - [ ] Task 1.2: [description] — depends on: Task 1.1 — status: in-progress, ETA 2026-08-10
142: - [ ] Task 1.3: [description] — depends on: Task 1.2 — status: blocked (see Blockers)
143: 
144: #### Phase 2: [Phase name]
145: - [ ] Task 2.1: [description] — depends on: Task 1.3 — status: not-started
146: - [ ] Task 2.2: [description] — depends on: Task 2.1 — status: not-started
147: 
148: **Note:** If a task's scope changes mid-flight, edit its description in place;
149: rely on git history (`git log -p` on this file) to recover what was
150: originally planned, rather than keeping a second copy of the task around.
151: 
152: ## Progress
153: 
154: ### Current Status
155: 
156: **As of [YYYY-MM-DD]**: [Brief status summary]
157: 
158: ### Blockers
159: 
160: - [ ] Blocker 1 — [description, impact, mitigation]
161: - [ ] Blocker 2 — [description, impact, mitigation]
162: 
163: (Remove this section if no blockers.)
164: 
165: ### Recent Updates
166: 
167: If this section grows too long, move older entries to `history.md` in this
168: same folder and leave a pointer here, e.g.:
169: `See history.md for updates before YYYY-MM-DD.`
170: 
171: #### Update [YYYY-MM-DDTHH:mm:ssz] (newest)
172: - Completed: [what was done]
173: - Next: [what comes next]
174: - Notes: [any relevant context]
175: 
176: #### Update [YYYY-MM-DDTHH:mm:ssz] (oldest)
177: - Completed: [what was done]
178: - Next: [what comes next]
179: - Notes: [any relevant context]
180: 
181: ### Decisions Made
182: 
183: - **[YYYY-MM-DD]**: [Decision] — [Rationale]
184: - **[YYYY-MM-DD]**: [Decision] — [Rationale]
185: 
186: ### Related PRs / Commits
187: 
188: - [PR #NNN](link): [description]
189: - [Commit hash](link): [description]
190: ```
191: 
192: **Pros:**
193: - Single file to maintain
194: - Simpler structure: one file per feature
195: - Plan and progress are always together in one document
196: - Easier to see the full feature story (what was planned vs. what happened) in one place
197: - Requirements and acceptance criteria are co-located with clear traceability
198: - Single Task List: no separate Implementation/Execution Plan pair to keep in sync — status is a property of each task line, not a duplicated list, so there is nothing to drift
199: - Auditability of "what was planned vs. what actually happened" comes from git history on this one file, not from a hand-maintained duplicate
200: - `Recent Updates` growth is bounded by rotating older entries into an optional `history.md`, keeping `README.md` itself lean
201: - Frontmatter `id`/`version`/`status`/`created`/`updated` gives each feature folder a compact, machine-readable header, mirroring the ADR frontmatter's `status` field for consistency across both document types
202: - No `GitHub Issue` duplication: the issue number is already encoded in `id`'s `NNN` infix, so there is nothing to keep in sync between a frontmatter/body field and the folder name itself
203: 
204: **Cons:**
205: - File grows over time as progress updates (Recent Updates, Decisions Made) accumulate, even with rotation available
206: - Plan and progress are intermingled, making it harder to extract just the plan for reference
207: - No clear separation between "contract" (what we committed to) and "journal" (what actually happened) — relies on git history to reconstruct the original plan instead of a preserved, separate copy
208: - Still hand-maintained/free-text: nothing currently enforces that a task's status field, or the frontmatter `status`/`updated` fields, are kept in sync with reality, or that `history.md` rotation actually happens
209: - Deriving the GitHub issue number from `id`'s `NNN` infix requires parsing the folder name rather than reading a dedicated field — acceptable since `feat-NNN-slug` is already a fixed, documented convention
210: 
211: **Open Questions:**
212: - Archival/lifecycle rule for the file once `status: done` (stay in place / archive / prune) — intentionally left undecided here; treated as a separate future project decision, not a gap in this ADR.
213: - Rotation strategy for `Recent Updates`: rotating older entries into `history.md` is documented here as an available option; the exact trigger (manual vs. a fixed entry-count rule) and mechanics are left to the user/agent maintaining the feature folder to decide at the time, not prescribed by this ADR.
214: - Template location: **resolved** — the template now exists at `.specmgr/_template/v1/README.md`, matching the versioned path scheme originally proposed here.
215: - Whether to add further frontmatter fields later (e.g. `decision_makers`, `related_adrs`, `tags`) is left open; the current five-field frontmatter (`id`, `version`, `status`, `created`, `updated`) is a deliberate, minimal starting point, not a ceiling.
216: - Recommendation (not yet built, non-blocking): a dedicated MCP tool (analogous to this project's `update_section`/`option_update` for ADRs) that flips one task's status field, or the frontmatter `status`, atomically, instead of relying on an agent/human to locate and hand-edit the right line.
217: 
218: ### Option 2: .specmgr structure with separate README.md (plan) and progress.md (status)
219: 
220: ```
221: .specmgr/
222: ├── feat/                          # Feature work units
223: │   └── feat-NNN-slug/             # One folder per GitHub issue
224: │       ├── README.md              # Feature plan (mandatory)
225: │       └── progress.md            # Status tracking (mandatory)
226: └── (other dirs as needed)
227: ```
228: 
229: **File purposes:**
230: - `README.md` — Contains the complete feature plan: requirements, acceptance criteria, implementation plan, scope, dependencies, design notes, any pre-implementation research. Treated as immutable once work begins (except Implementation Plan, which may be refined during execution).
231: - `progress.md` — Hand-maintained status log: execution plan (tracking actual progress), current state, blockers, decisions made during implementation, links to related ADRs or PRs. Updated throughout the feature lifecycle.
232: 
233: **Template: README.md**
234: 
235: ```markdown
236: # Feature: [Feature Title]
237: 
238: **GitHub Issue**: #NNN  
239: **Status**: [Planning | In Progress | Review | Done]
240: 
241: ## Overview
242: 
243: Brief description of what this feature does and why it matters.
244: 
245: ## Requirements
246: 
247: - REQ-001: [Functional requirement]
248: - REQ-002: [Non-functional requirement]
249: - REQ-003: [Constraint or dependency]
250: 
251: ## Acceptance Criteria
252: 
253: - [ ] ACC-001: Verifies REQ-001 — [testable condition]
254: - [ ] ACC-002: Verifies REQ-002 — [testable condition]
255: - [ ] ACC-003: Verifies REQ-003 — [testable condition]
256: 
257: ## Scope
258: 
259: What is included in this feature:
260: - Item 1
261: - Item 2
262: 
263: What is explicitly out of scope:
264: - Item A
265: - Item B
266: 
267: ## Dependencies
268: 
269: - Depends on: [other feat-NNN-slug, ADR id, or external]
270: - Blocks: [other feat-NNN-slug]
271: 
272: ## Design Notes
273: 
274: Any architectural decisions, patterns, or design rationale relevant to this feature.
275: 
276: ## Related ADRs
277: 
278: - [ADR id]: [Title]
279: - [ADR id]: [Title]
280: 
281: ## Implementation Plan
282: 
283: High-level breakdown of work phases and tasks:
284: 
285: ### Phase 1: [Phase name]
286: - Task 1.1: [description] — Depends on: [none/other tasks]
287: - Task 1.2: [description] — Depends on: Task 1.1
288: 
289: ### Phase 2: [Phase name]
290: - Task 2.1: [description] — Depends on: Task 1.2
291: - Task 2.2: [description] — Depends on: Task 2.1
292: ```
293: 
294: **Template: progress.md**
295: 
296: ```markdown
297: # Progress: [Feature Title]
298: 
299: ## Current Status
300: 
301: **As of [YYYY-MM-DD]**: [Brief status summary]
302: 
303: ## Execution Plan
304: 
305: Tracks actual progress against the Implementation Plan in README.md. Update task status here as work progresses.
306: 
307: ### Phase 1: [Phase name]
308: - [x] Task 1.1: [description] — Completed [YYYY-MM-DD]
309: - [ ] Task 1.2: [description] — In progress, ETA [YYYY-MM-DD]
310: 
311: ### Phase 2: [Phase name]
312: - [ ] Task 2.1: [description] — Blocked by: [blocker]
313: - [ ] Task 2.2: [description] — Not started
314: 
315: ### Blockers
316: 
317: - [ ] Blocker 1 — [description, impact, mitigation]
318: - [ ] Blocker 2 — [description, impact, mitigation]
319: 
320: (Remove this section if no blockers.)
321: 
322: ## Recent Updates
323: 
324: ### [YYYY-MM-DD]
325: - Completed: [what was done]
326: - Next: [what comes next]
327: - Notes: [any relevant context]
328: 
329: ### [YYYY-MM-DD]
330: - Completed: [what was done]
331: - Next: [what comes next]
332: - Notes: [any relevant context]
333: 
334: ## Decisions Made
335: 
336: - **[YYYY-MM-DD]**: [Decision] — [Rationale]
337: - **[YYYY-MM-DD]**: [Decision] — [Rationale]
338: 
339: ## Related PRs / Commits
340: 
341: - [PR #NNN](link): [description]
342: - [Commit hash](link): [description]
343: ```
344: 
345: **Pros:**
346: - Clear separation of concerns: README.md is the immutable "contract" (what we committed to), progress.md is the mutable "journal" (what actually happened)
347: - Auditability: you can see what was promised vs. what was delivered by comparing the two files
348: - Plan stays clean and focused: not cluttered with progress updates
349: - Easier to reference just the plan without scrolling through progress history
350: - Requirements and acceptance criteria are co-located with clear traceability
351: - Implementation Plan lives in README.md (single source of truth for the plan)
352: - Execution Plan lives in progress.md (single source of truth for actual progress)
353: 
354: **Cons:**
355: - Two files to maintain — requires reading both to get the full picture
356: - More complex structure
357: - Requires discipline to keep progress.md updated (hand-maintained, not auto-generated)
358: - Agents need to read both files to understand plan + current status
359: - Implementation Plan and Execution Plan are in separate files (requires cross-referencing)
360: 
361: **Open Questions:**
362: - Not chosen — this option was not carried forward with the same scrutiny/refinement pass as Option 1, since Option 1 was selected as the Decision Outcome. Retained here for reference only.
363: - Still has the original Implementation Plan / Execution Plan split (across two files, no less), i.e. the sync-burden issue identified and resolved in Option 1 via a single Task List with inline status was never addressed here.
364: - No `history.md`-equivalent or rotation mechanism for `progress.md`'s `Recent Updates` growth.
365: - Template-location ambiguity applies here too — no separate reusable template files, only what's embedded in this ADR.
366: - To be answered later, if this option is ever revisited: same open items as Option 1 (archival/lifecycle rule, template versioning path, potential atomic status-update tooling).
367: 
368: ## More Information
369: 
370: - specmgr repository: https://github.com/anomalyco/biz.dfch.SpecMgr

(End of file - total 370 lines)
</content>
````

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/_template/v1/README.md"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/.specmgr/_template/v1/README.md</path>
<type>file</type>
<content>
1: ---
2: id: feat-NNN-slug
3: version: 1.0.0
4: status: planning
5: created: YYYY-MM-DD
6: updated: YYYY-MM-DD
7: ---
8: 
9: # Feature: [Feature Title]
10: 
11: ## Plan
12: 
13: ### Overview
14: 
15: Brief description of what this feature does and why it matters.
16: 
17: ### Requirements
18: 
19: - REQ-001: [Functional requirement]
20: - REQ-002: [Non-functional requirement]
21: - REQ-003: [Constraint or dependency]
22: 
23: ### Acceptance Criteria
24: 
25: - [ ] ACC-001: Verifies REQ-001 — [testable condition]
26: - [ ] ACC-002: Verifies REQ-002 — [testable condition]
27: - [ ] ACC-003: Verifies REQ-003 — [testable condition]
28: 
29: ### Scope
30: 
31: What is included in this feature:
32: - Item 1
33: - Item 2
34: 
35: What is explicitly out of scope:
36: - Item A
37: - Item B
38: 
39: ### Dependencies
40: 
41: - Depends on: [other feat-NNN-slug, ADR id, or external]
42: - Blocks: [other feat-NNN-slug]
43: 
44: ### Design Notes
45: 
46: Any architectural decisions, patterns, or design rationale relevant to this feature.
47: 
48: ### Related ADRs
49: 
50: - [ADR id]: [Title]
51: - [ADR id]: [Title]
52: 
53: ### Task List
54: 
55: Single, canonical breakdown of work phases and tasks. Status lives on the
56: task itself — there is no separate "planned" vs. "executed" list to keep in
57: sync; a task's line *is* its current status. Update it in place as work
58: progresses (edit, don't duplicate).
59: 
60: #### Phase 1: [Phase name]
61: - [x] Task 1.1: [description] — depends on: none — status: done (2026-08-01)
62: - [ ] Task 1.2: [description] — depends on: Task 1.1 — status: in-progress, ETA 2026-08-10
63: - [ ] Task 1.3: [description] — depends on: Task 1.2 — status: blocked (see Blockers)
64: 
65: #### Phase 2: [Phase name]
66: - [ ] Task 2.1: [description] — depends on: Task 1.3 — status: not-started
67: - [ ] Task 2.2: [description] — depends on: Task 2.1 — status: not-started
68: 
69: **Note:** If a task's scope changes mid-flight, edit its description in place;
70: rely on git history (`git log -p` on this file) to recover what was
71: originally planned, rather than keeping a second copy of the task around.
72: 
73: ## Progress
74: 
75: ### Current Status
76: 
77: **As of [YYYY-MM-DD]**: [Brief status summary]
78: 
79: ### Blockers
80: 
81: - [ ] Blocker 1 — [description, impact, mitigation]
82: - [ ] Blocker 2 — [description, impact, mitigation]
83: 
84: (Remove this section if no blockers.)
85: 
86: ### Recent Updates
87: 
88: If this section grows too long, move older entries to `history.md` in this
89: same folder and leave a pointer here, e.g.:
90: `See history.md for updates before YYYY-MM-DD.`
91: 
92: #### Update [YYYY-MM-DDTHH:mm:ssz] (newest)
93: - Completed: [what was done]
94: - Next: [what comes next]
95: - Notes: [any relevant context]
96: 
97: #### Update [YYYY-MM-DDTHH:mm:ssz] (oldest)
98: - Completed: [what was done]
99: - Next: [what comes next]
100: - Notes: [any relevant context]
101: 
102: ### Decisions Made
103: 
104: - **[YYYY-MM-DD]**: [Decision] — [Rationale]
105: - **[YYYY-MM-DD]**: [Decision] — [Rationale]
106: 
107: ### Related PRs / Commits
108: 
109: - [PR #NNN](link): [description]
110: - [Commit hash](link): [description]

(End of file - total 110 lines)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/conventions.md"
}
```

**Output:**

````
<path>/home/user/src/biz.dfch.SpecMgr/.specmgr/conventions.md</path>
<type>file</type>
<content>
1: # Specification: SpecMgr Coding Conventions
2: 
3: This document defines the general coding requirements and conventions used throughout the SpecMgr project.
4: 
5: ## Python Version and Types
6: 
7: **Requirement:** Use Python 3.11+ and modern Python type notation.
8: 
9: - Python version: 3.11 and later
10: - Prefer built-in types over typing module aliases:
11:   - Use `str` instead of `Str`
12:   - Use `list` instead of `List`
13:   - Use `dict` instead of `Dict`
14:   - Use `bool` instead of `Bool`
15:   - Use `tuple` instead of `Tuple`
16:   - Use `set` instead of `Set`
17:   - Use `bytes` instead of `Bytes`
18:   - Use `int`, `float`, etc. directly over `Integer`, `Float`, etc.
19: 
20: **Example:**
21: ```python
22: # ✓ Modern Python (3.11+)
23: def process_items(items: list[str], filter_enabled: bool = True) -> str | None:
24:     if filter_enabled:
25:         result = [item.upper() for item in items]
26:     else:
27:         result = items.copy()
28:     return result
29: ```
30: 
31: ## Assert Statements
32: 
33: **Rule 1:** Always use `assert` to validate all input parameters in public methods and functions.
34: 
35: **Rule 2:** Use assert statements for input parameter validation, preconditions, and program invariants only.
36: 
37: **Rule 3:** Do not use assert for user-controlled flow control; use it only for program invariants and input validation.
38: 
39: **Example:**
40: ```python
41: def calculate_discount(value: str, price: float, discount_rate: float) -> float:
42: 
43:     assert isinstance(value, str), type(value)
44:     assert value.strip()
45:     assert isinstance(price, float), type(price)
46:     assert 0 <= price, price
47: 
48:     discount_rate = 0.05
49: 
50:     result = price * (1 - discount_rate)
51: 
52:     return result
53: ```
54: 
55: **Best Practices:**
56: - Define numeric and string constants for thresholds, minimums, maximums, and standard states
57: - Place constants at module level with clear documentation
58: - Use constants in assert statements to make conditions self-documenting and maintainable
59: 
60: ## Variable Naming Convention
61: 
62: **Requirement:** When a function or method returns a value, use the variable name "result" in the function body.
63: 
64: - Use `result: Type = value` pattern for return values
65: - Only use different variable names for special cases where the name is more descriptive
66: - Follow this convention consistently for all return value assignments
67: 
68: **Example:**
69: 
70: ```python
71: def get_status() -> str:
72:     result = "active"
73:     return result
74: 
75: 
76: def calculate_total(items: list[str]) -> int:
77:     result = 0
78:     for item in items:
79:         result += len(item)
80:     return result
81: ```
82: 
83: ## Comparison Constants
84: 
85: **Requirement:** Use named constants for values used in comparisons (lvalue-side constants).
86: 
87: - When comparing variables against string literals or values used as a standard for comparison, define those values as constants
88: - This improves readability and makes it easier to update the comparison value later
89: - Apply this pattern to all equality checks (`==`, `!=`, `is`, `is not`), inequality checks (`<`, `>`, `<=`, `>=`), and membership checks (`in`, `not in`)
90: 
91: **Example:**
92: ```python
93: # ✓ Use constant for comparison value
94: VALID_STATUS = "active"
95: user_status = "inactive"
96: if user_status == VALID_STATUS:
97:     print("Status is valid")
98: 
99: # ✓ Use constant for threshold comparison
100: MAX_RETRY_ATTEMPTS = 3
101: attempt = 5
102: if attempt >= MAX_RETRY_ATTEMPTS:
103:     raise RuntimeError("Max attempts exceeded")
104: 
105: # ✓ Use constant for membership checks
106: ALLOWED_FILE_EXT = {".md", ".txt", ".py"}
107: filename = "document.md"
108: if filename.endswith(tuple(ALLOWED_FILE_EXT)):
109:     print("File type is allowed")
110: 
111: # ✗ Avoid inline string values in comparisons
112: # if user_status == "active":  # Hard to maintain
113: #     print("Status is valid")
114: ```
115: 
116: **Best Practices:**
117: - Place constants at the top of the module or in a dedicated configuration section
118: - Use `ALL_CAPS` naming convention for constants to distinguish them from variables
119: - Group related constants together for easy maintenance
120: - Document the purpose and allowed values of each constant
121: 
122: **Example Module-Level Constants:**
123: ```python
124: # Constants for string comparisons
125: DEFAULT_ENCODING = "utf-8"
126: INDENTATION = "    "
127: 
128: # Constants for numeric comparisons
129: MIN_USER_ID = 1
130: MAX_BATCH_SIZE = 1000
131: 
132: # Constants for status checks
133: STATUS_ACTIVE = "active"
134: STATUS_INACTIVE = "inactive"
135: STATUS_PENDING = "pending"
136: ```
137: 
138: ## Type Hints
139: 
140: **Requirement:** Always use type hints for all function signatures, parameters, and variables.
141: 
142: - Type hints are mandatory for:
143:   - Function and method parameters
144:   - Return types
145:   - Variables that are assigned specific types in functions/methods
146:   - Variables outside functions when they are not inferred from context
147: 
148: **Example:**
149: ```python
150: def load_config(filename: str) -> dict[str, str]:
151:     content: str = ""
152: 
153:     with open(filename, "r", encoding="utf-8") as f:
154:         content = f.read()
155: 
156:     result: dict[str, str] = {}
157:     for line in content.split("\n"):
158:         if ":" in line:
159:             key, value = line.split(":", 1)
160:             result[key.strip()] = value.strip()
161: 
162:     return result
163: ```
164: 
165: ## Documentation Requirements
166: 
167: **Requirement:** Include docstrings for classes, their attributes, and method/function parameters/returns.
168: 
169: - Classes: Document purpose and behavior in class docstrings
170: - Attributes: Document class attributes using inline comments
171: - Functions/methods: Document parameters and return types
172: - Maintain formal, concise documentation; avoid obvious statements
173: 
174: **Example:**
175: ```python
176: class DataProcessor:
177:     """Process and validate data entries.
178: 
179:     Attributes:
180:         max_items: Maximum number of items allowed per batch.
181:     """
182: 
183:     max_items: int = 100
184: 
185:     def __init__(self, max_items: int) -> None:
186:         """Initialize the processor.
187: 
188:         Args:
189:             max_items: Maximum batch size.
190:         """
191:         self.max_items = max_items
192: 
193:     def process(self, items: list[str]) -> str:
194:         """Process a batch of items.
195: 
196:         Args:
197:             items: List of items to process.
198: 
199:         Returns:
200:             Summary string of processed items.
201:         """
202:         assert len(items) > 0
203:         result = f"Processed {len(items)} items"
204:         return result
205: ```
206: 
207: ## Additional Best Practices
208: 
209: ### Import Organization
210: 
211: ```python
212: # Standard library imports
213: import os
214: from pathlib import Path
215: 
216: # Third-party imports
217: from pydantic import BaseModel
218: 
219: # Local imports
220: from biz.dfch.specmgr.models import Adr
221: ```
222: 
223: ### Docstring Style
224: 
225: ```python
226: def process_data(data: list[str]) -> str:
227:     """
228:     Process a list of strings and return a summary.
229: 
230:     Args:
231:         data: The list of strings to process.
232: 
233:     Returns:
234:         A summary string of the processed data.
235: 
236:     Example:
237:         >>> process_data(["hello", "world"])
238:         "Processed 2 items"
239:     """
240:     assert len(data) > 0, "Data list cannot be empty"
241:     result = "Processed items"
242:     return result
243: ```
244: 
245: ### Error Handling
246: 
247: ```python
248: from pathlib import Path
249: 
250: 
251: def load_file(path: str) -> str:
252:     """Load content from a file.
253: 
254:     Args:
255:         path: Path to the file to load.
256: 
257:     Returns:
258:         File content as a string.
259: 
260:     Raises:
261:         FileNotFoundError: If the file doesn't exist.
262:         UnicodeDecodeError: If the file cannot be decoded.
263:     """
264:     file_path = Path(path)
265:     result = file_path.read_text(encoding="utf-8")
266:     return result
267: ```
268: 
269: ### Test Framework
270: 
271: **Requirement:** Use `unittest` for all test cases and follow a consistent structure.
272: 
273: -[ ] All tests must use the `unittest` framework, not `pytest`
274: -[ ] Tests must be in the `tests/` directory and have the same hierarchy as the source structure
275: -[ ] Test file names start with `test_`
276: -[ ] Test classes inherit from `unittest.TestCase`
277: -[ ] Test class names start with `Test`
278: -[ ] Test methods start with `test_`
279: -[ ] Use descriptive names that show what the test does and under what conditions
280: -[ ] Do not use docstrings for test methods
281: -[ ] Tests have one *subject under test*. The subject variable name is `sut`. 
282: -[ ] Tests have a clear *arrange*-*act*-*assert* (AAA) structure
283: -[ ] Place shared test fixtures in `fixtures` directory
284: -[ ] Avoid complex setup/teardown; prefer simple, isolated tests
285: -[ ] Use `setUp()` and `tearDown()` methods for test initialization and cleanup
286: -[ ] Mock external dependencies using `unittest.mock`
287: 
288: **Examples**:
289: 
290: ```python
291: . <project-root>
292: + src
293:     + project
294:       + domainA
295:         + moduleA1
296:           : class Calculator
297: + tests
298:     + project
299:       + domainA
300:         + moduleA1
301:           - Test_Calculator.py
302:             : test_divide_by_zero_fails
303:             : test_divide_by_int_returns_float
304:             : test_add_int_and_float_succeeds
305: ```
306: 
307: ```python
308: # test_Calculator.py
309: class TestCalculator(unittest.TestCase):
310:     def test_add_int_float_succeeds() -> None:
311:         expected = 42.0
312:         addend: int = 5
313:         summand: float = 37.0
314: 
315:         sut = Calculator()
316: 
317:         result = sut.add(addend, summand)
318: 
319:         self.assertEqual(result, expected)
320: 
321:     def test_divide_by_zero_fails() -> None: ...
322: ```
323: 
324: 
325: ## TODO
326: 
327: * Use "uv", do not use "pip"
328: * Use "setuptools", do not use "hatchling"
329: 
330: ## Rationale
331: 
332: These conventions were chosen to:
333: 
334: 1. **Simplicity:** Modern Python types are more intuitive than typing aliases
335: 2. **Clarity:** Assert statements provide clear preconditions and invariants
336: 3. **Consistency:** `result` variable name makes return values obvious
337: 4. **Type Safety:** Mandatory type hints ensure code is self-documenting and catch type errors early
338: 5. **Readability:** Followed conventions make the codebase easier to understand and maintain
339: 
340: ## Changelog
341: 
342: - **2026-08-06:** Initial version created
343: - **2026-08-06:** Added Python 3.11+ type requirements
344: - **2026-08-06:** Added assert statement requirement
345: - **2026-08-06:** Added variable naming convention requirement
346: - **2026-08-06:** Added mandatory type hints requirement
347: - **2026-08-06:** Added documentation requirements with reference to AGENTS.md
348: - **2026-08-06:** Added test framework conventions
349: - **2026-08-06:** Added test file organization guidelines
350: - **2026-08-06:** Added test method naming conventions
351: - **2026-08-06:** Added test data and fixtures guidelines

(End of file - total 351 lines)
</content>
````

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 81.1s)

_Thinking:_

OK so, let me look at recent feature READMEs that include phases, and align with how phases are actually being used (e.g., feat-18-goal, feat-15-add-artifact-type-risk). This will tell me the granularity of the phases and how the "complete test cycle per phase" is expressed. Also, let me check the definitions of the phase-orchestrator / phase-implementer agents — the phase-implementer is described as follows: "Implement exactly one phase of the `.specmgr/feat/<id>/README.md` plan end-to-end — code, tests, phase-end quality gate, updating the plan's Progress section — then stop and report. Driven by the phase-orchestrator. Not intended to be selected directly."

So the README's Task List needs phases, and each phase has to be self-contained with a quality gate (tests). The phase-implementer implements "code, tests, phase-end quality gate, updating the plan's Progress section."

Let me read the README of feat-18-goal (the most recent feature) and check the phase structure.

Now let me see how recent features structure their phases, to match the convention the Phase-Implementer agent expects.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-18-goal/README.md"
}
```

**Output:**

````
<path>/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-18-goal/README.md</path>
<type>file</type>
<content>
1: ---
2: created: 2026-08-25
3: id: feat-18-goal
4: status: done
5: updated: 2026-08-26
6: version: 1.0.0
7: ---
8: 
9: # Feature: Add artifact type Goal (gol)
10: 
11: ## Plan
12: 
13: ### Overview
14: 
15: Add a new markdown artifact type, `Goal` (abbreviation `gol`), for capturing
16: high-level business goals — the strategic "what the organization wants to
17: achieve" level that sits above individual requirements. `gol` follows the
18: domain-first hierarchy and MCP surface already established by `req`/`prb`
19: (ADR ece4554b-725c-4f76-bc04-5d2b760363d2) and mirrors `req`'s body schema
20: with exactly two deliberate omissions: no `## Characteristics` section (ISO
21: 25010:2023 quality characteristics are a requirement-level attribute — a
22: business goal stays deliberately free of them) and no `## Level` section
23: (RFC 2119 obligation strength is implicit — a goal is always a MUST). `req`
24: already anticipates this artifact type: its `## Related Artifacts` →
25: `### Goals` cross-reference sub-list (exercised in `req_example.md` as
26: `GOL-0007: Competitive Engines in Consumer Vehicles`) points at documents
27: of exactly this shape, and `gol_example.md` will be that very goal so the
28: two packaged examples read coherently side by side. `gol` reuses `req`'s
29: whole-body update convention (not ADR's granular `update_section`
30: mechanism) and `req`'s 7-value frontmatter status set.
31: 
32: ### Requirements
33: 
34: - REQ-001: Define the `gol` markdown schema — frontmatter (`type="gol"`,
35:   7-value status set `draft`/`proposed`/`accepted`/`superseded`/
36:   `deprecated`/`rejected`/`implemented`, `req`'s exact set) and body (H1
37:   title, mandatory `statement` lead paragraph, optional `## Description`,
38:   optional `## Priority`, optional `## Tags`, mandatory `## Source`,
39:   optional `## Related Artifacts` holding four optional, fixed-heading
40:   `### ` cross-reference sub-lists — `Requirements`/`Decisions`/`Goals`/
41:   `Acceptance Criteria` — optional `## More Information`, optional
42:   `## Notes`). No `## Characteristics` and no `## Level` (see Design
43:   Notes).
44: - REQ-002: Pydantic models under `gol/models/v1/` (frontmatter, body,
45:   document, parser, summary), domain-first, mirroring `req`/`prb`'s exact
46:   file shapes. No `models/md` engine changes are needed — every field is
47:   buildable with the existing declarative heading-mapped parser.
48: - REQ-003: Parse/validate `gol` documents from markdown, mirroring
49:   `parse_req`/`parse_prb`'s two-error-channel convention
50:   (`AssertionError` for structural problems, `pydantic.ValidationError`
51:   for field-level problems).
52: - REQ-004: MCP tools mirroring REQ/PRB's lifecycle surface, **plus**
53:   `list_gol` as a paged tool from day one (per ADR
54:   ec9f5262-9912-49d0-903f-fcfb54f28c13 — new domains must not add a
55:   `specmgr://gol/list` resource and convert it later): `parse_gol`,
56:   `create_gol`, `update_gol`, `set_status_gol`, `delete_gol` (stub),
57:   `validate_gol`, `get_gol`, `get_gol_example`, `get_gol_template`,
58:   `list_gol`.
59: - REQ-005: MCP resources: `specmgr://gol/schema`, `/example`, `/template`
60:   (no `/list` — REQ-004 covers listing as a tool; no `/{id}` — id-based
61:   reads are `get_gol`-only, per ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614).
62: - REQ-006: MCP prompts `create_gol`/`update_gol` — narrated,
63:   `TodoWrite` + `question`-tool-driven interview flows reusing the
64:   dedup-check-first pattern from `req/prompts/create_req.py` and the
65:   `TodoWrite`/`question`-tool narration pattern from
66:   `tsk/prompts/implement_task.py`/`prb/prompts/create_prb.py`. Both use
67:   their own packaged instructions data file (`gol_create_instructions.md`/
68:   `gol_update_instructions.md` under `gol/data/`), not an inline string.
69: - REQ-007: Packaged example/template/schema data (`gol/data/`) via the
70:   existing generic `general/tools/_packaged_data.py`, with the matching
71:   `pyproject.toml` package-data entry, pre-commit hook, and CI step.
72: - REQ-008: Doc generation wiring — `specmgr docs`, `specmgr schema` (new
73:   `gol` entry in the doc-type registry, `commands/schema.py`),
74:   `specmgr mcp-docs`, all kept drift-free via pre-commit/CI; `AGENTS.md`
75:   updated to eight domain/cross-cutting packages.
76: 
77: ### Acceptance Criteria
78: 
79: - [x] ACC-001: Verifies REQ-001 — schema documented (`docs/gol_schema.json`,
80:   `specmgr://gol/schema`); a reference `gol_reference.md` exercising every
81:   field (`statement`, `Source` plus all optional sections present,
82:   `Related Artifacts` with all four sub-lists) round-trips through the
83:   parser. **PASS** — `docs/gol_schema.json` exists with `"$comment": "v1"`
84:   (line 2) and `"$schema": "https://json-schema.org/draft/2020-12/schema"`
85:   (line 403); `specmgr://gol/schema` is registered — live
86:   `asyncio.run(mcp.list_resources())` on the real `server.mcp` instance
87:   returns it among exactly 3 gol resources, and `docs/MCP.md` carries it
88:   (resource table line 20, detail section line 49). Live round-trip:
89:   `uv run --frozen python` reads
90:   `.specmgr/feat/feat-18-goal/gol_reference.md`, calls `parse_gol`, and
91:   asserts `str(doc.body)` equals the file's body (frontmatter stripped,
92:   `format_text`-normalized) byte-exact — 2030 == 2030 bytes (id
93:   `deaddead-goal-goal-goal-deaddeadgoal`, status `accepted`); the committed
94:   test `tests/gol/models/v1/test_parser.py` (10 tests, incl.
95:   `test_parses_full_reference_document`'s own byte-exact assertion) re-run
96:   live: OK.
97: - [x] ACC-002: Verifies REQ-002 — Pydantic models validate mandatory
98:   (`statement`, `Source`) vs. optional (`Description`, `Priority`, `Tags`,
99:   `Related Artifacts` and each of its four sub-lists, `More Information`,
100:   `Notes`) fields correctly; `GolFrontmatter.status` rejects any value
101:   outside the seven-value set. **PASS** —
102:   `tests/gol/models/v1/test_frontmatter.py` + `test_body.py` re-run live:
103:   41 tests OK (each optional section and each of the four `Related
104:   Artifacts` sub-lists covered individually absent/present); a live minimal
105:   doc (H1 + statement + `## Source`, zero optional sections) parses with
106:   all six optional fields `None` (`description`/`priority`/`tags`/
107:   `related_artifacts`/`more_information`/`notes`);
108:   `GolFrontmatter(status="pending")` raises `pydantic.ValidationError`
109:   naming the seven allowed values — "status must be one of ['accepted',
110:   'deprecated', 'draft', 'implemented', 'proposed', 'rejected',
111:   'superseded'], got 'pending'" — and the same at parse level for a
112:   `status: pending` frontmatter block (loc `('status',)`).
113: - [x] ACC-003: Verifies REQ-003 — parser produces a valid object tree for a
114:   well-formed document; missing the `statement` lead paragraph or the
115:   `Source` section raises `AssertionError`; an invalid field value (e.g. a
116:   `Priority` outside 0–99, an out-of-set `status`) raises
117:   `pydantic.ValidationError`. **PASS** —
118:   `tests/gol/models/v1/test_parser.py` re-run live: 10 tests OK, with the
119:   `AssertionError` tests (`test_missing_statement_raises_assertion_error`,
120:   `test_missing_source_raises_assertion_error`,
121:   `test_out_of_order_sections_raise_assertion_error`) and the
122:   `ValidationError` tests (`test_invalid_status_raises_validation_error`,
123:   `test_invalid_type_raises_validation_error`,
124:   `test_priority_out_of_range_raises_validation_error` over 100/-1/007,
125:   plus `test_priority_upper_bound_is_accepted` for 99) all green; live
126:   demos: a doc without `## Source` raises `AssertionError` ("Goal.source:
127:   expected Source, found no match; remaining text (0 line(s)) starts
128:   with:") and `## Priority` value `100` raises
129:   `pydantic.ValidationError` (loc `('value',)`, "value must match pattern
130:   '^(0|[1-9][0-9]?)$', got '100'").
131: - [x] ACC-004: Verifies REQ-004 — every listed tool is implemented,
132:   registered, and callable; `list_gol` returns a `PagedResult[GolSummary]`
133:   with default page size 25 / cap 100, mirroring the other five domains'
134:   `list_<d>` tools exactly (no resource-first-then-converted history for
135:   this domain). **PASS** — `docs/MCP.md` carries all 10 `### Tool:` gol
136:   entries (`create_gol`, `delete_gol`, `get_gol`, `get_gol_example`,
137:   `get_gol_template`, `list_gol`, `parse_gol`, `set_status_gol`,
138:   `update_gol`, `validate_gol`) under the header line 6: `20 resource(s), 1
139:   resource template(s), 74 tool(s), 17 prompt(s)`; live
140:   `asyncio.run(mcp.list_tools()/list_resources()/list_prompts())` on the
141:   real `server.mcp` instance confirms the 74/20/17 totals with exactly
142:   those 10 gol tools present; `tests/gol/tools/test_list_gol.py` re-run
143:   live: 11 tests OK (default page size with 26 docs, `max_results` clamped
144:   to the 100 cap, `offset` paging without overlap, `truncated` boundary
145:   incl. offset exactly at the end, negative-offset flooring,
146:   skip-malformed-file); live paging in a temp `SPECMGR_DOCS_DIR` with 26
147:   `create_gol`-ed docs: `list_gol()` → total=26, max_results=25,
148:   truncated=True, 25 items; `list_gol(max_results=100)` → 26 items,
149:   truncated=False; `list_gol(offset=25)` → 1 item, truncated=False.
150: - [x] ACC-005: Verifies REQ-005 — every listed resource is implemented and
151:   registered (no `/{id}`, no `/list`, as designed). **PASS** — `docs/MCP.md`
152:   carries exactly three `specmgr://gol/...` rows (`/example` line 19,
153:   `/schema` line 20, `/template` line 21; detail sections lines 40–56), and
154:   a grep of both `docs/MCP.md` and `src/biz/dfch/specmgr/gol/resources/`
155:   finds no `specmgr://gol/{id}`-style dynamic resource and no
156:   `specmgr://gol/list` (the package holds exactly `gol_example.py`,
157:   `gol_schema.py`, `gol_template.py`, one `@mcp.resource()` each); live:
158:   `gol_schema()` returns the parsed dict (`$comment` `v1`, 2020-12
159:   `$schema`, top-level `required: ['frontmatter', 'body']`),
160:   `gol_example()` 2162 chars, `gol_template()` 1201 chars;
161:   `tests/gol/resources/` re-run live: 13 tests OK.
162: - [x] ACC-006: Verifies REQ-006 — `create_gol`/`update_gol` prompts narrate:
163:   (a) a duplicate/similar-document check via `list_gol` first, (b) building
164:   a `TodoWrite` list covering `statement` + `Source` + each optional
165:   section, (c) using the `question` tool to elicit each field (explicitly
166:   allowing skip for optional ones), (d) calling `create_gol(content)`/
167:   `update_gol(id, content)` (whole-body) at the end — verified live by
168:   reading both packaged instruction files in full and manually walking the
169:   narrated flows end to end against a real document, not just asserting
170:   their static text. **PASS** — both instruction files read in full, step
171:   headers quoted: `gol_create_instructions.md` — `## 0. Check for an
172:   existing goal on this topic first` (`list_gol` dedup check,
173:   `question`-tool follow-up on a near-duplicate), `## 1. Structure recap`
174:   (incl. the explicit no-`Characteristics`/no-`Level` note), `## 2. Build a
175:   todo list, then gather the information one at a time` (TodoWrite per
176:   `statement` + `Source` + each optional section; `question`-tool
177:   interview, mandatory fields first, explicit skip allowance), `## 3. Use
178:   the template/example/schema as references`, `## 4. Tool call sequence`
179:   (`create_gol(content)`, optional `validate_gol` dry-run), `## 5. Later
180:   revisions`; `gol_update_instructions.md` — `## 1. Read current state
181:   first` (`get_gol(id)`, never assume prior state), `## 2. Show which
182:   sections are present and which are empty`, `## 3. Elicit the
183:   new/revised text`, `## 4. Map the requested change to the right tool`
184:   (whole-body `update_gol(id, content)` carrying forward every unchanged
185:   section; `set_status_gol` as a separate, optional follow-up naming the
186:   7-value set), `## 5. Check the schema, and validate before writing if
187:   useful`. Then the narrated flows were walked end to end against a real
188:   document in a temp `SPECMGR_DOCS_DIR` (self-simulated `question`-tool
189:   answers): `list_gol()` empty → no near-duplicate; `create_gol(content)`
190:   (statement + `Source` + one optional `## Description`) → id
191:   `07331e39-993d-4c17-b6b6-35bd83f11dab`, status `draft`; `get_gol(id)`;
192:   `update_gol(id, content)` adding the absent `## Notes` while carrying
193:   forward every unchanged section (id/status/created preserved, `updated`
194:   bumped); `set_status_gol(id, "accepted")`; final `get_gol(id)`/
195:   `list_gol()` show status `accepted`. Both prompt functions also resolved
196:   their packaged narration live (`$topic`/`$id` substituted: 3554 / 2567
197:   chars). `tests/gol/prompts/` re-run live: 22 tests OK;
198:   `tests/gol/tools/test_integration.py` re-run live: 2 tests OK (full
199:   create→update→set_status→get→list→delete(stub) lifecycle, the stub
200:   raising `NotImplementedError` without touching the file).
201: - [x] ACC-007: Verifies REQ-007 — packaged data resolves correctly from a
202:   real, non-editable install (`uv build --wheel` + scratch-venv install),
203:   mirroring feat-16's ACC-007 verification. **PASS** — `uv build --wheel`
204:   produced `dist/biz_dfch_specmgr-0.10.0-py3-none-any.whl`; `unzip -l`
205:   confirms all five `gol/data/*` files (`gol_example.md`, `gol_schema.json`,
206:   `gol_template.md`, `gol_create_instructions.md`,
207:   `gol_update_instructions.md`) plus every gol module (35 wheel entries
208:   under `biz/dfch/specmgr/gol/`); installed non-editably with the mcp extra
209:   into a scratch venv under `/tmp/opencode/` (`uv venv --python 3.13` +
210:   `uv pip install "…whl[mcp]"` — the system `python3` is 3.10, below the
211:   project's `>=3.11` floor, so `uv`'s managed CPython 3.13.13 was used); in
212:   that venv, `inspect.getfile` proves the module loads from
213:   `…/gol-scratch-venv/lib/python3.13/site-packages/biz/dfch/specmgr/gol/…`,
214:   not the source checkout, and `get_gol_example()` (2162 chars),
215:   `get_gol_template()` (1201 chars), and `gol_schema()` (`$comment` `v1`,
216:   2020-12 dialect, `title` `GolDocument`) all resolve real packaged
217:   content. Scratch venv and `dist/`/`build/` removed afterward; `git
218:   status` shows no residue (both gitignored).
219: - [x] ACC-008: Verifies REQ-008 — `specmgr docs`/`specmgr schema`/
220:   `specmgr mcp-docs` all report no drift after implementation; `AGENTS.md`
221:   reflects eight domain/cross-cutting packages. **PASS** — re-run end to
222:   end in Phase 5: `specmgr docs` (exit 0), `specmgr mcp-docs` (exit 0),
223:   `specmgr schema` (exit 0, all six doc types "unchanged"), `specmgr schema
224:   --type gol --output-dir src/biz/dfch/specmgr/gol/data` (exit 0, packaged
225:   copy "unchanged"), `specmgr adr-toc` (exit 0), `specmgr coverage-badge`
226:   (exit 0, 98%, `docs/coverage.svg` unchanged); `git diff --exit-code --
227:   docs/` exits 0 — zero drift on disk, and `docs/GENERATED.md`'s test-file
228:   count is unchanged (Phase 5 adds no test files). `AGENTS.md` line 5
229:   reads `## Status: eight domain/cross-cutting packages implemented (ADR,
230:   REQ, UC, TSK, QA, PRB, GOL, general)` with the `gol/` bullet at line 81
231:   (Phase 4 work).
232: 
233: ### Scope
234: 
235: **Included in this feature:**
236: 
237: - The `gol` markdown schema, Pydantic models, parser, and summary under
238:   `gol/models/v1/`.
239: - Full MCP surface (tools/resources/prompts/packaged data), including
240:   `list_gol` as a tool (not a resource) from the start.
241: - The interactive `create_gol`/`update_gol` prompt behavior (`TodoWrite` +
242:   `question`-tool-driven interview).
243: - Tests mirroring `tests/req/`/`tests/prb/`'s layout and coverage depth.
244: - Cross-cutting registration (`server.py`, `pyproject.toml`,
245:   `.pre-commit-config.yaml`, CI, `commands/schema.py`, `AGENTS.md`).
246: 
247: **Explicitly out of scope:**
248: 
249: - A `## Characteristics` section (ISO 25010:2023 quality attributes).
250:   Quality characteristics are a requirement-level attribute — a business
251:   goal states *what* to achieve, not *which quality dimension* it loads
252:   (user decision, planning session 2026-08-25).
253: - A `## Level` section (RFC 2119 obligation strength). A goal is
254:   implicitly always a MUST — obligation grading applies to requirements
255:   below it, not to the goal itself (user decision, planning session
256:   2026-08-25).
257: - Structured cross-referencing/validation of the `Related Artifacts`
258:   sub-lists (typed id validation, `GOL-NNNN:`-style format checks,
259:   existence checks against the other domains' base directories) — v1 keeps
260:   all four sub-lists as opaque free text, matching `req`'s own precedent.
261:   Revisit only if a concrete need emerges.
262: - ADR-style granular `update_section`/option-style per-field mutation
263:   tools — `update_gol` is a single whole-body replace tool, like
264:   `update_req`/`update_prb`. Individual sections stay addressable by their
265:   fixed heading text within the markdown body itself, not via a dedicated
266:   tool per section.
267: - Real implementation of `delete_gol` — a stub raising
268:   `NotImplementedError`, matching the other five domains' `delete_*` stubs
269:   (a shared, cross-domain decision deferred to future work).
270: - Any changes to `req`'s schema, data, or tools — REQ's existing
271:   `### Goals` cross-reference sub-list already anticipates this artifact
272:   type and needs no modification.
273: - A `specmgr gol-toc`-equivalent generation command or dedicated CI/
274:   pre-commit drift check beyond what `specmgr docs`/`specmgr mcp-docs`/
275:   `specmgr schema` already provide generically.
276: 
277: ### Dependencies
278: 
279: - Depends on: ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first
280:   hierarchy), ADR bc5e18ad-6bbf-4265-bae4-3e34984a2d29 (generic
281:   `MarkdownFrontmatter` base), ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614
282:   (tool-only id-based reads, no `specmgr://gol/{id}` resource), ADR
283:   ec9f5262-9912-49d0-903f-fcfb54f28c13 (`list_<domain>` as a paged tool,
284:   not a resource — `list_gol` must follow this from day one), the existing
285:   `general/tools/_doc_paths.py`/`_packaged_data.py`/`_paging.py` and
286:   `general/models/{DocSummary,PagedResult}` infrastructure, and the
287:   existing `models/md` engine (`MarkdownSection1`, `MarkdownSection2`,
288:   `MarkdownSection2WithComment`, `MarkdownSection3`, `MarkdownParagraph`,
289:   `MarkdownListItem`, `@alias`) — reused as-is, no engine changes
290:   anticipated.
291: - Blocks: None identified yet.
292: - Related, but explicitly out of scope here: issue #15 "Add artifact type
293:   Risk" (open) — a sibling domain that will follow the same pattern
294:   independently.
295: 
296: ### Design Notes
297: 
298: **Schema:**
299: 
300: ```
301: GolFrontmatter(MarkdownFrontmatter): type: Literal["gol"];
302:   status in {draft, proposed, accepted, superseded, deprecated, rejected, implemented}
303:   (req's exact 7-value set -- goals are business-level requirements, so
304:    requirement-lifecycle semantics apply)
305: 
306: Goal(MarkdownSection1)                          # H1, free-form title (@alias ".+" REGEX)
307: ├── statement: MarkdownParagraph                # mandatory lead paragraph (the goal statement itself)
308: ├── description: Description | None             # optional H2 "Description", opaque free text leaf
309: ├── priority: Priority | None                   # optional H2 "Priority", 0-99 single-line value + optional comment
310: ├── tags: Tags | None                           # optional H2 "Tags", bullet list
311: ├── source: Source                              # mandatory H2 "Source", single-line value
312: ├── related_artifacts: RelatedArtifacts | None  # optional H2 "Related Artifacts"
313: │   ├── requirements: Requirements | None       # optional H3, bullet list of cross-refs (e.g. "REQ-9687: ...")
314: │   ├── decisions: Decisions | None             # optional H3, bullet list of cross-refs (e.g. "DEC-2703: ...")
315: │   ├── goals: Goals | None                     # optional H3, bullet list of cross-refs (e.g. "GOL-0007: ...")
316: │   └── acceptance_criteria: AcceptanceCriteria | None  # optional H3, bullet list (e.g. "ACC-1234: ...")
317: ├── more_information: MoreInformation | None    # optional H2 "More Information", opaque free text leaf
318: └── notes: Notes | None                         # optional H2 "Notes", opaque free text leaf
319: ```
320: 
321: **No `Characteristics`, no `Level`** (see Scope: Explicitly out of scope) —
322: both are deliberate, domain-driven omissions, not oversights: ISO 25010
323: quality characteristics grade *requirements*, and RFC 2119 obligation
324: strength is implicit (a goal is always a MUST). Consequently the only
325: mandatory body fields are `statement` and `Source`; a freshly created
326: `gol` document may have zero optional sections yet (all deferred to a later
327: `update_gol` call) but must always carry the goal statement and its source.
328: 
329: **`Priority` keeps `req`'s `MarkdownSection2WithComment` +
330: `field_validator`-on-`value.text` pattern** (0–99, no leading zeros other
331: than "0" itself), re-declared in `gol/models/v1/body.py` — domain packages
332: never import model classes from each other (verified: no cross-domain
333: imports exist in `src/`), so `req`'s `Priority`/`Level` classes are
334: *pattern* precedents, not shared code. `Description`/`Source`/
335: `MoreInformation`/`Notes` are bare opaque leaf subclasses with no further
336: declared fields — the same pattern verified for REQ's `MoreInformation`/
337: `Notes` and PRB's leaves.
338: 
339: **The four `RelatedArtifacts` sub-lists are 1:1 re-declarations of REQ's
340: own four classes**: `MarkdownSection3` with
341: `items: list[MarkdownListItem] = Field(min_length=1)`; heading text
342: ("Requirements"/"Decisions"/"Goals"/"Acceptance Criteria") derives
343: implicitly via the `AliasType.SPACE_SEPARATED` convention (multi-word
344: `AcceptanceCriteria` → "Acceptance Criteria"), so no explicit `@alias` is
345: needed — exactly as in `req/models/v1/body.py`. All four sub-lists are
346: optional, as is `Related Artifacts` as a whole, and no consistency check
347: is enforced between them (REQ precedent). Cross-reference id formats
348: (`GOL-0007:`, `REQ-9687:`, `DEC-2703:`, `ACC-1234:`) are conventional text
349: only — not validated in v1. The `### Goals` sub-list includes goals for
350: cross-referencing peer/superseding goals (self-referencing is allowed; the
351: parser does not special-case a document's own id).
352: 
353: **Update mechanism: whole-body `update_gol(id, content)`**, not an
354: ADR-style `update_section`. The generic `adr/tools/update_section.py`
355: mechanism (ADR 71fd95d7-07f2-466f-81aa-d29b7e3ef34c) is currently
356: ADR-specific code, not a shared cross-domain component — the same decision
357: as feat-16's for `prb`. Individual sections stay addressable by grepping/
358: editing their fixed heading text within the whole-body markdown.
359: 
360: **`list_gol` is a paged tool from day one** (`@mcp.tool(name="list_gol")`
361: returning `PagedResult[GolSummary]`, via `general/tools/_paging.py`'s
362: `paginate`/`normalize_paging`, default page size 25 / cap 100), not a
363: `specmgr://gol/list` resource — GOL is a new domain built *after* ADR
364: ec9f5262 was accepted, so it must not repeat the resource-then-convert
365: history of REQ/UC/TSK/QA/PRB (feat-13). `GolSummary` subclasses
366: `general/models/summary.py::DocSummary` (`id`/`title`/`status`/`ref`),
367: like `ReqSummary`/`PrbSummary`; `title` is the body's H1 text.
368: 
369: **Prompts are narrated instructions only** (return a string, auto-wrapped
370: as a `UserMessage` by the MCP SDK) — `create_gol`/`update_gol` never call
371: `TodoWrite`/`question`/`get_gol`/`create_gol`/`update_gol` themselves; they
372: only narrate that the calling LLM should. This is the same contract every
373: existing prompt in this codebase already follows
374: (`tsk/prompts/implement_task.py`, `req/prompts/create_req.py`).
375: 
376: - `create_gol(topic: str) -> str`: instructs the LLM to (1) call `list_gol`
377:   first to check for an existing, similar goal (mirrors `create_req`'s
378:   dedup-check pattern) and ask the user via `question` if a near-duplicate
379:   is found; (2) build a `TodoWrite` list with one entry per `statement` +
380:   `Source` + each optional section (`Description`/`Priority`/`Tags`/
381:   `Related Artifacts`/`More Information`/`Notes`); (3) use the `question`
382:   tool to elicit the goal statement (mandatory) and the source (mandatory)
383:   plus each optional field in turn, explicitly allowing the user to skip
384:   any optional one; (4) reference the packaged
385:   `specmgr://gol/template`/`specmgr://gol/example`/`specmgr://gol/schema`
386:   for the fixed structure; (5) assemble the full body markdown per the
387:   schema above and call `create_gol(content)`.
388: - `update_gol(id: str) -> str`: instructs the LLM to (1) call
389:   `get_gol(id)` first (never assume prior state); (2) show the user which
390:   sections are already present and which are empty, and ask via
391:   `question` which ones (if any) they want to add or revise; (3) for each
392:   selected section, elicit the new/revised text via `question`; (4) call
393:   `update_gol(id, content)` (whole-body replace, carrying forward every
394:   unchanged section); (5) mention `set_status_gol` as a separate, optional
395:   follow-up (e.g. `implemented` once the goal has genuinely been reached,
396:   `rejected`/`superseded` if abandoned or replaced).
397: 
398: Both prompts' instructional text lives in packaged data files
399: (`gol/data/gol_create_instructions.md`/`gol_update_instructions.md`, read
400: via `general.tools._packaged_data.read_packaged_text`, `string.Template`
401: substitution), matching `req_create_instructions.md`/
402: `prb_create_instructions.md`'s precedent — not an inline Python string.
403: 
404: **Frontmatter status** is REQ's exact 7-value closed set
405: (`draft`/`proposed`/`accepted`/`superseded`/`deprecated`/`rejected`/
406: `implemented`), re-declared as `GolFrontmatter`'s own `_ALLOWED_STATUSES`
407: frozenset (each domain declares its own set — `ReqFrontmatter`,
408: `TskFrontmatter`, `PrbFrontmatter` all do), with goal-specific semantics:
409: `draft` = still being written; `proposed` = under consideration;
410: `accepted` = agreed to be pursued; `implemented` = the goal has genuinely
411: been reached; `superseded` = replaced by another goal; `deprecated` = no
412: longer pursued, kept for reference; `rejected` = considered and not
413: pursued.
414: 
415: **Example/template documents:** `gol_example.md` is drafted as
416: `GOL-0007: Competitive Engines in Consumer Vehicles` — the exact goal
417: `req_example.md`'s `### Goals` sub-list already cross-references — so the
418: two packaged examples read coherently side by side; it reuses
419: `gol_reference.md`'s content verbatim (feat-16's own precedent:
420: `prb_example.md` reuses `prb_reference.md`). `gol_template.md` mirrors
421: `req_template.md` minus the `Characteristics` and `Level` sections, with
422: goal-oriented placeholder prose.
423: 
424: ### Related ADRs
425: 
426: - ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by
427:   document-type domain (domain-first hierarchy)
428: - bc5e18ad-6bbf-4265-bae4-3e34984a2d29: Generic base frontmatter model for
429:   markdown document types
430: - ddfb1109-422d-4507-8dbc-dc5e4bec9614: Expose id-based reads as a tool
431:   (`get_gol`), not a resource
432: - ec9f5262-9912-49d0-903f-fcfb54f28c13: Expose `<domain>_list` as a paged
433:   MCP tool (`list_gol`), not a resource — must be followed from the start
434:   for this new domain, not retrofitted later
435: - 71fd95d7-07f2-466f-81aa-d29b7e3ef34c: Generic `update_section` — reviewed
436:   and explicitly *not* reused for `gol` (see Design Notes)
437: 
438: No new ADR is anticipated for this feature — every schema/tooling decision
439: either follows an existing ADR's precedent directly or is scoped enough to
440: log only in this file's own Decisions Made.
441: 
442: ### Task List
443: 
444: Single, canonical breakdown of work phases and tasks. Status lives on the
445: task itself. Each phase ends with a mandatory phase-end task (tests, full
446: quality gate, README Progress update), mirroring feat-16's per-phase
447: commit discipline, since implementation is likely to span multiple
448: sessions.
449: 
450: #### Phase 1: Specification
451: 
452: - [x] Task 1.1: Write a full reference `gol_reference.md`
453:   (`.specmgr/feat/feat-18-goal/gol_reference.md`) exercising every field
454:   (`statement`, `Source`, plus all optional sections present:
455:   `Description`/`Priority`/`Tags`/`Related Artifacts` with all four
456:   sub-lists/`More Information`/`Notes`) — depends on: none — status:
457:   completed
458: - [x] Task 1.2: Define `gol` frontmatter (`gol/models/v1/frontmatter.py` —
459:   `GolFrontmatter` subclass of `MarkdownFrontmatter`, `type=Literal["gol"]`,
460:   7-value status set identical to `ReqFrontmatter`'s) — depends on: none —
461:   status: completed
462: - [x] Task 1.3: Define `gol` body structure (`gol/models/v1/body.py`) —
463:   `Goal(MarkdownSection1)` with `@alias(value=".+", type=AliasType.REGEX)`,
464:   mandatory `statement: MarkdownParagraph` + `source: Source`, optional
465:   `description`/`priority`/`tags`/`related_artifacts`/`more_information`/
466:   `notes`; `Priority` re-declares REQ's `MarkdownSection2WithComment` +
467:   `field_validator` pattern (0–99); `RelatedArtifacts(MarkdownSection2)`
468:   with four optional `MarkdownSection3` sub-lists (see Design Notes) —
469:   depends on: Task 1.2 — status: completed
470: - [x] Task 1.4: `tests/gol/models/v1/test_frontmatter.py`, `test_body.py` —
471:   structural + validation tests mirroring `tests/req/models/v1/`/
472:   `tests/prb/models/v1/`, explicit coverage of mandatory-vs-optional field
473:    combinations (each optional section individually absent/present; each of
474:    the four `Related Artifacts` sub-lists individually absent/present) —
475:   depends on: Task 1.3 — status: completed
476: - [x] Task 1.5: Phase-end quality gate — run the full pre-commit/quality
477:   gate (ruff format/check, vulture, full `unittest` suite); confirm
478:   `gol_reference.md` is `specmgr mdformat`-clean; add any new
479:   vulture-invisible Pydantic field names to `whitelist.py` if needed;
480:   update this README's Progress section — depends on: Task 1.1, Task 1.4 —
481:   status: completed
482: 
483: #### Phase 2: Pydantic Models, Parser & Schema
484: 
485: - [x] Task 2.1: `gol/models/v1/document.py` (`GolDocument(frontmatter, body)`, mirroring `ReqDocument`) — depends on: Task 1.3 — status:
486:   completed
487: - [x] Task 2.2: Implement `parse_gol(text: str) -> GolDocument` (model-layer
488:   function, mirrors `parse_req`) — depends on: Task 2.1 — status:
489:   completed
490: - [x] Task 2.3: `gol/models/v1/summary.py` (`GolSummary(DocSummary)`,
491:   subclassing `general/models/summary.py::DocSummary`, for `list_gol`) —
492:   depends on: Task 2.1 — status: completed
493: - [x] Task 2.4: Field-level `Field(description=...)` on every scalar/
494:   optional field (schema-quality parity with REQ/PRB) — depends on:
495:   Task 2.1 — status: completed
496: - [x] Task 2.5: Implement `generate_gol_schema()` in `commands/schema.py`
497:   (mirroring `generate_req_schema`, via `GolDocument.model_json_schema()`),
498:   and register `"gol"` in the `specmgr schema` doc-type generator registry
499:   (`_GENERATORS`); draft `docs/gol_schema.json` — depends on: Task 2.1 —
500:   status: completed
501: - [x] Task 2.6: `tests/gol/models/v1/test_parser.py` — mirrors
502:   `TestParseReq`'s shape (minimal doc, full reference-doc round-trip,
503:   defaults-when-absent, invalid status, missing-mandatory-field
504:   `AssertionError` cases (`statement`, `Source`), invalid-field
505:   `ValidationError` (e.g. `Priority` out of 0–99 range, invalid `type`
506:   field)) — depends on: Task 2.2, Task 2.5 — status: completed
507: - [x] Task 2.7: Phase-end quality gate — full pre-commit/quality gate
508:   including Task 2.6's new tests; update this README's Progress section —
509:   depends on: Task 2.5, Task 2.6 — status: completed
510: 
511: #### Phase 3: MCP Surface
512: 
513: - [x] Task 3.1: `gol/tools/_paths.py`/`_io.py`/`_write.py`/`_lock.py`, thin
514:   wrappers over `general/tools/_doc_paths.py` (mirrors `req/tools/`/
515:   `prb/tools/` exactly) — depends on: Task 2.2 — status: completed
516: - [x] Task 3.2: `parse_gol(path: str) -> GolDocument` tool wrapper
517:   (`gol/tools/parse_gol.py`) — depends on: Task 3.1 — status: completed
518: - [x] Task 3.3: `create_gol(content: str) -> GolDocument` tool (body-only
519:   content; MCP builds frontmatter: `id`, `type="gol"`, `status="draft"`,
520:   `created=updated=now`, `version`) — depends on: Task 3.1 — status:
521:   completed
522: - [x] Task 3.4: `update_gol(id, content) -> GolDocument` tool (whole-body
523:   replace, preserves `id`/`type`/`status`/`created`/`version`, bumps
524:   `updated`) — depends on: Task 3.1 — status: completed
525: - [x] Task 3.5: `set_status_gol(id, status) -> GolDocument` tool (only path
526:   that changes `status`; reconstructs `GolFrontmatter` via its own
527:   constructor so the 7-value validator runs, mirroring `set_status_req`) —
528:   depends on: Task 3.1 — status: completed
529: - [x] Task 3.6: `delete_gol(id) -> NoReturn` stub tool — depends on: Task
530:   3.1 — status: completed
531: - [x] Task 3.7: `validate_gol(content, full=False) -> bool` tool — depends
532:   on: none — status: completed
533: - [x] Task 3.8: `get_gol(id) -> GolDocument` tool (id-based single-document
534:   read; tool, not resource) — depends on: Task 3.1 — status: completed
535: - [x] Task 3.9: `list_gol(max_results=None, offset=None) -> PagedResult[GolSummary]`
536:   tool, via `general/tools/_paging.py`'s `paginate`/`normalize_paging`
537:   (default page size 25, cap 100), preserving the standard skip-malformed-
538:   file scan behavior — depends on: Task 2.3, Task 3.1 — status: completed
539: - [x] Task 3.10: `get_gol_example`/`get_gol_template` tools + packaged data
540:   (`gol/data/gol_example.md` — drafted as `GOL-0007: Competitive Engines in Consumer Vehicles` per Design Notes, `gol/data/gol_template.md` —
541:   `req_template.md` mirrored minus `Characteristics`/`Level`) via
542:   `general/tools/_packaged_data.py` — depends on: Task 1.1 — status:
543:   completed
544: - [x] Task 3.11: `gol/resources/{gol_schema,gol_example,gol_template}.py`
545:   — `specmgr://gol/schema` (packaged `gol/data/gol_schema.json`, mirroring
546:   `specmgr://req/schema`), `specmgr://gol/example`, `specmgr://gol/template`
547:   (no `/list`, no `/{id}`) — depends on: Task 2.5, Task 3.10 — status:
548:   completed
549: - [x] Task 3.12: `pyproject.toml` package-data entry for
550:   `biz.dfch.specmgr.gol` (`data/*.md`, `data/*.json`); `.pre-commit-config.yaml`
551:   — widen the shared schema-hook glob to include `gol/models/v1`, add a
552:   `specmgr-schema-gol-package` hook — depends on: Task 2.5 — status: completed
553: - [x] Task 3.13: `.github/workflows/ci.yml` — add the `docs/gol_schema.json`
554:   check + packaged-copy check steps — depends on: Task 2.5 — status:
555:   completed
556: - [x] Task 3.14: `gol/data/gol_create_instructions.md` +
557:   `gol/prompts/create_gol.py` (`@mcp.prompt()`, `string.Template`
558:   substitution, narrates the full interview flow — see Design Notes) —
559:   depends on: Tasks 3.3, 3.9 — status: completed
560: - [x] Task 3.15: `gol/data/gol_update_instructions.md` +
561:   `gol/prompts/update_gol.py` — depends on: Tasks 3.4, 3.5, 3.8 — status:
562:   completed
563: - [x] Task 3.16: `gol/__init__.py` (docstring + `from . import prompts, resources, tools`), add `gol` to `server.py`'s bottom-of-file domain
564:   import line (alphabetical: `adr, general, gol, prb, qa, req, tsk, uc`)
565:   and update its module docstring (Tools/Resources/Prompts sections) —
566:   depends on: Tasks 3.2-3.15 — status: completed
567: - [x] Task 3.17: `tests/gol/tools/...`, `tests/gol/resources/...`,
568:   `tests/gol/prompts/...` mirroring `tests/req/`/`tests/prb/`'s layout,
569:   including live end-to-end coverage of `create_gol`/`update_gol`'s
570:   narrated `TodoWrite`/`question`-tool flow (ACC-006) and `list_gol`'s
571:   paging behavior (default page size, `max_results` clamping, `offset`
572:   paging, `truncated` boundary) — depends on: Tasks 3.1-3.16 — status:
573:   completed
574: - [x] Task 3.18: Phase-end quality gate — full pre-commit/quality gate
575:   including Task 3.17's new tests; update this README's Progress section —
576:   depends on: Task 3.17 — status: completed
577: 
578: #### Phase 4: Cross-cutting registration
579: 
580: - [x] Task 4.1: `AGENTS.md` — update heading to "eight domain/cross-cutting
581:   packages implemented (ADR, REQ, UC, TSK, QA, PRB, GOL, general)"; add a
582:   `gol/` bullet (chronological order, after `prb/`); update the "Still
583:   genuinely missing" list (`validate_gol` not enforced via pre-commit/CI,
584:   `delete_gol` stub) and the closing domain-enumeration paragraphs —
585:   depends on: Phase 3 complete — status: completed
586: - [x] Task 4.2: `specmgr docs` / `specmgr mcp-docs` / `specmgr schema`
587:   regeneration — confirm `gol` appears correctly and all three commands
588:   report zero drift — depends on: Task 4.1 — status: completed
589: - [x] Task 4.3: Phase-end quality gate — full pre-commit/quality gate;
590:   update this README's Progress section — depends on: Task 4.2 — status:
591:   completed
592: 
593: #### Phase 5: Final cross-cutting verification
594: 
595: - [x] Task 5.1: Final verification pass — walk every ACC-001..008 and
596:   confirm each is satisfied with concrete evidence (including a live
597:   `create_gol`→`update_gol`→`set_status_gol` run, not just unit tests);
598:   run the full quality gate (ruff format/check, pylint advisory, vulture,
599:   unittest, `specmgr docs`/`specmgr mcp-docs`/`specmgr schema` drift
600:   checks) end to end; set feature status to `done` — depends on: Phase
601:   1-4 complete — status: completed
602: 
603: **Note:** If a task's scope changes mid-flight, edit its description in
604: place; rely on git history (`git log -p` on this file) to recover what was
605: originally planned, rather than keeping a second copy of the task around.
606: 
607: ## Progress
608: 
609: ### Current Status
610: 
611: **As of 2026-08-26**: Feature complete — all five phases done, all eight
612: acceptance criteria verified PASS (see annotated Acceptance Criteria
613: above), full quality gate green (1609 tests, coverage 98%, ruff
614: format/check clean, vulture clean, pylint 8.92/10 advisory — identical to
615: the Phase-4 baseline, no regressions). Phase 5's final verification walk
616: included a live, non-mocked `create_gol`→`get_gol`→`update_gol`→
617: `set_status_gol`→`get_gol`→`list_gol` run against a temp docs directory
618: (not just unit tests), `list_gol` paging confirmed live with 26 documents
619: (default 25 / cap 100 / `truncated` boundary), the MCP registration counts
620: (74 tools / 20 resources / 17 prompts) confirmed on the real `server.mcp`
621: instance, and ACC-007's real `uv build --wheel` + non-editable
622: scratch-venv install (scratch venv, `dist/`, and `build/` removed
623: afterward — `git status` shows no residue). GitHub issue #18 ("Add
624: artifact type Goal (GOL)") is filed and open; the feature is ready for
625: review/merge and the issue can be closed when the PR merges.
626: 
627: ### Blockers
628: 
629: None.
630: 
631: ### Recent Updates
632: 
633: #### Update 2026-08-26 (Phase 5: Final cross-cutting verification — feature complete)
634: 
635: - Completed Task 5.1, the final task of the feature. Walked every
636:   ACC-001..008 with concrete evidence (recorded inline in the Acceptance
637:   Criteria section above, each now checked `[x]`). This phase modified no
638:   source/test/doc/config/data file — the only write is this README
639:   (frontmatter `status: done`, the ACC annotations, the Task 5.1 flip, and
640:   these Progress updates).
641:   - ACC-001/002/003 (schema/models/parser): `docs/gol_schema.json`'s
642:     `"$comment": "v1"` (line 2) and 2020-12 `"$schema"` (line 403)
643:     confirmed; live byte-exact round-trip of `gol_reference.md` through
644:     `parse_gol` (2030 == 2030 body bytes); live minimal-doc (all six
645:     optionals `None`) and closed-set (`status: pending` →
646:     `ValidationError` naming the seven allowed values, model- and
647:     parse-level) demos; `test_parser.py` (10 tests),
648:     `test_frontmatter.py` + `test_body.py` (41 tests) re-run green.
649:   - ACC-004/005 (tools/resources): live `mcp.list_tools()/
650:     list_resources()/list_prompts()` on the real `server.mcp` instance —
651:     74/20/17 totals, exactly 10 gol tools / 3 gol resources / 2 gol
652:     prompts; `docs/MCP.md` citations match (header line 6, 10 `### Tool:`
653:     entries, 3 resource rows, no `/{id}`, no `/list`); `test_list_gol.py`
654:     (11 tests) re-run green and paging re-confirmed live with 26 docs in a
655:     temp `SPECMGR_DOCS_DIR` (`total=26`/default `max_results=25`/
656:     `truncated=True`; `max_results=100` → 26 items/`False`; `offset=25` →
657:     1 item/`False`, no page overlap); the three gol resources resolved
658:     live (`schema` dict with top-level `required: ['frontmatter',
659:     'body']`, example 2162 chars, template 1201 chars),
660:     `tests/gol/resources/` (13 tests) green.
661:   - ACC-006 (prompts): both packaged instruction files read in full (step
662:     headers quoted in the annotation); the narrated `create_gol`/
663:     `update_gol` flows walked end to end with the real tool functions in a
664:     temp `SPECMGR_DOCS_DIR` — `list_gol` empty (no near-duplicate) →
665:     `create_gol` (draft, id `07331e39-…`) → `get_gol` → `update_gol` (adds
666:     the absent `## Notes`, carries forward every unchanged section,
667:     `updated` bumped) → `set_status_gol(…, "accepted")` → final
668:     `get_gol`/`list_gol` show `accepted`; both prompt functions resolved
669:     their packaged narration live with `$topic`/`$id` substituted (3554 /
670:     2567 chars); `tests/gol/prompts/` (22 tests) and
671:     `tests/gol/tools/test_integration.py` (2 tests) re-run green.
672:   - ACC-007 (packaged data from a real install): `uv build --wheel` →
673:     `dist/biz_dfch_specmgr-0.10.0-py3-none-any.whl`; `unzip -l` confirms
674:     all five `gol/data/*` files + every gol module (35 entries under
675:     `biz/dfch/specmgr/gol/`); non-editable install with the mcp extra into
676:     a scratch venv under `/tmp/opencode/`; `inspect.getfile` proves the
677:     module loads from the venv's `site-packages`, and
678:     `get_gol_example()`/`get_gol_template()`/`gol_schema()` resolve real
679:     packaged content from there (see Notes for the venv specifics).
680:   - ACC-008 (doc generation drift): `specmgr docs`/`mcp-docs`/`schema`
681:     (generic + `--type gol --output-dir …/gol/data`)/`adr-toc`/
682:     `coverage-badge` all re-run exit 0, every generated file reported
683:     "unchanged", `git diff --exit-code -- docs/` clean (no test files
684:     added this phase, so `docs/GENERATED.md`'s test-file count is
685:     unchanged); `AGENTS.md`'s eight-package heading (line 5) + `gol/`
686:     bullet (line 81) confirmed from Phase 4.
687: - Ran the full quality gate one final time: `ruff format --check` (1011
688:   files already formatted), `ruff check` (all passed), `pylint` (advisory;
689:   8.92/10 — "previous run: 8.92/10, +0.00", identical to the Phase-4
690:   baseline; no `.py` file changed this phase), `vulture src/ whitelist.py
691:   --min-confidence 60` (exit 0, no output), full suite via `coverage run`
692:   (**1609 tests**, 54.6s, OK) followed by `specmgr coverage-badge` (98%,
693:   `docs/coverage.svg` byte-unchanged).
694: - Set this README's own frontmatter `status: in-progress` → `status: done`
695:   as Task 5.1's own required action; every phase and every acceptance
696:   criterion is now checked off.
697: - Next: Feature complete — ready for review/merge; issue #18 can be closed
698:   when the PR merges.
699: - Notes:
700:   - ACC-007 venv specifics: the system `python3` is 3.10.12, below the
701:     project's `requires-python = ">=3.11"`, so the scratch venv was
702:     created with `uv venv --python 3.13` (uv-managed CPython 3.13.13) and
703:     the wheel installed with `uv pip install --python
704:     /tmp/opencode/gol-scratch-venv/bin/python "dist/biz_dfch_specmgr-
705:     0.10.0-py3-none-any.whl[mcp]"` (network to PyPI was available; the
706:     full mcp dependency tree installed). Cleanup confirmed: `rm -rf
707:     /tmp/opencode/gol-scratch-venv dist/*` plus removal of the
708:     `uv build`-created `build/` artifact dir (`build/lib` copies of the
709:     source tree); `git status` shows zero entries afterward (both `dist/`
710:     and `build/` are gitignored, `.gitignore` lines 11/13).
711:   - The full-suite run's merged log carries a few lines of stray stdout
712:     after the `OK` summary (a test-spawned subprocess flushing late); the
713:     process exit code is 0 and the summary reads `Ran 1609 tests in
714:     54.648s / OK` — no test failures.
715:   - No new design decisions required this phase — purely verification,
716:     exactly as scoped.
717: 
718: #### Update 2026-08-26 (Phase 4)
719: 
720: - Completed: Phase 4 (Cross-cutting registration), Tasks 4.1–4.3.
721:   - Task 4.1: `AGENTS.md` updated, scoped exactly to the plan — heading
722:     "seven → eight domain/cross-cutting packages implemented (ADR, REQ,
723:     UC, TSK, QA, PRB, GOL, general)"; opening sentence "Six → Seven
724:     document-type domains plus one cross-cutting package"; new
725:     `**gol/**` (Goal) bullet in chronological position (after `prb/`,
726:     before `general/`) mirroring the `prb/` bullet's shape and density
727:     (all ten tools with the `delete_gol` stub noted, the three resources
728:     with the no-`specmgr://gol/{id}` (ADR ddfb1109) / no-
729:     `specmgr://gol/list` (`list_gol` paged tool from day one, ADR
730:     ec9f5262) references, the narrated `TodoWrite` + `question`-tool
731:     prompts with the `create_gol` dedup-check-first note, schema at
732:     `gol/models/v1/` inside the domain package, the REQ-mirrored-minus-
733:     `Characteristics`/`Level` body note, whole-body `update_gol`); "Still
734:     genuinely missing" list gains `validate_gol` (first bullet's
735:     parenthetical) and `delete_gol` (stubs bullet); the closing
736:     "Don't assume any other domain package exists beyond …" enumeration
737:     gains `gol` (alphabetical, between `general` and `prb`). Two further
738:     domain-set enumerations updated per the task's item-5 rule (see
739:     Decisions Made): the "Still genuinely missing" bullet that lists
740:     which domains register `tools`/`resources`/`prompts`
741:     (`req`/`tsk`/`qa`/`prb` → `req`/`tsk`/`qa`/`prb`/`gol`), and the
742:     "MCP server (`server.py`)" section's list of the domain packages
743:     `server.py`'s bottom import line pulls in (now includes `gol`,
744:     matching the actual line since Phase 3). Left untouched, deliberately:
745:     the "Models location" paragraph's historical "REQ, UC, and TSK were
746:     built *after* that refactor" enumeration (already stale pre-GOL — it
747:     omits QA/PRB; fixing it is a pre-existing-staleness edit outside this
748:     task, reported to the orchestrator) and the "Existing feature
749:     folders" paragraph (explicitly out of scope per the task).
750:   - Task 4.2: zero-drift confirmation — `specmgr docs` (exit 0;
751:     `git diff --exit-code -- docs/` exit 0 — no changes), `specmgr
752:     mcp-docs` (exit 0; `git diff --exit-code -- docs/MCP.md` exit 0),
753:     `specmgr schema` (exit 0; all six types "unchanged"). `gol` appears
754:     correctly: `docs/MCP.md` header line `20 resource(s), 1 resource
755:     template(s), 74 tool(s), 17 prompt(s)` with exactly 10 `### Tool:
756:     *gol` entries, 3 `### Resource: gol_*` entries, 2 `### Prompt: *gol`
757:     entries; `docs/GENERATED.md` carries the full 30-line `gol/` module
758:     section (package + `models/v1` 7 + prompts 3 + resources 4 + tools
759:     15); `docs/api/` holds 23 `biz.dfch.specmgr.gol*` pages (the package
760:     page `biz.dfch.specmgr.gol.md` + the 22 sub-module pages: 15 tools
761:     incl. `tools.md`, 4 resources incl. `resources.md`, 3 prompts incl.
762:     `prompts.md`); `docs/gol_schema.json` present with
763:     `$comment: "v1"`, 2020-12 dialect, top-level
764:     `required: ["frontmatter", "body"]`.
765:   - Task 4.3: quality gate green — see below.
766: - Next: Phase 5 (Final cross-cutting verification) — walk every
767:   ACC-001..008 with concrete evidence (incl. the live
768:   `create_gol`→`update_gol`→`set_status_gol` run and ACC-007's
769:   scratch-venv install), full quality gate end to end, set feature
770:   status to `done`.
771: - Notes:
772:   - Quality gate: `ruff format --check` (1011 files already formatted),
773:     `ruff check` (all passed), `pylint` (advisory; exit 30, 8.92/10 —
774:     identical to the Phase-3 baseline by construction: this phase
775:     changes no `.py` file, and `git status` confirms only `AGENTS.md` +
776:     this README are modified; 112 of the pre-existing findings reference
777:     committed `gol` files, e.g. `tests/gol/models/v1/test_body.py`,
778:     none introduced here), `vulture` (exit 0, no output), full unittest
779:     suite (1609 tests, all OK, 55s), `specmgr coverage-badge` (98%,
780:     `docs/coverage.svg` byte-unchanged), `specmgr adr-toc` (no change to
781:     `docs/adr/README.md`), `specmgr docs`/`mcp-docs`/`schema` (zero
782:     drift, per Task 4.2 above). Final `git status`: only `AGENTS.md` and
783:     `.specmgr/feat/feat-18-goal/README.md` modified.
784:   - ACC-008 (this phase's acceptance criterion) is satisfied by the
785:     Task 4.2 zero-drift evidence plus the `AGENTS.md` update: `specmgr
786:     docs`/`schema`/`mcp-docs` all report no drift after implementation,
787:     and `AGENTS.md` now reflects eight domain/cross-cutting packages.
788:     The final ACC walk over all of ACC-001..008 is Phase 5's Task 5.1.
789: 
790: #### Update 2026-08-26 (Phase 3)
791: 
792: - Completed: Phase 3 (MCP Surface), Tasks 3.1–3.18.
793:   - Task 3.1: `gol/tools/_paths.py` (`gol_base_dir`/
794:     `ensure_gol_base_dir`/`iter_gol_paths`/`find_gol_path`/
795:     `GolNotFoundError`/`GOL_TYPE_NAME`), `_io.py` (`read_gol`/
796:     `load_by_id`), `_write.py` (`write_gol_file`), `_lock.py`
797:     (`gol_lock`) — thin wrappers over `general/tools/_doc_paths.py`,
798:     mirroring `prb/tools/` file-for-file (REQ's same shape).
799:   - Tasks 3.2–3.9: all eight lifecycle tools — `parse_gol` (path-based
800:     disk read), `create_gol` (body-only content; tool builds the full
801:     `GolFrontmatter`: fresh `uuid4` id, `type="gol"`, `status="draft"`,
802:     `created=updated=now` with `timespec="microseconds"`,
803:     `version=CURRENT_SCHEMA_VERSION`; filename
804:     `gol-<uuid>-<slug>.md`), `update_gol` (whole-body replace, preserves
805:     `id`/`type`/`status`/`created`/`version`, bumps `updated`),
806:     `set_status_gol` (sole status path; reconstructs `GolFrontmatter` via
807:     its own constructor so the 7-value validator runs), `delete_gol`
808:     (stub, `structured_output=False`), `validate_gol` (disk-free dry run,
809:     `full` flag with symmetric `ValueError`s), `get_gol` (tool-only id
810:     read, ADR ddfb1109), `list_gol` (`PagedResult[GolSummary]` via
811:     `paginate`/`normalize_paging`, skip-malformed-file scan, `title` =
812:     body H1, ADR ec9f5262 paged-from-day-one wording).
813:   - Task 3.10: `get_gol_example`/`get_gol_template` tools + packaged data —
814:     `gol_example.md` is a **byte-identical copy of `gol_reference.md`**
815:     (`diff` empty, verified); `gol_template.md` = `req_template.md` minus
816:     `## Characteristics`/`## Level` with goal-oriented placeholders
817:     (dead-UUID `id: deaddead-goal-goal-goal-deaddeadgoal`, plain
818:     `2026-08-26` dates) — verified parseable by `parse_gol` (same
819:     guarantee `tests/prb/tools/test_integration.py` gives PRB's
820:     template); `gol_schema.json` generated via `specmgr schema --type gol
821:     --output-dir src/biz/dfch/specmgr/gol/data` (byte-identical to
822:     `docs/gol_schema.json`, generator exits 0).
823:   - Task 3.11: `gol/resources/` — `specmgr://gol/schema` (reads the
824:     packaged JSON via `read_packaged_text`, mirroring `req_schema.py`),
825:     `specmgr://gol/example`, `specmgr://gol/template`; no `/list`, no
826:     `/{id}`.
827:   - Tasks 3.12/3.13: `pyproject.toml` package-data entry for
828:     `biz.dfch.specmgr.gol` (`data/*.md`, `data/*.json`, alphabetical
829:     position between `adr` and `prb`); `.pre-commit-config.yaml` — all six
830:     existing schema-hook `files:` globs widened to include
831:     `gol/models/v1`, plus a new `specmgr-schema-gol-package` hook
832:     (mirrors the prb one); `ci.yml` — two new 3.13-pinned steps
833:     (`docs/gol_schema.json` all-types check + packaged-copy check) after
834:     the prb pair, before the coverage-badge step.
835:   - Tasks 3.14/3.15: `gol/data/gol_create_instructions.md` +
836:     `gol/prompts/create_gol.py` (`topic: str` only; narrates
837:     dedup-check-first via `list_gol` → `TodoWrite` list over `statement` +
838:     `Source` + each optional section → `question`-tool interview with
839:     explicit skip-allowed for optionals → `specmgr://gol/template|example|
840:     schema` references → `create_gol(content)` → `update_gol` for later
841:     revisions; also narrates the deliberate `Characteristics`/`Level`
842:     omissions) and `gol/data/gol_update_instructions.md` +
843:     `gol/prompts/update_gol.py` (`id: str` only — see Decisions Made;

(Output capped at 50 KB. Showing lines 1-843. Use offset=844 to continue.)
</content>
````

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 90.8s)

_Thinking:_

I've confirmed the feature README conventions. Key points:

- Each phase ends with a **phase-end quality gate task** (full pre-commit/quality gates: ruff format/check, vulture, full unittest suite, doc drift check as applicable), and a README Progress update — this matches the user's requirement that "every phase must have a complete test cycle."
- The Phase-Implementer agent implements exactly one phase from top to bottom: "code, tests, phase-end quality gate, and updating the plan's Progress section."
- Phases have a dependency chain, and status is written inline per task.

Now, let me check the phase-orchestrator agent. According to the task tool's description: "phase-implementer: Implements exactly one phase of the `.specmgr/feat/<id>/README.md` plan from top to bottom — code, tests, phase-end quality gate, and updating the plan's Progress section — then stops and reports. Driven by phase-orchestrator. Not intended to be selected directly."

So the orchestration flow is: I (main agent) launch phase-orchestrator, and it in turn drives phase-implementer per phase. Or the user launches phase-orchestrator. The user said "this feature will be orchestrated by the Phase-Orchestrator agent and implemented by the Phase-Implementer agent." So in the plan, the final step after plan approval is: launch `task(subagent_type="phase-orchestrator")` with the feature id, and have it drive the phases.

Wait — is phase-orchestrator a selectable agent? The available agent list includes "phase-implementer" but not "phase-orchestrator". The phase-implementer's description says "driven by phase-orchestrator. Not intended to be selected directly." Hmm, phase-orchestrator isn't in my task tool's list of available agent types. The available types are: architect-designer, ccm, explore, implementation-specialist, phase-implementer, python-reviewer, requirements-clarifier, ste100, test-automation-engineer.

So phase-orchestrator is not a directly launchable sub-agent from here. Probably phase-orchestrator is *me* (the main session's role) — i.e., the main conversation acts as orchestrator and launches phase-implementer per phase. That matches "driven by phase-orchestrator": phase-orchestrator is a role, likely documented somewhere. Let me search the repo for "phase-orchestrator" to see if there's an agent definition file (e.g., under .opencode/ or agent config) and understand the contract.

Let me search for "phase-orchestrator" and "phase-implementer" in the repo and in opencode config.

I have the phase convention (feat-18 shows the per-phase quality-gate discipline). Now let me find the Phase-Orchestrator/Phase-Implementer agent definitions to wire the plan to them correctly.

**Tool: bash**

**Input:**

```json
{
  "command": "grep -rn \"phase-orchestrator\\|phase-implementer\" --include=\"*\" -l . /home/user/docker/opencode/.config/opencode 2>/dev/null | grep -v node_modules | grep -v __pycache__ | head -20"
}
```

**Output:**

```
./.git/index
./.opencode/agent/phase-implementer.md
./.opencode/agent/phase-orchestrator.md
./.opencode/command/implement-feature.md
./.ruff_cache/0.16.1/400181868758547324
./.specmgr/feat/feat-15-add-artifact-type-risk/README.md
./.specmgr/feat/feat-15-add-artifact-type-risk/session-ses_fccf-feat-15-00.md
./.specmgr/feat/feat-15-add-artifact-type-risk/session-ses_fcc0-feat-15-01.md
./.specmgr/feat/feat-18-goal/session-ses_fc59-feat-18-01-implementation.md
./.specmgr/feat/feat-16-problem-statement/session-ses_fc85-feat-16-01.md
./.specmgr/feat/feat-14-qa-v2-adjacent-qa/session-ses_fd23-feat-14-00.md
./.specmgr/feat/feat-12-qa-artifact/session-ses_feab-feat-12-qa-artifact.md

```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 76.8s)

_Thinking:_

There are agent definitions in the repository: `.opencode/agent/phase-orchestrator.md` and `.opencode/agent/phase-implementer.md`, and furthermore there's also a command `.opencode/command/implement-feature.md`. I'll read these to understand the orchestration contract.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.opencode/agent/phase-orchestrator.md"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/.opencode/agent/phase-orchestrator.md</path>
<type>file</type>
<content>
1: ---
2: description: >-
3:   Drives multi-phase feature implementation from a `.specmgr/feat/<id>/README.md`
4:   plan by delegating each phase to a fresh `phase-implementer` subagent and
5:   overseeing (never writing) the work. Use when implementing a planned feature
6:   phase by phase.
7: mode: primary
8: temperature: 0.1
9: permission:
10:   edit: deny
11:   write: deny
12:   bash:
13:     "git status*": allow
14:     "git diff*": allow
15:     "git log*": allow
16:     "git show*": allow
17:     "git add*": allow
18:     "git commit*": allow
19:     "git push*": deny
20:     "uv run*": allow
21:     "*": allow
22:   task: allow
23:   webfetch: allow
24: ---
25: 
26: # Phase Orchestrator
27: 
28: You are an **orchestrator**, not an implementer. You drive a multi-phase
29: feature plan to completion by delegating each phase to a fresh
30: `phase-implementer` subagent, verifying its results, and moving on. You never
31: write code yourself — the `edit` and `write` tools are denied to you on
32: purpose. If you feel the urge to edit a file, that is a signal to delegate
33: instead.
34: 
35: ## What you own vs. what you delegate
36: 
37: **You own (do these yourself):**
38: 
39: - Reading the feature plan (`.specmgr/feat/<id>/README.md`) and understanding
40:   the phase/task breakdown and dependency order.
41: - Maintaining a `todowrite` list mirroring the plan's phases, one item per
42:   phase, updated in real time.
43: - Deciding which phase runs next based on the plan's stated dependencies.
44: - Writing a precise, self-contained task prompt for each phase and launching
45:   exactly one `phase-implementer` subagent per phase via the `task` tool.
46: - Verifying the subagent's returned result: re-run the phase-end quality gate
47:   yourself (read-only + `uv run` commands are allowed), inspect `git diff` /
48:   `git status`, and confirm the phase's acceptance criteria are met.
49: - Resolving ambiguity in the plan by asking the user (the `question` tool)
50:   before delegating — never let a subagent guess at an unresolved design
51:   decision.
52: - Deciding whether a phase passed. If it did not, sending the subagent back
53:   (resume its `task_id`) with specific, concrete corrections.
54: - The per-phase commit (with the user's confirmation), keeping one
55:   Conventional Commit per phase as the plan requires.
56: 
57: **You delegate (never do these yourself):**
58: 
59: - Writing, editing, or creating any source file, test, or data file.
60: - Running the actual code changes for a phase.
61: - Debugging and fixing failing tests *within* a phase (the subagent fixes its
62:   own work; you only verify and, if needed, send it back).
63: 
64: ## Workflow
65: 
66: 1. **Load the plan.** Read the target `.specmgr/feat/<id>/README.md` in full,
67:    plus its `history.md` if present. Identify every phase, its tasks, its
68:    dependencies, and its mandatory phase-end gate. Build a `todowrite` list
69:    with one entry per phase.
70: 2. **Pre-flight.** If any design decision the next phase depends on is
71:    unresolved or ambiguous in the plan, ask the user now with `question`.
72:    Do not delegate on top of an ambiguity.
73: 3. **Delegate one phase.** Mark the phase `in_progress`. Launch a single
74:    `phase-implementer` subagent with a prompt containing:
75:    - the absolute path to the plan README and the exact phase heading;
76:    - the complete list of that phase's tasks, verbatim from the plan;
77:    - the phase's dependencies and what already-completed phases produced;
78:    - the explicit instruction to run that phase's phase-end quality gate and
79:      report concrete evidence (commands run + their output) back to you;
80:    - the explicit instruction to update the plan README's Progress section
81:      (Current Status, a dated Recent Updates entry, Decisions Made if
82:      applicable) as the plan's phase-end task requires;
83:    - the instruction NOT to commit, NOT to start the next phase, and to stop
84:      and return a summary once the phase is done or if it hits a blocker.
85: 4. **Verify.** When the subagent returns, independently confirm the work:
86:    inspect `git diff`/`git status`, re-run the quality gate commands yourself
87:    (`uv run --frozen ruff format --check`, `uv run --frozen ruff check`,
88:    `uv run --frozen vulture ...`, the `unittest` suite, and any
89:    `specmgr docs`/`specmgr adr-toc`/`specmgr schema` drift checks the phase
90:    touches). Never take "tests pass" on trust — run them.
91: 5. **Correct or accept.** If verification fails, resume the same subagent
92:    (`task_id`) with the specific failures and required fixes; do not fix it
93:    yourself. If it passes, mark the phase `completed`.
94: 6. **Commit.** Ask the user to confirm, then stage and commit that phase as
95:    one Conventional Commit (see the `conventional_commit_message` tooling).
96: 7. **Advance.** Move to the next phase per plan dependency order. Repeat.
97: 8. **Finish.** After the plan's final verification phase, walk every
98:    acceptance criterion, confirm each with concrete evidence, and report a
99:    final summary to the user.
100: 
101: ## Hard rules
102: 
103: - One `phase-implementer` subagent per phase. Do not batch multiple phases
104:   into one delegation, and do not run phases out of dependency order.
105: - Never edit or write files. If a fix is a one-line typo, still delegate it —
106:   the orchestrator/implementer boundary must stay clean and auditable.
107: - Always re-verify a phase's quality gate yourself before accepting it.
108: - Keep the `todowrite` list authoritative and current at all times.
109: - Preserve the plan's own conventions (per-phase commit, numbering gaps,
110:   Progress-section discipline). Do not renumber tasks.
111: - Surface blockers to the user immediately; do not invent a workaround that
112:   contradicts the plan.

(End of file - total 112 lines)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.opencode/agent/phase-implementer.md"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/.opencode/agent/phase-implementer.md</path>
<type>file</type>
<content>
1: ---
2: description: >-
3:   Implements exactly one phase of a `.specmgr/feat/<id>/README.md` plan end to
4:   end — code, tests, the phase-end quality gate, and the plan's Progress-section
5:   update — then stops and reports. Driven by the `phase-orchestrator`; not
6:   intended to be selected directly.
7: mode: subagent
8: temperature: 0.1
9: permission:
10:   edit: allow
11:   write: allow
12:   bash:
13:     "git push*": deny
14:     "*": allow
15:   task: deny
16: ---
17: 
18: # Phase Implementer
19: 
20: You implement **exactly one phase** of a feature plan, completely, then stop.
21: You are launched by the `phase-orchestrator` with a prompt naming the plan
22: file, the phase, and that phase's tasks. You do the real work: writing code,
23: writing and running tests, and running the phase-end quality gate. You do not
24: plan the whole feature, and you do not proceed past your assigned phase.
25: 
26: ## Scope discipline
27: 
28: - Do only the tasks of the single phase you were given. Do not start the next
29:   phase, even if it looks trivial or you have context budget left.
30: - Do not commit. The orchestrator owns commits. Leave the working tree clean
31:   and staged/unstaged state as-is for the orchestrator to inspect.
32: - Do not delegate — the `task` tool is denied to you. You are the one doing the
33:   work.
34: - Follow the plan's own conventions exactly: file locations, naming, numbering
35:   gaps (never renumber tasks), and the mirror-an-existing-domain instructions.
36:   When the plan says "1:1 port of REQ's X", read REQ's X first and match it.
37: - If you hit a genuine ambiguity or a design decision the plan left unresolved,
38:   STOP and report it to the orchestrator rather than guessing. Do not invent a
39:   design decision.
40: 
41: ## Procedure
42: 
43: 1. Read the plan README for context, then focus on your assigned phase's
44:    tasks. Read any sibling domain the plan tells you to mirror (e.g. `req/`,
45:    feat-10) before writing, so you match existing patterns.
46: 2. Implement every task in the phase.
47: 3. Run the phase-end quality gate that the plan specifies for the phase.
48:    Unless the plan says otherwise, that is:
49:    - `uv run --frozen ruff format --check`
50:    - `uv run --frozen ruff check`
51:    - `uv run --frozen vulture src/ whitelist.py --min-confidence 60`
52:    - `uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"`
53:    - plus any `specmgr docs` / `specmgr adr-toc` / `specmgr schema --type <t>`
54:      drift checks the phase touches.
55:    Fix your own failures and re-run until the gate is green. Debugging your own
56:    work is in scope; do not hand a red gate back to the orchestrator.
57: 4. Update the plan README's Progress section as the phase-end task requires:
58:    Current Status, a dated Recent Updates entry, and a Decisions Made entry if
59:    the phase settled any decision. Keep the plan's Task List status markers in
60:    sync (mark the phase's tasks done in place).
61: 5. Stop and return a concise report to the orchestrator containing:
62:    - which tasks you completed and the files you changed (paths);
63:    - the exact quality-gate commands you ran and their pass/fail outcome;
64:    - any design decision you made and why (for the Decisions Made log);
65:    - anything the orchestrator should verify or that blocks the next phase.
66: 
67: ## Quality bar
68: 
69: - Match `.specmgr/conventions.md` and the repo's existing style (ruff, line
70:   length 120, mandatory type hints, `result` for return values).
71: - New files must be `git add`-visible for pylint/CI, but do NOT commit — just
72:   make sure they exist on disk in the right place.
73: - Prefer editing existing files and mirroring existing domains over inventing
74:   new structure.

(End of file - total 74 lines)
</content>
```

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.opencode/command/implement-feature.md"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/.opencode/command/implement-feature.md</path>
<type>file</type>
<content>
1: ---
2: description: Drive a .specmgr feature plan to completion, one phase per subagent.
3: agent: phase-orchestrator
4: ---
5: 
6: Implement the feature planned in `.specmgr/feat/$ARGUMENTS/README.md`.
7: 
8: Act strictly as an orchestrator: read the plan in full, build a phase-by-phase
9: `todowrite` list, and drive it to completion by delegating **each phase** to a
10: fresh `phase-implementer` subagent (one subagent per phase, in dependency
11: order). After each subagent returns, independently re-run that phase's quality
12: gate, inspect `git diff`, confirm the phase's acceptance criteria, then — with
13: my confirmation — commit that phase as one Conventional Commit before moving
14: on. Do not write or edit any file yourself; delegate all implementation.
15: 
16: Before delegating a phase whose design depends on an unresolved decision, ask
17: me first.

(End of file - total 17 lines)
</content>
```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 248.7s)

_Thinking:_

Now I fully understand the orchestration mechanism:

- `.opencode/command/implement-feature.md` is a command that runs the `phase-orchestrator` agent against `.specmgr/feat/<id>/README.md`.
- phase-orchestrator: reads the plan, builds a todowrite per phase, delegates each phase to a fresh phase-implementer, verifies (re-runs the quality gates), commits per phase (with user confirmation), and advances.
- phase-implementer: implements exactly one phase — code + tests + phase-end quality gate + updating the Progress section of the plan README — and stops and reports.

Key implications for the plan:

1. The feature README must be created **before** orchestration starts — but wait: I'm in plan mode (read-only). The user said "please create a feature with phases from it." Creating the feature folder + README is itself an edit. In plan mode I can't do it. So the plan has to include Phase 0 (or Task 0.x): "Create the feature folder and README with the full phase breakdown" — either I do this myself once out of plan mode, or the user runs something. Actually, the cleanest is: **Phase 1 of the plan is "scaffold the feature + ADR"**, and the orchestrator/implementer handles it. But there's a chicken-and-egg problem: the orchestrator drives phases *from* the README; the README itself has to exist first.

Looking at feat-18's session file might tell me how it was started (session-ses_fc59-feat-18-01-implementation.md). The feature was probably created by the main agent in a planning session before the orchestrator was launched. The user's request "please create a feature with phases from it" = write the README now (as part of the plan; execution after approval). Since plan mode forbids edits, my deliverable is a **complete plan whose Phase 1 is exactly that: creating the feature folder + README (with the exact phase breakdown specified in the plan) + ADR**. Then orchestration: run the `/implement-feature feat-NNN-...` command (phase-orchestrator), and drive Phases 2..N.

Hmm, wait. Actually there's a subtle point: the README's Task List contains phases. Phase 1 creates the README… circular. Solution: **the plan itself (this conversation) fully specifies the README content**, Phase 1 = "Create the feature folder + README + ADR", and the README's own task list starts with Phase 1 (scaffolding) marked done once Phase 1 completes, followed by the implementation phases. This is self-consistent: the README is written with all phases enumerated and Phase 1's task marked "status: in-progress" → flipped to done at the end.

Alternatively, more simply: I (the main agent, once out of plan mode) create the README as step 0 before launching the orchestrator, and the README's phases are all implementation phases (no meta-phase). Which fits the repo's practice better? Let me check the feat-18 session file to see how the feature README was created — was there a Phase 1 "Specification" that included the reference document, with the README itself already existing before that? In feat-18, Phase 1 was "Specification" (writing gol_reference.md, models, tests) — the README existed from the start (created during the planning session, status: planning → in-progress). So repo practice is: **the README is authored in a planning session (by the main agent), then the orchestrator drives the implementation phases**.

Given that the user explicitly asked to "create a feature with phases from it", my plan is:

- Step 0 (me, once plan mode is lifted, or as part of Phase 1): create `.specmgr/feat/feat-NNN-consolidate-mutation-tools/README.md` with the full plan + phase task list + frontmatter, and create the ADR via specmgr_create_adr.
- Then: user (or I) runs `/implement-feature feat-NNN-consolidate-mutation-tools`, and the phase-orchestrator drives the phases.

Actually — can I launch the phase-orchestrator myself? It's not in my `task` tool's agent list (I can only launch the listed agents). The orchestrator is `mode: primary` — meaning it's a primary agent the user selects (e.g., `/agent phase-orchestrator`, or via the `/implement-feature` command which sets `agent: phase-orchestrator`). So in the plan, the orchestration step is: user runs the `/implement-feature feat-NNN-...` command (or switches to the phase-orchestrator agent), which drives the phase-implementer subagents. I should spell this out: the plan I produce is executed by the orchestrator; I (this session) only prepare the feature README + ADR.

Hmm, but the user said "the feature is orchestrated by the Phase-Orchestrator agent and implemented by the Phase-Implementer agent" — describing the mechanism, and asking me to walk the plan and adjust it accordingly. So the plan has to be shaped as follows:

1. **Phase 1: Feature scaffolding + ADR** — create the feature folder/README (with this plan's phase list), create the ADR via `specmgr_create_adr`, regenerate `adr-toc`. Test cycle: full quality gates (ruff, vulture, unittest, specmgr docs/mcp-docs/adr-toc drift). Wait — does Phase 1's README creation have to happen before the orchestrator reads the plan? Yes — the orchestrator reads the README to drive phases. So either Phase 1 is done by the main agent before orchestration, or the orchestrator's first phase is scaffolding (but in that case the README wouldn't exist yet for the orchestrator to read… chicken-and-egg).

Cleanest resolution: **the feature README is created in this session (plan→execute transition, step 0, done by me directly or by an implementation-specialist), before the phase-orchestrator is launched.** The README contains Phases 1..N (all implementation phases). Then `/implement-feature feat-NNN-...` drives them. The ADR is… hmm, the ADR needs to be created via the specmgr MCP tool (ADR 898bfcd0: "Create and edit ADRs only via MCP structured tools, never…"). The ADR is part of the feature — either put it in Phase 1 or make it step 0.

Wait, actually let me reconsider: if Phase 1 = "ADR + feature documentation" is included in the README, then the chicken-and-egg is only about the README's existence, not its content. The README must exist for the orchestrator, but the first phase can be the ADR (creating docs/adr/... + adr-toc regeneration + gates). That works:

- Step 0 (me, pre-orchestration): create the feature folder + README (full plan: requirements, ACC, phase task list, progress section), with frontmatter status: planning→in-progress.
- Phase-orchestrator drives:
  - Phase 1: ADR (create via specmgr_create_adr, adr-toc, gates)
  - Phase 2: general/tools/update.py (7 adapters + dispatch + mcp tool) + its tests
  - Phase 3: general/tools/set_status.py (8 adapters + dispatch) + its tests
  - Phase 4: delete the old tools + fix the domain's __init__/docstrings + register in general
  - Phase 5: rewrite prompts/instruction data + prompt tests
  - Phase 6: server.py docstring + docs regeneration + AGENTS.md + CHANGELOG
  - Phase 7: final verification (walk ACCs, live end-to-end, set status to done)

But wait — there's a big problem with mid-feature phases: \*\*after Phase 2/3 adds the new `update`/`set_status` tools, and before Phase 4 deletes the old ones, both exist — that's fine (registration coexists; the mcp-docs drift check just regenerates). But the *tests* of old tools remain until Phase 4 — fine. However, the pre-commit hook runs the full unittest suite + specmgr docs/mcp-docs on commit: as long as each phase keeps docs in sync (regenerate at each phase's gate), each phase's gate stays green. Good — that's exactly why "each phase has a full test cycle": the orchestrator re-runs the full gate after each phase.

But: vulture! Deleting 15 modules in Phase 4 — private helpers in the domain remain used. But what about the `ReqNotFoundError` class etc.? Still used by get_req. OK. What about symbols only referenced by the deleted tools' tests? Tests are also deleted in Phase 4 (the phase includes removing the old tests). Vulture scans only src/. Fine.

Another mid-feature concern: **during Phases 2–4, the `update` tool exists while `update_req` etc. also exist — the MCP surface temporarily has both. That's acceptable in-branch (not released). Fine.**

Also, a subtle import-order concern: adding `general/tools/update.py` in Phase 2 (registered via general/tools/__init__.py) means that from Phase 2 onward, every fresh import of server pulls in the domain packages earlier — the smoke test in Phase 2's gate catches circular imports. Good — that's why the smoke test belongs in Phase 2 (the phase that introduces it), not just at the end.

Now, "each phase must have a full test cycle. I don't want to test only at the end." — the feat-18 convention already has per-phase-end quality gates (full ruff+vulture+unittest+drift checks). I'll make this explicit in each phase's task list: a "phase-end quality gate" task that enumerates the full commands + README progress update. This matches exactly the phase-implementer's default gate.

Next, on phase granularity: each phase should be implementable by a fresh phase-implementer without ambiguity, and should leave the repo in a green state (the full test suite passes at each phase boundary). Let me carefully verify that each phase boundary is green:

- **Step 0** (README only): green (no code).

- **Phase 1: ADR** — adds a docs/adr file; regenerate adr-toc; gates green. ADR content: describes the decision (type-dispatched update/set_status, exclusion of ADR from update, superseded_by for adr in set_status, removal of old tools). Note: ADR creation is via the `specmgr_create_adr` MCP tool (per ADR 898bfcd0). phase-implementer has bash allowed, MCP tools available? It has edit/write/bash — MCP tools (like specmgr_create_adr) are part of the toolset the subagent has (task tool deny is only for sub-subagents; MCP tools are accessible — feat-18's ADR etc. were probably created this way). The plan should explicitly state "use the specmgr_create_adr MCP tool, never hand-write."

- **Phase 2: `update` generic tool + tests (additive only).** New `general/tools/update.py`; registered in `general/tools/__init__.py`. Old tools untouched. Tests: `tests/general/tools/test_update.py` — but wait, if old `update_req` etc. still exist, testing `update(type="req", ...)` is additive. Green. mcp-docs drift: regenerate docs/MCP.md (adds `update` tool entry). Also `specmgr docs` (docs/api for the new module). Gates green.

- **Phase 3: `set_status` generic tool + tests (additive).** New `general/tools/set_status.py`; 8 adapters (7 domain ports + ADR port with superseded_by). Registered. Tests `tests/general/tools/test_set_status.py`. But — the name collision! ADR's `set_status` tool is already registered under the name `set_status` (adr/tools/set_status.py). Adding a new `@mcp.tool(name="set_status")` in Phase 3 while the ADR one still exists → duplicate tool name registration → the mcp SDK probably raises on duplicate registration (or silently overwrites). This breaks Phase 3's gate!

  Fix: Phase 3 must be additive and non-colliding: (a) temporarily register the generic one under a different name — ugly; (b) merge Phase 3 and Phase 4: Phase 3 = "set_status generic + delete all 15 old tools + fix docstrings/registration" in one phase — larger but atomic. The set_status name collision forces the ADR tool deletion to be in the same phase as the generic one's addition. For `update`, no collision exists (the old names are update_req etc.), so Phase 2's `update` can be additive.

  Options:

  - Phase 2: `update` generic (additive) + tests.
  - Phase 3: `set_status` generic (additive) + delete all 15 old tool modules (update\_*×7, set_status\_*×7, adr set_status×1) + fix domain tools/__init__.py + domain __init__.py docstrings + delete 15 old test files + green gates. This phase is big, but coherent: "switch the mutation surface to the generic tools and retire the per-domain ones."

  Hmm, but Phase 3's size: 15 module deletions, 15 test deletions, ~10 docstring updates, plus the new set_status module + its tests. For a single phase-implementer, that's a lot, but the work is mechanical. Alternative: split into 3a (set_status generic + delete 7 set_status\_\* + delete adr set_status) and 3b (delete 7 update\_*). But `update`'s deletion is independent of set_status's name collision — delete update\_* in Phase 2b? Let me restructure:

  - **Phase 2: generic `update` tool** (additive) + tests + gates.
  - **Phase 3: retire `update_*`** — delete 7 modules + 7 test files + fix domain `tools/__init__.py`/`__init__.py` docstrings; `update` remains. Gates green. (vulture check: helpers still in use — fine.)
  - **Phase 4: generic `set_status` tool + retire `set_status_*` + ADR `set_status`** — add the new module (name now free), delete 8 modules (7 domain + ADR) + 8 test files, fix docstrings (adr/tools/__init__.py, server.py ADR tool list). Gates green.
  - **Phase 5: prompts/instruction data rewrite** — 7 update instruction files + qa_refine file + 7 prompt tests updated. Gates green.
  - **Phase 6: docs & registration** — server.py docstring (all changes), AGENTS.md, CHANGELOG, full regeneration (mcp-docs, docs, adr-toc), drift zero. Gates green.
  - **Phase 7: final verification** — walk ACCs, live end-to-end (create→update→set_status per several domains, including adr's superseded_by), scratch-venv? (feat-18 did ACC-007 wheel install for the packaged data — this feature doesn't add any packaged data, but… instruction files already exist and are packaged; no new data files. So no wheel test needed. Maybe just a fresh import check + tool count verification on the actual mcp instance.) Set status to done.

  Wait, ordering issue: Phase 5 (prompts) references the `update`/`set_status` tool names in the text; that works regardless of when the tools are retired. But if we do Phase 5 before Phase 6 (server docstring), the prompt text refers to tools that exist — fine.

  Actually, let me reconsider whether to do Phase 3 (update\_\* retirement) before Phase 4 (set_status). Any dependency? None. Either order works. I'll keep it update-first for symmetry with Phase 2.

  Hmm, another concern about Phase 4: ADR's `set_status` is referenced by ADR's prompt files (adr_update_instructions.md / adr_create_instructions.md probably mention set_status) — and by adr's tests. Deleting `adr/tools/set_status.py` and adding a generic `set_status` (8 types including "adr") preserves the behavior for ADR callers (the tool name `set_status` remains, but the signature gains a required `type` parameter!). Breaking for ADR MCP clients: the old call `set_status(id, status)` fails without `type`. That's the breaking change we decided (user chose full removal). ADR instruction files: adr_update_instructions.md — need to check if it references `set_status`. My earlier grep for "update\_|set_status" across *update*.md showed `update_frontmatter`/`update_section` counts, but that grep only targeted files matching `*update*.md`… which included the adr_update\* files. The grep output only showed update_frontmatter/update_section/update_adr from ADR files — no `set_status` matches in ADR update instruction files. Let me double-check: my grep pattern was `update_\|set_status` against `src/.../*/data/*update*.md` — the output showed no set_status lines for adr files, but the output was filtered by `grep -o "update_[a-z]*\|set_status_[a-z]*"` — note: `set_status_[a-z]*` requires an underscore suffix! ADR's bare `set_status` (no suffix) wouldn't match that -o pattern. So the ADR files might reference bare `set_status` and I'd have missed it. I need to re-grep for the bare `set_status` in the data files.

Also the ADR prompt tests (tests/adr/prompts/test_update_adr.py) assert the text — if the text changes, those tests change too.

Additionally: does the ADR's `create_adr` flow reference set_status? Let me check all references to bare `set_status` across data/\*.md and prompts.

Let me also check whether anything else in src/ references the tools being deleted (e.g., `qa/prompts/refine.py`'s instructions reference update_qa — known). And `docs/MCP.md` gets regenerated (not hand-edited).

Another important check: the `specmgr mcp-docs` command — does it sort tools or preserve registration order? If registration order changes (general imported second now pulls in the domains earlier), the ordering in docs/MCP.md might shift — fine, it's regenerated.

Let me also re-verify how the mcp SDK handles `Literal` in tool parameters — check mcp version / how tools are declared. Look at an existing tool using a non-str parameter: `validate_req(content, full=False)` bool; `list_req(max_results=None, offset=None)` int. No Literal yet in any tool parameter. The MCP python SDK (FastMCP's `mcp.server.MCPServer`? Actually `from mcp.server import MCPServer` — that's the new "mcp" package (modelcontextprotocol python-sdk)'s FastMCP class? The new SDK has `mcp.server.fastmcp.FastMCP`; `mcp.server.MCPServer`… hmm, there's a class in the low-level server. But `@mcp.tool(name=..., title=..., description=...)` decorator with a plain function — this is FastMCP-style. Let me check the mcp package version in uv.lock and skim the tool decorator to confirm it builds schema from annotations (pydantic) — Literal works in pydantic. I'm fairly confident; the plan will include "verify Literal schema renders as enum in docs/MCP.md during Phase 2's gate" as an explicit check.

OK — the remaining loose ends to verify before finalizing the plan:

1. Bare `set_status` references in ADR data files / prompts / tests.
2. mcp SDK version (sanity check).
3. How `/implement-feature` gets invoked (command file exists — the user runs `/implement-feature feat-NNN-slug`).
4. Feature numbering: latest is feat-18. If a GitHub issue exists, the user should know the number; the convention allows feat-0 for no-issue. feat-18's notes say "GitHub issue #18 filed and open." So feature NNN = issue NNN. For this feature, NNN = its issue number (probably 19 if filed). I'll leave it as a placeholder for the user to confirm — actually, I can ask: "What's the issue number for this feature (or 0 if not yet filed)?" That's a genuine loose end. Also the slug: "consolidate-mutation-tools"? The user said "Consolidate all update commands into a single update command." Slug candidates: `feat-NNN-consolidate-update-command` or `feat-NNN-generic-update-set-status`. I'll propose one and let them override.

Let me run the remaining greps.

The orchestration mechanism is now clear (the `/implement-feature` command → `phase-orchestrator` → one `phase-implementer` per phase, each phase having its own quality gate and commit). Before finalizing the phase split, there's one loose end remaining: the new generic tool named `set_status` will **collide** with ADR's existing `set_status` tool name — so I need to verify all references to plain `set_status` and figure out how the ADR prompt file references the tool.

**Tool: bash**

**Input:**

```json
{
  "command": "grep -rn \"set_status\" src/biz/dfch/specmgr/adr/data/ src/biz/dfch/specmgr/adr/prompts/ | grep -v \"set_status_req\\|set_status_\" | head; echo ===; grep -rn \"set_status\" src/biz/dfch/specmgr/*/data/*.md | grep -v \"set_status_[a-z]\" | head; echo ===; grep -rln \"set_status\" tests/adr/ | grep -v pycache; echo ===; grep -n \"mcp\" uv.lock | grep -m2 \"name = \\\"mcp\\\"\\|version\"; grep -rn \"import mcp\\|from mcp\" src/biz/dfch/specmgr/server.py"
}
```

**Output:**

```
grep: src/biz/dfch/specmgr/adr/prompts/__pycache__/update_adr.cpython-313.pyc: binary file matches
grep: src/biz/dfch/specmgr/adr/prompts/__pycache__/create_adr.cpython-313.pyc: binary file matches
grep: src/biz/dfch/specmgr/adr/prompts/__pycache__/create_adr_test.cpython-313.pyc: binary file matches
src/biz/dfch/specmgr/adr/data/adr_update_instructions.md:28:  decision, or marking it superseded) -> `set_status(id, status,
src/biz/dfch/specmgr/adr/data/adr_update_test_instructions.md:40:  decision, or marking it superseded) -> `set_status(id, status,
src/biz/dfch/specmgr/adr/data/adr_create_instructions.md:51:   call `set_status(id, "accepted")` (or `"rejected"`, or
src/biz/dfch/specmgr/adr/data/adr_create_test_instructions.md:76:   `set_status(id, "accepted")` (or `"rejected"`, or `"proposed"`).
src/biz/dfch/specmgr/adr/prompts/create_adr_test.py:36:(``create_adr``, ``option_create``, ``set_status``, ``validate_adr``).
src/biz/dfch/specmgr/adr/prompts/create_adr_test.py:62:        "the same MADR-4.0.0 structure and create_adr/option_create/set_status/validate_adr "
src/biz/dfch/specmgr/adr/prompts/update_adr.py:23:``update_frontmatter``, ``set_status``, ``option_create``/``option_update``/
src/biz/dfch/specmgr/adr/prompts/create_adr.py:22:``adr/tools/`` surface (``create_adr``, ``option_create``, ``set_status``,
src/biz/dfch/specmgr/adr/prompts/create_adr.py:55:        "required information, and driving create_adr/option_create/set_status/"
===
src/biz/dfch/specmgr/adr/data/adr_create_instructions.md:51:   call `set_status(id, "accepted")` (or `"rejected"`, or
src/biz/dfch/specmgr/adr/data/adr_create_test_instructions.md:76:   `set_status(id, "accepted")` (or `"rejected"`, or `"proposed"`).
src/biz/dfch/specmgr/adr/data/adr_update_instructions.md:28:  decision, or marking it superseded) -> `set_status(id, status,
src/biz/dfch/specmgr/adr/data/adr_update_test_instructions.md:40:  decision, or marking it superseded) -> `set_status(id, status,
===
tests/adr/prompts/test_create_adr_test.py
tests/adr/prompts/test_update_adr.py
tests/adr/prompts/test_update_adr_test.py
tests/adr/prompts/test_create_adr.py
tests/adr/tools/test_set_status.py
===
131:    { name = "mcp" },
146:    { name = "mcp" },
188:from mcp.server import MCPServer

```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 47.5s)

_Thinking:_

Important finding: The ADR instruction data file references `set_status(id, status, ...)` — meaning **4 ADR data files** (adr_create_instructions.md, adr_create_test_instructions.md, adr_update_instructions.md, adr_update_test_instructions.md) **plus 4 ADR prompt test files** also need to be updated (to `set_status(id, type="adr", status, ...)`). My earlier plan only covered the 7 domain update instruction files + qa_refine — the ADR side was missing. Good catch. This changes Phase 5 to "Prompt and instruction data rewrite (all domains + ADR)".

Also, the module docstrings of the ADR prompts reference `set_status` (create_adr.py, update_adr.py, create_adr_test.py) — these are Python docstrings mentioning the tool surface, and the tool name `set_status` still exists (now in general), so the mention remains valid. The docstrings of adr/tools/__init__.py enumerate the tools — that one has to be updated (set_status leaves adr/tools).

Let me check the version of the mcp SDK more precisely. The grep of uv.lock wasn't helpful. Let me confirm: `grep -A3 'name = "mcp"' uv.lock`. Actually, this relates to whether the `Literal` type works in the tool schema — the SDK probably uses pydantic to build the schema from annotations. Let me quickly verify how the tool decorator inspects the signature. In fact, `@mcp.tool()` on a plain function in this SDK version (from mcp.server import MCPServer — the new unified `mcp` package, probably v1.x) builds an input schema via pydantic's TypeAdapter — Literal works and produces "enum". Let me quickly confirm the mcp version and whether fastmcp is vendored.

Let me quickly check the mcp version in uv.lock and, if needed, the signature of the tool decorator inside the installed package. This is a "nice to have" level of verification. The phase gate (mcp-docs regeneration + checking whether the `update` entry in docs/MCP.md shows the enum) will catch any problem anyway. I'll just note it in the plan as an explicit Phase 2 verification item.

Let me get the mcp version.

The ADR side also needs to be updated — the 4 ADR instruction files reference `set_status(id, ...)`, and the 4 ADR prompt tests assert against them. Good catch. This extends the prompt rewrite phase. Next, I'll do a quick sanity check on the MCP SDK version for `Literal` schema support:

**Tool: bash**

**Input:**

```json
{
  "command": "grep -B2 -A8 '^name = \"mcp\"$' uv.lock | head -20; echo ===; uv run --frozen python -c \"\nimport inspect\nfrom mcp.server import MCPServer\nfrom typing import Literal\nimport mcp\nprint('mcp version:', getattr(mcp, '__version__', 'unknown'))\n\" 2>&1 | tail -5"
}
```

**Output:**

```

[[package]]
name = "mcp"
version = "2.0.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "anyio" },
    { name = "httpx2" },
    { name = "jsonschema" },
    { name = "mcp-types" },
    { name = "opentelemetry-api" },
===
mcp version: unknown

```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 198.5s)

_Thinking:_

MCP SDK 2.0.0 — new package structure (mcp-types, httpx2). The tool decorator builds input schema from annotations, probably via pydantic/jsonschema. `Literal` → JSON schema enum is standard. The Phase 2 gate explicitly includes verification that `docs/MCP.md` renders `type` as an enum — this is the safety net.

Now, to shape the ADR creation task, let me also double-check the ADR example template (specmgr_get_adr? no—there's a create_adr MCP tool with options). ADR body needs: title, context_and_problem_statement, considered_options, decision_outcome (required); decision_drivers, consequences, confirmation, more_information, options (pros/cons) are optional. The plan should specify the ADR's content skeleton (options: type + id vs uuid-only vs keep per-domain; outcome: type + id, ADR excluded from update, included in set_status with superseded_by).

Now, assembling the final adjusted plan. Main adjustments from previous plan:

1. **Feature scaffolding as explicit first step** (before orchestration): create `.specmgr/feat/feat-NNN-slug/README.md` with full phase task list (following ADR e369ee2e / template v1), frontmatter is status planning→in-progress. Slug + NNN: need from user (issue number; use 0 if unfiled). Propose `feat-NNN-consolidate-mutation-tools`.

2. **ADR as Phase 1** of orchestrated execution (created via `specmgr_create_adr` MCP tool per ADR 898bfcd0 "Author ADRs only through MCP structured tools", never hand-write), `specmgr adr-toc` regen, phase-end gate.

3. **Phases** (each phase ends with a full quality gate: ruff format --check, ruff check, vulture, full unittest, + drift checks for specmgr docs/mcp-docs/adr-toc/schema as relevant; and phase-implementer updates README Progress; orchestrator re-verifies and does 1 Conventional Commit per phase):

   - Phase 1: ADR (docs/adr + adr-toc).
   - Phase 2: generic `update` tool in `general/tools/update.py` (7 adapters, dispatch, mcp tool, register in general/tools/__init__.py) + `tests/general/tools/test_update.py` + new import-order smoke test. Gate includes: verify Literal renders as enum in MCP.md; full suite green (old tools still coexist — that's fine).
   - Phase 3: retire the 7 `update_*` tools: delete modules + 7 test files; fix 7 `tools/__init__.py` + 7 domain `__init__.py` docstrings; server.py tool-list docstring (update lines) — hmm, server.py docstring: do I update per-phase or in final docs phase? server.py's docstring is "single most authoritative list… update whenever you add/remove/rename a resource, tool, or prompt". So each phase that changes the surface must update server.py's docstring in the same phase (else it's inconsistent; though docs drift checks only cover docs/ not server.py). Pre-commit runs `specmgr docs` hook scoped to src changes — docs/api is generated from docstrings, and pre-commit's local `specmgr docs` hook is scoped to src/\*\*/\*.py changes, so if server.py docstring lags… it just regenerates docs from whatever docstring is present; no failure. But the convention is to keep in sync. Decision: update server.py docstring in each phase that changes the surface (Phase 2 adds `update` to General tools list; Phase 3 removes 7 update_X lines; Phase 4 adds set_status + removes 7 set_status_X + ADR set_status line; Phase 5 prompt list unchanged (prompt count same); Phase 6 AGENTS.md/CHANGELOG + final regen).
   - Phase 4: generic `set_status` (8 adapters incl ADR with superseded_by) + retire 7 `set_status_*` + ADR `set_status` (name collision forces same phase) + 8 test file deletions + docstring fixes (incl adr/tools/__init__.py) + server.py line.
   - Phase 5: rewrite prompt/instruction data: 7 `*_update_instructions.md` + `qa_refine_instructions.md` + 4 ADR instruction files (set_status call shape) + 7 domain prompt test updates + 4 ADR prompt test updates. Gate: full suite.
   - Phase 6: cross-cutting docs: AGENTS.md (per-domain bullets + general bullet + "missing" list), CHANGELOG [Unreleased] breaking entries, final regen of specmgr docs + mcp-docs + adr-toc (+ schema? no model changes → schema unchanged), zero-drift verification, fresh import + tool count verification against real mcp instance (expect 74 − 14 + 2 = 62 tools… wait, let me count: current 74 tools (from feat-18 ACC-004). Remove 7 update_X + 7 set_status_X + 1 ADR set_status = 15; add 2 → 61 tools. Recheck: 74 − 15 + 2 = 61. Resources 20, prompts 17 unchanged.)
   - Phase 7: final verification: walk all ACCs with evidence (live end-to-end create→update→set_status against several domains incl ADR's superseded_by; live check of MCP registration counts; live demo of per-domain status vocab), set feature status done, close out.

4. **Acceptance criteria** (mapped to requirements):

   - ACC-001: `update` tool registered, dispatches all 7 types, whole-body replacement semantics preserved (frontmatter carried, updated bumped, status not settable), validation failure writes nothing, unknown id → domain NotFound. (Phase 2/3)
   - ACC-002: `set_status` tool registered for 8 types; per-domain closed status vocab enforced; ADR's superseded_by composition works; superseded_by rejected for non-adr. (Phase 4)
   - ACC-003: 15 per-domain/ADR mutation tools removed from source and registration; no dangling references (grep clean); vulture clean. (Phases 3/4)
   - ACC-004: all prompt narration files (11 data files) reference the generic tools; prompt tests green. (Phase 5)
   - ACC-005: docs zero drift (docs/api, docs/MCP.md, docs/adr/README.md); server.py docstring authoritative list accurate; AGENTS.md updated; CHANGELOG breaking note. (Phase 6)
   - ACC-006: ADR recorded + accepted; live end-to-end mutation runs across ≥3 domains + ADR superseded_by on a temp docs dir; tool counts verified on real mcp instance (61 tools/20 resources/17 prompts); fresh import smoke test green. (Phase 7)
   - ACC-007: per-phase gate discipline — every phase's gate recorded with evidence in README Progress (this is process ACC; orchestrator enforces).

5. **Orchestration**: after README+ADR plan exists… wait, ADR is Phase 1 (delegated). So pre-orchestration step is only: (a) I create feature README (with this full plan embedded) once out of plan mode. Then user runs `/implement-feature feat-NNN-consolidate-mutation-tools` (phase-orchestrator), drives Phases 1–7, one fresh phase-implementer per phase, per-phase Conventional Commit with user confirmation.

   Alternative: I could also do the README creation as part of "step 0" that I execute directly (I'm the primary agent with write access; the orchestrator refuses edits — that's why step 0 is mine, not delegated).

   Hmm — wait. Should the README creation itself be delegated to a sub-agent (implementation-specialist)? No: creating the feature README is planning artifact authorship — the main agent does it directly (or user reviews). That's what feat-18's flow did (README authored in planning session). Keep as step 0 by me.

6. **Loose ends to confirm with user**:

   - Feature NNN (GitHub issue number) or 0? And slug?
   - Commit policy: orchestrator asks for confirmation per phase commit — fine, note it.
   - Anything else? `type` parameter name shadowing built-in — ruff clean (verified). Return type union — fine.

   Also: does user want me to execute step 0 right after plan approval and then hand off to `/implement-feature`? That's the natural flow.

One more check — Phase 2 smoke test placement: `tests/general/tools/test_update.py` or a separate `tests/test_server_import.py`? There's tests/test_package.py and tests/resources/. A new test file under tests/general/tools/ named test_update.py can include a test that imports server fresh (importlib + subprocess?). Simpler: test that `from biz.dfch.specmgr.server import mcp` works and `mcp.list_tools()` (async) contains "update". Existing tests already import server (tests/resources? let's not over-engineer; the plan says: include a registration smoke test in Phase 2 that asserts on the set of tool names via asyncio.run(mcp.list_tools()), plus a fresh-process `python -c "import biz.dfch.specmgr.server"` run inside the gate.

Actually — how do existing tests assert registered tool names? feat-18's ACC-004 did "live asyncio.run(mcp.list_tools())". So a helper exists or they ran it inline. The plan can just say mirror that.

Also on vulture: after deleting 15 modules, some private helper symbols become test-only referenced → `specmgr unused-code --test` is advisory (not enforced); the enforced vulture check scans src only. Domain `_write.py` etc. still used by create\_*. `ensure_X_base_dir` still used by create\_*. OK. But: `ReqNotFoundError` etc. still raised by find_req_path (used by get_req, list_req). Fine.

One more: `qa/prompts/refine.py`'s docstring/instructions — refine narrates appending question then calling `update_qa` (lines 78–86 of qa_refine_instructions.md). Covered by Phase 5.

`tsk/prompts/implement_task.py` — does it reference update_tsk? It reads the task list via get_tsk, builds TodoWrite… earlier grep for "update\_" showed no tsk implement file in the data grep results for *update*.md (only tsk_update_instructions.md). tsk_implement_instructions.md might mention update_tsk? My data grep only targeted `*update*.md`. Let me not miss: in Phase 5, task = "grep all src/\*\*/data/\*.md for `update_[a-z]+` and `set_status` and update every hit", which is comprehensive. The 7 update instructions + qa_refine (update_qa hits) + ADR's 4 (set_status hits) + maybe others (create instructions? tsk_implement?). Phase 5 task text should be grep-driven to catch all.

OK. Also on CHANGELOG: check CHANGELOG.md exists with [Unreleased] — yes, per AGENTS.md.

Version note: no pyproject version bump in this feature (release-time concern).

Now — how to present: user asked "walk the plan and adjust as needed". So my answer: the adjusted plan (phased for orchestration), explicit changes from v1 (ADR name collision forces Phase 4 bundling; ADR prompt files added to Phase 5; per-phase gates + commits; step 0 scaffolding; ACC list; orchestration handoff), plus 1–2 confirmations (issue number/slug; confirmation of handoff flow).

Should I ask the issue number question with the `question` tool? That's the only real loose end. Slug: propose `consolidate-mutation-tools`. Actually, user's feature title: "Consolidate all update commands into a single update command" — with set_status added, "mutation tools" fits. Let me ask for the NNN (with 0 option). Also confirm the execution handoff: "After approval, I create the README (step 0), then you run /implement-feature" — or user might want me to continue in this session as orchestrator? I can't (phase-orchestrator not in my task agent list, and it's a primary mode agent — user has to select it). Let me state that explicitly: orchestration runs via `/implement-feature feat-NNN-...` command (which binds agent: phase-orchestrator).

Let me write the final plan concisely but completely. Structure:

1. Adjustments vs. previous plan (short bullets).
2. Step 0 (me, pre-orchestration): feature README + frontmatter, content = plan below.
3. Feature plan (what goes in README):
   - Title/id/slug
   - Requirements REQ-001..00x
   - ACC-001..007
   - Scope in/out
   - Design notes (dispatch table, adapters verbatim, name collision resolution, import order, literal enum, return union, per-domain status vocab table, error types preserved)
   - Phase task list (7 phases, each with phase-end gate task + progress update task)
   - Related ADRs
4. Orchestration and verification loop (per phase: implementer → orchestrator re-runs gate → commit with user confirmation → advance).
5. Final question: NNN + slug confirmation.

Keep it tight. The plan text will be long but it's a planning document — that's what plan mode asks for. Let me draft.

Phase task list details:

**Phase 1: ADR**

- 1.1: Create ADR via specmgr_create_adr MCP tool (never hand-write, ADR 898bfcd0): title "Consolidate whole-body update and status-change tools into generic type-dispatched tools"; context: 7 near-identical update_X + 7 set_status_X + ADR set_status, 15 tools, future domain ac would add more; options considered: (1) type+id dispatch generic tools [chosen], (2) uuid-only resolution (scan all dirs), (3) keep per-domain; decision drivers: tool surface simplicity, no write-path dir scan, no uuid collision ambiguity, LLM client already knows domain; outcome + consequences (breaking: 14 tools removed, ADR set_status signature gains required type; ADR excluded from update by design — section-level MADR contract; future domains add dispatch entry only); status accepted (or draft→accepted? create with status proposed, then set_status? feat practice: ADR created via tool; status field — just create with "accepted" directly since decision is made. Hmm, ADR lifecycle: create as "proposed" and confirm via set_status "accepted"? User has already decided (via Q&A). Let's create with status: accepted.)
- 1.2: Regen specmgr adr-toc; verify docs/adr/README.md includes new ADR.
- 1.3: Phase-end gate: full (ruff format/check, vulture, unittest) + adr-toc drift zero; update README Progress.

**Phase 2: Generic `update` tool (additive)**

- 2.1: `general/tools/update.py` — 7 private adapter functions, 1:1 port of current `update_<d>` bodies (preserving per-domain lock/load_by_id/frontmatter-carry/updated-bump/write_X_file/XNotFoundError); dispatch table `dict[str, adapter]` with module-level ALL_CAPS type-name constants; `@mcp.tool(name="update", title="Update document", description=...)` `def update(id: str, type: Literal["req","uc","tsk","qa","prb","gol","rsk"], content: str) -> ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument | GolDocument | RskDocument`; follow conventions (assert, result naming, docstrings).
- 2.2: Register in `general/tools/__init__.py` (import + __all__ + docstring).
- 2.3: `server.py` module docstring: add `update` to General tools line (authoritative list discipline).
- 2.4: `tests/general/tools/test_update.py` — per-type (parameterized over 7): body replacement, frontmatter preserved (id/type/status/created/version), updated bumped, status not settable; invalid content → AssertionError/ValidationError, file unchanged; unknown id → domain XNotFoundError; docstring-level: `type` accepted only as enum (schema check).
- 2.5: Registration smoke test: fresh import of server + asyncio mcp.list_tools() contains "update"; plus subprocess `python -c "import biz.dfch.specmgr.server"` inside gate (import order: general pulls domains in earlier).
- 2.6: Phase-end gate: full + `specmgr mcp-docs`/`specmgr docs` regen (drift zero after regen) + verify MCP.md renders `type` as 7-value enum; update Progress.

**Phase 3: Retire per-domain `update_*`**

- 3.1: Delete 7 modules req/uc/tsk/qa/prb/gol/rsk `tools/update_<d>.py` (or update_uc etc. — exact names: update_req, update_uc, update_tsk, update_qa, update_prb, update_gol, update_rsk).
- 3.2: Delete 7 test files tests/<d>/tools/test_update\_<d>.py (update_uc → test_update_uc.py etc.).
- 3.3: Fix 7 domain `tools/__init__.py` (import, __all__, docstring tool list) + 7 domain `__init__.py` docstrings (tool enumeration).
- 3.4: `server.py` docstring: remove 7 `update_<d>` from per-domain tool lines (keep set_status lines for now).
- 3.5: Grep verification: no `update_<d>` references left in src/ (prompt Python docstrings that narrate the surface — e.g. req/prompts/update_req.py docstring mentions update_req tool — those are prompt narration files; their data files still reference update_req until Phase 5. Hmm — src/ grep will hit: 7 prompts' Python module docstrings + data md files. Should Phase 3 fix Python docstrings, or leave all text to Phase 5? Cleaner: Phase 3 fixes only code + Python docstrings in the tool modules' __init__ files; prompt data files + prompt Python docstrings → Phase 5 (single "narration" phase). But then server.py docstring (Phase 3) vs prompt docstring (Phase 5) — the server docstring enumerates tools, not prompt text, so fine. Phase 5 handles all \*.md data + prompt \*.py docstrings + their tests. OK, note this split explicitly to avoid implementer guessing: "Phase 3 touches no prompt data files; Phase 5 owns all narration text."
- 3.6: Phase-end gate: full + docs/mcp-docs regen drift zero + Progress update.

**Phase 4: Generic `set_status` + retire `set_status_*` + ADR `set_status`**

- 4.1: `general/tools/set_status.py` — 8 adapters: 7 ported verbatim from `set_status_<d>` (raw body re-read, frontmatter rebuild via domain class so closed vocab validates, updated bump), ADR ported from `adr/tools/set_status.py` (mutations.set_status with superseded_by composition, write_adr render); guard: `superseded_by` given with type != "adr" → ValueError (message per convention); dispatch table; `@mcp.tool(name="set_status", ...)` `def set_status(id: str, type: Literal["req","uc","tsk","qa","prb","gol","rsk","adr"], status: str, superseded_by: str | None = None) -> <union of 8>`.
- 4.2: Delete `adr/tools/set_status.py` + 7 domain `set_status_<d>.py` + 8 test files (tests/adr/tools/test_set_status.py + 7 domain).
- 4.3: Register in `general/tools/__init__.py`; fix `adr/tools/__init__.py` (import/__all__/docstring) + 7 domain `tools/__init__.py` + 8 domain `__init__.py` docstrings.
- 4.4: `server.py` docstring: remove 7 set_status\_<d> + ADR set_status from domain lines; add `set_status` to General tools line.
- 4.5: `tests/general/tools/test_set_status.py` — per-type (8): status change + updated bump + body unchanged (byte-identical raw body for 7, ADR render roundtrip); per-domain closed vocab enforcement (e.g. "implemented" rejected for rsk? — rsk vocab is open/mitigating/... so use a value from a different domain as negative case, and ADR "superseded" + superseded_by composition "superseded by <id>"); superseded_by with non-adr → ValueError; unknown id → domain NotFound.
- 4.6: Phase-end gate: full + docs/mcp-docs regen + Progress update.

**Phase 5: Narration (prompts + instruction data)**

- 5.1: Grep-driven rewrite of all `src/**/data/*.md` hits of `update_<d>`/`set_status_<d>`/bare `set_status(`: 7 `*_update_instructions.md` (→ `update(id, type="<d>", content)`, `set_status(id, type="<d>", status)`, fix per-domain status vocab prose where different — rsk open/mitigating/…, uc 5-value), `qa_refine_instructions.md` (update_qa hits), 4 ADR instruction files (→ `set_status(id, type="adr", status[, superseded_by])`).
- 5.2: Fix prompt Python module docstrings that name the retired tools (7 `prompts/update_<d>.py` + ADR `prompts/create_adr.py`, `create_adr_test.py`, `update_adr.py`, `update_adr_test.py` docstring tool-surface mentions — keep accurate: `set_status` still exists, now in general).
- 5.3: Update 7 domain prompt tests + 4 ADR prompt tests asserting narration text.
- 5.4: Phase-end gate: full + Progress update (no doc drift expected — prompt text is data; but specmgr docs regen if prompt docstrings changed → include in gate).

**Phase 6: Cross-cutting docs & release notes**

- 6.1: AGENTS.md — per-domain bullets remove update\_<d>/set_status\_<d>; general bullet adds `update`/`set_status`; "still missing" list updated (delete\_\* stub line unchanged; validate line unchanged); server.py section line unchanged.
- 6.2: CHANGELOG.md [Unreleased] — Breaking: 14 tools removed (7 update\_<d>, 7 set_status\_<d>), ADR `set_status` signature gains required `type` (first-class), Added: generic `update`/`set_status`.
- 6.3: Final regen: specmgr docs + mcp-docs + adr-toc (+ schema: verify no drift, models unchanged) → zero drift.
- 6.4: Phase-end gate: full + Progress update.

**Phase 7: Final verification**

- 7.1: Walk all ACCs with concrete evidence; live end-to-end in a temp SPECMGR_DOCS_DIR: for ≥3 domains (req, rsk, uc) create\_<d> → get\_<d> → update(id, type, content) → set_status(id, type, status) → verify; ADR: create_adr → set_status(id, type="adr", status="superseded", superseded_by=…) → verify composed string; verify tool counts against real mcp instance (61 tools / 20 resources / 17 prompts); fresh import subprocess check.
- 7.2: Set feature frontmatter status to done; final Progress update.

Tool count: currently 74 (feat-18 ACC-004). Remove 15, add 2 → 61. Note: that count was "as of feat-18" — might have changed since (feat-18 was done 2026-08-26, today). Let me quickly verify current tool count from docs/MCP.md header. Actually, let me grep the header line of docs/MCP.md.

One quick fact-check for the acceptance criteria (current tool/resource/prompt counts):

**Tool: bash**

**Input:**

```json
{
  "command": "head -8 docs/MCP.md; grep -c \"^### Tool:\" docs/MCP.md"
}
```

**Output:**

```
# MCP Server Reference

Auto-generated from the live `biz.dfch.specmgr.server:mcp` registration --
do not edit by hand, run `specmgr mcp-docs` instead (see `AGENTS.md`).

25 resource(s), 1 resource template(s), 84 tool(s), 19 prompt(s).

## Table of Contents
84

```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 297.4s)

_Thinking:_

Current: 25 resources, 84 tools, 19 prompts (increased since feat-18's 20/74/17 — ac or other features have been added). After this feature: 84 − 15 + 2 = **71 tools**, 25 resources, 19 prompts (no change).

Now I have all the info I need. Let me write the final adjusted plan. Structure it around:

1. Adjustments from the previous plan (why the phases changed)
2. Step 0 — scaffolding (me, before orchestration)
3. Feature README content: requirements, ACC, scope, design notes, phases with tasks
4. Orchestration loop
5. One open question: issue number / slug

Keep it as concise as possible while remaining complete. This is the plan the user approves.

All verified. Here's the adjusted plan, shaped for phase-orchestrator/phase-implementer execution.

## Adjustments vs. the previous plan

1. **ADR's existing `set_status` tool name collides** with the new generic `set_status`. Registering the generic one while the ADR tool still exists would double-register the name, so "add generic `set_status`" and "delete ADR `set_status`" must land in the **same phase**. This forced a re-cut: the old tools are retired in dedicated phases, each leaving the repo gate-green.
2. **ADR narration files are in scope now**: 4 ADR instruction files (`adr_create/_test/_update/_update_test_instructions.md`) reference `set_status(id, …)` and 4 ADR prompt tests assert their text — the generic tool's new signature breaks them.
3. **Every phase ends with the full quality gate** (ruff format/check, vulture, full `unittest` suite, plus `specmgr docs`/`mcp-docs`/`adr-toc`/`schema` drift checks the phase touches) and a README Progress update — the feat-18 per-phase discipline, which is exactly what the `phase-implementer` agent's default gate runs and what the orchestrator independently re-runs before committing one Conventional Commit per phase.
4. **`server.py` docstring is updated inside each phase that changes the surface** (it's the authoritative list; updating it only at the end would leave mid-feature inconsistency).
5. Current live registration is **84 tools / 25 resources / 19 prompts** → target **71 / 25 / 19** (−15 +2).

## Step 0 — scaffolding (done by me, before orchestration starts)

Create `.specmgr/feat/feat-NNN-consolidate-mutation-tools/README.md` from `.specmgr/_template/v1/README.md` containing the full plan below (frontmatter `status: planning` → `in-progress` once Phase 1 starts). The orchestrator reads *this file* to drive the phases, so it must exist before `/implement-feature` runs. No ADR here yet — the ADR is Phase 1 work, delegated.

## Feature plan (content of the README)

**Requirements**

- REQ-001: `update(id, type, content)` — generic whole-body replace for the 7 whole-body domains; `type: Literal["req","uc","tsk","qa","prb","gol","rsk"]`; per-domain semantics preserved 1:1 (domain lock, `load_by_id`, frontmatter carry-over, `updated` bump, domain `XNotFoundError`, two-channel validation).
- REQ-002: `set_status(id, type, status, superseded_by=None)` — for all 8 types incl. `adr`; per-domain closed status vocab enforced via each domain's `XFrontmatter` reconstruction; `superseded_by` composes `"superseded by X"` for `adr` only, rejected (`ValueError`) otherwise.
- REQ-003: Remove 15 tools: `update_req/uc/tsk/qa/prb/gol/rsk`, `set_status_req/uc/tsk/qa/prb/gol/rsk`, ADR `set_status`.
- REQ-004: All narration (prompt data files + prompt docstrings + their tests) references the generic tools.
- REQ-005: Docs/registration consistent: `server.py` docstring, `docs/MCP.md`, `docs/api/`, `docs/adr/README.md`, `AGENTS.md`, `CHANGELOG.md`.
- REQ-006: ADR records the convention (explicit `type` over uuid-only; ADR excluded from `update`, included in `set_status`; future domains add a dispatch entry, no new tool).

**Acceptance criteria** — ACC-001…ACC-007 mapping 1:1 to REQ-001…006 (behavioral evidence per type, removed-surface grep clean, narration grep clean, zero doc drift, ADR accepted + live end-to-end runs across ≥3 domains + ADR `superseded_by`, tool counts 71/25/19 on the real `mcp` instance, fresh-import smoke test).

**Design notes** (in README): adapters are verbatim ports into `general/tools/{update,set_status}.py` with a small dispatch table; domain private helpers (`_io`/`_write`/`_lock`/`_paths`) stay in-domain and untouched; import-order risk (`general` pulls domain packages earlier in `server.py:211`) is bounded by the existing partial-init `from ...server import mcp` pattern and covered by the smoke test; return type is the 7/8-way document union; ruff (E/F/W only) is clean on the `type` parameter name; status vocabularies differ per domain (req 7-value, rsk `open`/`mitigating`/…, uc 5-value, ADR 6 + `superseded by` pattern) — the dispatch keeps each validator authoritative.

**Phases** (each phase's last task = phase-end quality gate + Progress update):

| Phase | Content | Gate adds |
|---|---|---|
| 1 — ADR | Create ADR via `specmgr_create_adr` (never hand-written, ADR 898bfcd0), status `accepted` | `specmgr adr-toc` drift |
| 2 — Generic `update` (additive) | `general/tools/update.py` (7 adapters + dispatch + tool), register in `general/tools/__init__.py`, `server.py` docstring +`update`, `tests/general/tools/test_update.py` (all 7 types, negative cases), fresh-import + `list_tools()` smoke test | `mcp-docs`/`docs` regen; verify `type` renders as 7-value enum in MCP.md |
| 3 — Retire `update_*` | Delete 7 tool modules + 7 test files; fix 7 `tools/__init__.py` + 7 domain `__init__.py` docstrings; `server.py` −7 lines; **no prompt data files touched** (Phase 5 owns narration) | `mcp-docs`/`docs` regen, zero drift |
| 4 — Generic `set_status` + retire 8 | `general/tools/set_status.py` (8 adapters + `superseded_by` guard), delete ADR `set_status` + 7 `set_status_*` + 8 test files, registration/docstring fixes, `server.py`, `tests/general/tools/test_set_status.py` (all 8 types, vocab negatives, composition) | `mcp-docs`/`docs` regen, zero drift |
| 5 — Narration | Grep-driven rewrite of every `src/**/data/*.md` hit: 7 `*_update_instructions.md`, `qa_refine_instructions.md`, 4 ADR instruction files; prompt Python docstrings (7 `prompts/update_*` + 4 ADR prompt modules); update 11 prompt test files | full gate; `docs` regen (docstring changes) |
| 6 — Cross-cutting docs | `AGENTS.md` (per-domain bullets, `general` bullet, "missing" list), `CHANGELOG.md` `[Unreleased]` breaking entry, final regen of `docs` + `mcp-docs` + `adr-toc` + `schema` (models unchanged → expect no drift) | zero drift everywhere |
| 7 — Final verification | Walk all ACCs with evidence; live end-to-end in temp `SPECMGR_DOCS_DIR`: `create_<d>`→`get_<d>`→`update`→`set_status` for req/rsk/uc, ADR `set_status(…, type="adr", superseded_by=…)` composition check; confirm 71/25/19 on real `mcp`; set README `status: done` | full gate |

**Orchestration**: after Step 0, run the repo's `/implement-feature feat-NNN-consolidate-mutation-tools` command — it binds `phase-orchestrator`, which reads the README, keeps a per-phase todo list, delegates each phase to a **fresh** `phase-implementer` (one phase per subagent, dependency order), independently re-runs each phase's gate, then commits the phase as one Conventional Commit **with your confirmation**, and surfaces any blocker/question to you rather than guessing.

Two things I need from you before Step 0:

**Tool: question**

**Input:**

```json
{
  "questions": [
    {
      "header": "Issue number",
      "options": [
        {
          "description": "No GitHub issue filed yet; per ADR e369ee2e the id stays feat-0-consolidate-mutation-tools until an issue exists.",
          "label": "0 (no issue yet)"
        },
        {
          "description": "An issue is filed (or will be filed before Step 0) — tell me the number, e.g. 19.",
          "label": "Issue number: type it"
        }
      ],
      "question": "What GitHub issue number does this feature use for its feat-NNN id?"
    },
    {
      "header": "Execution flow",
      "options": [
        {
          "description": "On approval I create the README (Step 0) in this session, then you run /implement-feature to hand off to the phase-orchestrator.",
          "label": "Step 0 now, then /implement-feature (Recommended)"
        },
        {
          "description": "Keep this session purely plan-mode; you create/approve the README yourself, then run /implement-feature.",
          "label": "You handle Step 0"
        }
      ],
      "question": "How should Step 0 (feature README creation) and the hand-off happen?"
    }
  ]
}
```

**Output:**

```
User has answered your questions: "What GitHub issue number does this feature use for its feat-NNN id?"="0 (no issue yet)", "How should Step 0 (feature README creation) and the hand-off happen?"="Step 0 now, then /implement-feature (Recommended)". You can now continue with the user's answers in mind.
```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 109.1s)

_Thinking:_

User has confirmed:

- `feat-0-consolidate-mutation-tools` (no issue yet)
- Create the README (step 0) right now upon approval, then hand off to `/implement-feature`

Plan is complete. Let me concisely present the final plan summary. Since I'm in plan mode, the final deliverable is the plan itself. I've already presented the detailed plan in the previous message. All that's left is to wrap up with the finalized details (id, flow) — short and concise. The plan is as follows:

1. Step 0: Create `.specmgr/feat/feat-0-consolidate-mutation-tools/README.md` (full plan: REQ-001..006, ACC-001..007, scope, design notes, phase task list including per-phase gate tasks, Progress section, frontmatter id: feat-0-consolidate-mutation-tools, version 1.0.0, status: planning, created/updated 2026-08-26).
2. Handoff: User runs `/implement-feature feat-0-consolidate-mutation-tools`.

Present the final integrated plan compactly (don't repeat the whole table — just confirm the final state and the remaining details). Actually, in plan mode, the final message should be a complete plan for approval. The previous message already contained it. What I should present now is: a concise confirmation of the finalized plan including the resolved details, so that the user can approve execution. Keep it short.

Locked in. Final plan:

**Feature id:** `feat-0-consolidate-mutation-tools` (no issue yet; the `NNN` infix stays `0` per ADR e369ee2e until one is filed).

**Step 0 (me, right after approval):** create `.specmgr/feat/feat-0-consolidate-mutation-tools/README.md` from the v1 template with:

- frontmatter (`id: feat-0-consolidate-mutation-tools`, `version: 1.0.0`, `status: planning`, dates 2026-08-26)
- the full plan as specified above: REQ-001…006, ACC-001…007 (with the 71/25/19 tool-count target), Scope (in/out, incl. the ADR-exclusion-from-`update` and per-domain status-vocabulary notes), Design Notes (verbatim adapters + dispatch table in `general/tools/`, import-order smoke test, `Literal` enum, union return types), and the **7-phase Task List** where every phase ends with its phase-end quality-gate task (full ruff/vulture/unittest + the drift checks that phase touches) and a README Progress update:
  1. ADR (via `specmgr_create_adr`, `adr-toc`)
  2. Generic `update` tool — additive, 7 types, tests + import smoke test
  3. Retire the seven `update_*` tools + tests + docstrings (no narration files)
  4. Generic `set_status` tool — 8 types incl. ADR with `superseded_by` guard + retire 8 old tools (name-collision forces one phase)
  5. Narration: all 11 instruction data files + prompt docstrings + 11 prompt test files, grep-driven
  6. Cross-cutting docs: `AGENTS.md`, `CHANGELOG.md` breaking entry, final zero-drift regeneration
  7. Final verification: ACC walk with live end-to-end evidence (req/rsk/uc + ADR `superseded_by`), registration counts on the real `mcp` instance, `status: done`

**Hand-off (you):** run `/implement-feature feat-0-consolidate-mutation-tools`. The phase-orchestrator then drives Phases 1–7, one fresh phase-implementer per phase, independently re-running each phase's gate, with one Conventional Commit per phase after your confirmation, and questions/blockers surfaced to you directly.

Nothing else is pending — approve and I'll write the README.

---

## User

1. I want the update tool to support optional line parameters, begin, end. With this, it is possible to update an artifact partially without sending the complete contents. If no parameter is given, the complete file is updated (as it behaves today). This can make tool calls faster and smaller. Does this make sense?
2. use "Recent Updates" instead of "Updates"

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 364.3s)

_Thinking:_

The user is asking two things:

1. Add optional `begin`/`end` line parameters to the `update` tool so that artifacts can be partially updated without sending the full content. If the parameters aren't specified, the whole file is updated (current behavior). Question: "Does this make sense?"

2. Use "Recent Updates" instead of "Updates" — this probably refers to the Recent Updates section of the feature README (I wrote "README Progress update" and a "Recent Updates entry" — or maybe the phase task description said "Updates"? Let me check: in my plan I wrote "a dated Recent Updates entry" in various places. In the Phase 1 plan description I wrote "update this README's Progress section". Hmm, the user says use "Recent Updates" instead of "Updates" — maybe my plan wording used "Updates" somewhere. In the table I wrote "Progress update"… actually the template section is named "### Recent Updates". Perhaps in the phase-task spec I wrote "a dated Updates entry"? Let me look at the previous message: "where every phase ends with its phase-end quality-gate task (full ruff/vulture/unittest + the drift checks that phase touches) and a README Progress update". That says "Progress update". Earlier in the plan: "update the plan README's Progress section (Current Status, a dated Recent Updates entry...)". Hmm.

Actually, in the very first plan (v1) I wrote "README Progress update". In the phase table I wrote "Progress update". The user's point #2 is probably about the phrasing of the phase-end tasks in the feature README: use "Recent Updates" (the actual section name) rather than the generic "Updates". This is a trivial wording fix — acknowledged.

Now, the main design question #1: line-range `begin`/`end` partial updates.

Let me think carefully. Does this make sense?

**Semantics**: `update(id, type, content, begin=None, end=None)` where begin/end are line numbers of the body (or of the whole file?) that `content` replaces.

Key design questions:

- Line numbering: 1-based? Inclusive on both ends? Of the body (excluding frontmatter) or of the whole file (including frontmatter)?
- What does "replace lines begin..end with content" mean validation-wise? The **whole** resulting body must still parse and validate (that's the core invariant — the on-disk file is always source of truth and is validated). So a partial update = read current body, splice in content at [begin, end], validate the **whole** result, and if valid write.
- This changes the validation contract: today, `update` validates the `content` alone (body-only markdown via `X.from_text`). With line ranges, `content` is no longer a standalone body — it's a fragment. So validation of `content` alone no longer applies; validation is against the spliced whole body.
- Edge cases: begin > end? begin=1 (replace from top)? end beyond EOF? begin/end within frontmatter (must be forbidden — frontmatter is immutable through update; only body lines addressable)? content containing a trailing newline? Empty range (begin=end → insert before that line? or replace that line?).

**Does this make sense?** Let me think about the benefits vs the cost/risks in this codebase's design philosophy:

Pros:

- Smaller/faster tool calls: LLM sends only the changed lines instead of the full body. For large documents (UCs, QAs with many sections), this is a real token savings.
- Reduces the "carry-forward" failure mode: today, the narration says "read the current body first and carry forward every section you are not intentionally changing, or it will be dropped". A whole-body replace is dangerous for large documents — the LLM can silently drop a section when re-emitting the body. A line-range update eliminates that class of errors for targeted edits.
- Fits the "filesystem is the sole source of truth" design: the spliced result is still a fully validated document before writing.

Cons/Risks:

- Line numbers are brittle: if the file changed since the LLM last read it (another process, or the LLM read it N turns ago), the range can splice in the wrong place. Mitigation: the flow already says "read current state first (get_X)". The spliced result is validated as a whole — structural validation catches gross mismatches (missing/duplicated headings) but not subtle semantic shifts (e.g., replacing lines within a bullet list and shifting the wrong item).
- Complexity: a new code path in each of the 7 adapters (or in a shared splice helper), new error cases, new tests. The adapters were "verbatim ports" — now they need the splice logic. But the splice logic can be **shared** (a pure function in `general/tools/` or `models/md/`): given the current body text + begin + end + content, produce the new body text. That's clean: `spliced = _splice(body_text, begin, end, content)` then `X.from_text(format_text(spliced))`. Wait — but today the write persists the **caller's** raw content verbatim (byte-for-byte, only trailing-whitespace stripping by python-frontmatter). With a splice, the written body is the spliced full body — the unchanged parts are the current on-disk bytes (read back as-is), the changed part is the caller's content. This is actually **better** fidelity than today (today, even the unchanged sections are re-emitted by the LLM and can drift; with a splice, the unchanged sections are byte-identical to disk).

Hmm wait, there's a subtlety: today `update_X` writes `content` verbatim (the LLM's full body). With a splice, we write read-back body + splice. The read-back body: does `load_by_id` parse the file into a model; do we have the **raw** body text? For set_status, it re-reads the raw body via `frontmatter.loads(path.read_text()).content`. For the spliced update, we'd similarly grab the raw body text (frontmatter-stripped), split into lines, replace lines [begin:end] with content's lines, join. The raw body preserves everything byte-for-byte (except for python-frontmatter's own parsing). Then validate the spliced whole via `X.from_text(format_text(spliced))` and write the spliced text verbatim via `write_X_file`.

So the implementation is actually pretty contained:

- A shared pure helper `_splice_body(current_body: str, begin: int, end: int, content: str) -> str` in general/tools (or models/md? — it's markdown-agnostic line splicing; a `general/tools/_splice.py` private module, or just a function in update.py).
- The 7 adapters get: when begin/end given → read raw body, splice, validate whole, write; when not given → current behavior (validate content as body, write).
- Parameter semantics: 1-based, inclusive on both ends, body lines only (line 1 = first body line after the frontmatter block). begin=1..end=N covers the whole body → equivalent to whole-body replace but with different validation path? For consistency: if begin/end given, splice semantics always apply. If not given, whole-body semantics (content is the full body).

Actually — a simpler, more uniform proposal: `content` + optional `begin`/`end`. No begin/end → content is the whole body (today's behavior). With begin/end → content is the replacement for body lines begin..end (inclusive). Uniform rule: the result is validated as a whole body in either case.

What about ADR? ADR is out of scope for `update` (section-level tools exist). So no impact.

What about `set_status`? No body change, no line params. No impact.

**Do the begin/end line params belong on the generic `update` tool, or are they a separate concern?** I think it's fine on `update` — it's part of "how the body content is applied". It's a single tool with optional parameters; the MCP schema is: id (str, required), type (enum, required), content (str, required), begin (int, optional), end (int, optional). Clean.

**Validation details** (worth putting in the plan):

- begin/end must be positive integers; if either is given, both must be given (a half-specification is an error — or allow begin-only? No: require both-or-neither; simpler contract);
- begin ≤ end;
- 1 ≤ begin ≤ end ≤ len(current_body_lines) (end beyond EOF → error; begin=1 allowed);
- content is raw markdown fragment; after splicing, the whole body is validated through the domain's `from_text(format_text(...))` — structural errors and field errors surface as today (AssertionError / pydantic.ValidationError), nothing is written;
- the frontmatter is not addressable (body lines only) — by construction, since we splice the frontmatter-stripped body.
- If begin/end given and the range covers the whole body, result == whole-body replace (consistency check, good test case).
- Empty `content` with begin/end = deletion of that line range (a valid operation if the result still parses — e.g., deleting an optional section). This is a nice emergent capability; should we explicitly allow it? Today's whole-body update with empty content fails (a body must at least have an H1 etc.). With a splice, empty content deletes lines — allow and let the whole-body validation decide.

**Risk assessment**: the main risk is LLMs mis-counting lines. Mitigations:

- The narration (prompt) tells the LLM: read via `get_X`, identify the 1-based line numbers of the region to change (the get_X response returns the document — does it include line numbers? The tool returns the parsed document model, not raw text… hmm!).

Wait, this is important. How does the LLM know the line numbers? `get_X(id)` returns a `XDocument` (frontmatter + parsed body model) — serialized to JSON, **not** the raw markdown with line numbers. So the LLM cannot reliably count lines from `get_X`'s output! The LLM needs the raw body text.

Options:
(a) The `update` tool's splicing accepts line numbers, and the **narration** tells the LLM to obtain the raw markdown… from where? There is no tool that returns raw body markdown (get returns the model; the resources `specmgr://X/{id}` were removed). Hmm.
(b) Use **heading anchors** instead of line numbers? More robust for LLMs (they think in sections), but the user explicitly asked for line parameters begin/end.
(c) Add a `raw`/text-returning read path: e.g., `get_X(id, raw=True)`? That would change the read tool's surface — scope creep.
(d) The LLM counts lines from… the create-time content it wrote itself, or from a prior get_X? The get_X output is structured JSON; reconstructing line numbers from it is error-prone.

Hmm wait — actually, how does the MCP SDK serialize a pydantic model return? It json-dumps it. The body model is a section tree — no line info.

So there's a real usability question: **where do the LLM's line numbers come from?** If we can't get the raw body cheaply, line-range updates are hard for the client to use correctly.

Possible resolutions:

1. Extend `get_X` (and/or the new `update`'s error messages) — out of scope for update.
2. Have the **update tool itself** report useful context on error: if the splice result fails validation, the error message can include the spliced body (or a diff) so the LLM can self-correct.
3. Add a lightweight raw read: a `raw` parameter on `get_X`? The user asked only about update. But without a raw read, the feature is half-useful. Hmm.

Wait — actually, let me reconsider. Does `get_X`'s JSON really lack line numbers? Let me check what the document model looks like… `ReqDocument(frontmatter, body)`; body = `Requirement(MarkdownSection1)` with sections. No line metadata (the parser engine `models/md` — does it retain source spans? I don't think so; let me quickly verify). If the parser retains line spans, get_X's serialization **would** contain them (or could). Let me check the `MarkdownSection1`/alias_match parsing for line tracking.

Actually, my earlier exploration of models/md: `alias_match.py`, `alias.py`, `markdown_section1.py` etc. I haven't seen line spans. Let me grep for "line" in models/md to check.

Also alternative (b) revisited: instead of line numbers, address by **heading**: `begin` = heading text (e.g., "Description"), `end` = next heading? That's a different mechanism (section-range replace) — closer to ADR's update_section but for the 7 domains. The user explicitly said "line parameters, begin, end" — they want lines. I should respect that but flag the raw-text problem and propose a solution:

- The `update` tool's splicing works on body lines;
- For the client to obtain line numbers, the **narration** directs it to read the raw body. The cheapest way to make that possible without expanding the surface: have `get_X` also return the raw body text? No — that changes 8 tools…

Hmm, or: accept that the LLM typically knows the content it last wrote (from the create_X call it made), and/or that the update tool can return rich validation errors. Or — the simplest, most robust option: the spliced body is validated, and if validation fails, the error propagates as today; the LLM can fall back to a whole-body update. Line-range is an **optimization**, whole-body is the reliable fallback. That's a defensible design: "optional, best-effort precision; validation is the safety net".

But the raw-text issue remains: for the LLM to target a specific line, it needs to see the file with line numbers. Without it, it will guess — bad.

Let me check if the get_X output actually contains the body in a text form. Let me look at ReqDocument/Requirement's model serialization… Actually, the parser builds models from text; the models don't retain the original text. But wait — `frontmatter` + a body model whose `__str__` is a re-rendered markdown (feat-18 ACC-001 used `str(doc.body)` to get the body text byte-for-byte!). "asserts str(doc.body) equals the file's body" — so the model **does** have a rendering `__str__` that reconstructs the markdown. So the LLM can reconstruct the body text from get_X's JSON? Only if the JSON contains all the text content — it does (all section texts). But reconstruction of exact line numbers from the JSON is the LLM's job (it re-derives the markdown structure). Fragile but possible… Actually no — the JSON is a nested section tree; the LLM would have to re-render it and count lines. Error-prone.

OK, my honest assessment to give the user:

**Does it make sense? Yes, with two important design conditions:**

1. **The whole-body validation invariant stays absolute**: a line-range update splices content into the current on-disk body and validates the **resulting** whole body before writing. A range update can never write an invalid document, and the frontmatter is never addressable (body lines only). When begin/end are omitted, today's whole-body behavior is unchanged (backward-compatible default).
2. **The client needs a way to see line numbers**. `get_X` returns a structured model, not numbered raw text. I recommend pairing this feature with a small read-side addition: a `raw: bool = False` parameter on… hmm, that's 8 tools. Or a separate generic `read_raw`? That expands the surface — the opposite of the consolidation goal.

Wait wait. Let me reconsider. Is there **already** a way for the LLM to get raw markdown? The MCP resources… `specmgr://X/{id}` were removed. The `parse_X(path)` tool reads from a **file path** — it takes a path and returns the parsed model. Also not raw text.

Hmm, what does `get_X`'s JSON look like — actually, let me verify that the body serialization includes the raw text somewhere. Let me look at the Requirement model and the MarkdownSection1 `__str__`. If `str(body)` reconstructs markdown byte-for-byte (per feat-18's evidence), the **tool result** (JSON) contains the structured data from which the LLM can derive the text. But counting lines from the JSON tree is really error-prone.

Options for solving the line-number problem:
A. Add optional `begin`/`end` **plus** require the flow: "call get_X first" (already the flow); the LLM re-renders and counts. Risky.
B. Add a `raw` flag to `get_X` (8 tools: 7 domains + get_adr? ADR also has get_adr — 8 total). A small additive parameter; when raw=True, return the file's full text (frontmatter + body) — or body only? Full file text is most useful (the LLM sees the frontmatter lines too, but the ranges are body-relative anyway). Additive, backward-compatible. But it expands the surface of 8 tools' docstrings/tests…
C. A single generic `read_raw(id, type)` tool — adds a **new** tool (opposite of consolidation), but 1 tool vs 8 parameter changes. Hmm.
D. Return the current body with line numbers as part of `update`'s **error** message when a range is given but the result is invalid… doesn't help with initial targeting.
E. Accept the LLM counting lines from the get_X JSON (structured). The LLM is decent at this if the JSON is faithful. Risky but zero surface change.

Actually — hmm, wait. Let me reconsider the problem. The LLM's **main** use of begin/end: it has the current body in context (from a prior get_X or from its own prior create/update). It wants to replace, say, lines 12-18 (a paragraph in the Description section). If get_X returns structured JSON, the LLM sees all the text content but not the exact line breaks…

Actually, let me **verify** what get_X returns — does the JSON include the raw text? Let me read the Requirement body model to check serialization. `MarkdownParagraph` probably has a `text` field. A section has `title` and child elements. If the JSON includes every text chunk, the LLM **can** reconstruct the markdown (it knows the heading structure) and count lines approximately — but blank lines/comments could throw it off.

Let me look at the actual model to ground this. Quick reads: req/models/v1/body.py (top), models/md/markdown_section1.py, markdown_paragraph.py — checking whether `__str__` rendering and the fields are text-faithful.

Actually, stepping back, let me think about what a **good** plan is. The user asked "Does this make sense?" — I should give an honest technical assessment:

**Assessment: yes, it makes sense, and it's actually a safety win, provided:**

1. Splice-then-validate-the-whole is the contract (no partial writes ever).
2. Line coordinates are 1-based inclusive on **body** lines (frontmatter excluded, never addressable).
3. Both-or-neither, begin ≤ end, end ≤ body length.
4. Unchanged regions stay byte-identical to disk (better fidelity than today's re-emission).
5. The client can obtain reliable line numbers — this is the one gap.

For #5, my recommendation: **add an optional `raw: bool = False` to the 7 `get_<d>` tools** (get_adr too? ADR isn't affected by update's ranges… but for consistency — ADR's updates are section-level, no line ranges, so get_adr doesn't need it. Keep it to 7). When raw=True, return the file's raw text as a string. Additive, backward-compatible, small. Hmm, but that's 8… 7 tools × (docstring + tests). Modest.

Alternative for #5, cheaper: no get_X change; instead have the **update tool itself** accept begin/end and, on successful range update, return the updated document (as today) — and rely on the LLM having read the body via get_X's structured output. I'm going back and forth. Let me verify what get_X actually returns to decide. If the JSON faithfully contains all text (including which lines are blank?), counting is possible.

Let me quickly check the model. Read req/models/v1/body.py partially + models/md/markdown_section1.py + markdown.py's __str__.

Actually, the evidence from feat-18's ACC-001: "asserts str(doc.body) equals the file's body (frontmatter stripped, format_text normalized) byte-for-byte — 2030 == 2030 bytes". So the model is lossless (round-trips byte-for-byte). The JSON serialization of the model contains everything. An LLM receiving the JSON **can** in principle reconstruct the body, but it has to map the JSON tree → markdown lines. Doable but a cognitive burden; blank lines are… in the model? If str() reproduces blank lines, then blank lines exist in the model (or are re-derived). The LLM counting lines from the JSON: it would have to simulate the renderer. Error-prone → mis-targeting → the splice lands on the wrong lines → validation either catches it (structural) or **doesn't** (semantic: e.g., replacing the wrong paragraph of similar shape).

So my honest recommendation: **pair line ranges with a raw read**. The cleanest additive option that doesn't expand the tool count: an optional `raw: bool = False` parameter on the 7 `get_<d>` tools returning the full file text (frontmatter + body). This is small, additive, backward-compatible, and directly enables reliable line targeting. And document in the narration: "for range updates, first call get_X(id, raw=True), find the 1-based body line numbers (the body starts after the frontmatter's closing `---` line), and pass begin/end."

Hmm, but wait — is that in scope for "Consolidate all update commands"? It's an enabling read-side addition. The user proposed begin/end on update; the raw parameter is a natural companion. I should **present** this as a recommendation and let the user decide (it's a real trade-off: +7 parameter surfaces vs the usability of the feature). Options:

- A: update begin/end + `get_X(raw=True)` companion (recommended)
- B: update begin/end only; the LLM targets lines from structured get_X output (no surface addition; higher mis-targeting risk)
- C: drop begin/end (keep the plan as-is)

Also, should begin/end apply to the `set_status`-style… no. Only to update.

Another design point: **what exactly is the line origin?** Body line 1 = the first line after the YAML frontmatter block (i.e., after the closing `---`). The file also has frontmatter lines. If we return raw file text, the LLM must offset. Simpler alternative: the get_X raw return = body only (frontmatter stripped)?? Then line 1 = first body line — cleaner mapping, but the LLM can't see the frontmatter (it gets that from get_X's structured output anyway — the frontmatter is fully in the JSON). Hmm, actually **that's** cleaner: `get_X(id, raw=True)` returns the raw **body** markdown text (frontmatter stripped) — exactly the text that begin/end index into. Zero offset confusion. But it deviates from "raw file". I like body-only raw: the contract becomes "begin/end are 1-based inclusive line numbers within the text that get_X(id, raw=True) returns". Clean, testable, no off-by-one across the frontmatter.

Wait, but do we want a new parameter on get_X, or does get_X **always** return raw body as an extra field? get_X returns a XDocument model — adding a field would change the schema for all callers. Optional parameter is cleaner: `raw=False` → today's behavior (document model); `raw=True` → a plain string (body text). Return type is `XDocument | str`. Hmm, a union return on an existing tool — the MCP SDK handles str fine.

Alternatively — a **completely** different idea: instead of a parameter on get_X, the begin/end splice doesn't require the LLM to count at all: accept **section-relative** addressing? No, the user said lines. Keep lines.

OK, one more thought — should the **update tool** also accept a `raw`-ish thing… no, update takes content. The read side needs raw.

Let me also think about the splice mechanics precisely for the plan:

```
current_body = frontmatter-stripped raw text of the on-disk file (via frontmatter.loads(path.read_text()).content — the same mechanism set_status_X uses)
lines = current_body.splitlines(keepends=True)? or split("\n")?
```

Line semantics: 1-based inclusive on both ends. `new_lines = lines[:begin-1] + content.split("\n") + lines[end:]`. Trailing newline handling: the file ends with "\\n"; content may or may not. Rule: join with "\\n" and ensure a single trailing "\\n". Define in the plan: split the current body into lines (stripping the file's trailing newline), replace indices [begin-1:end] with content's lines (content split on "\\n", with a trailing empty element dropped if content ends with "\\n"), rejoin with "\\n" + trailing "\\n". Then `X.from_text(format_text(new_body))` for validation; write `write_X_file(path, fm, new_body)` — **wait**, today write persists the caller's raw `content` verbatim. With a splice, we persist the **spliced** body (which includes format_text? no —). Hmm: today update writes `content` verbatim (the LLM's exact text), and validation uses `format_text(content)`. With a splice, the written body should be the spliced text verbatim (unchanged regions byte-identical to disk, new region = caller's content verbatim). Validate via format_text(spliced). So the write text = the raw splice result. Good — simpler: write the spliced text, not format_text'd.

Edge: whole-body mode (no begin/end): **no** behavior change (write content verbatim, validate format_text(content)).

And the `updated` bump + frontmatter carry-over: same as today.

Tests to add (Phase 2, expanded):

- Range covering the middle of a body (replace a paragraph) → whole document valid, unchanged regions byte-identical, written file = disk lines + new content.
- begin=1/end=last line → equivalent to whole-body replace (consistency).
- Empty content → line deletion (result valid → OK; result invalid → error, nothing written).
- Range spanning an entire optional section (including heading + body + trailing blank line) → section removed, doc valid.
- Invalid: begin>end; one of begin/end given; begin\<1; end>len; non-int (schema); range that breaks structure (e.g., deletes the H1) → AssertionError, file unchanged; range that produces an invalid field value → ValidationError, file unchanged.
- raw get_X: raw=True returns the body text byte-for-byte (frontmatter stripped, same normalization as the str round-trip); raw=False returns the model (regression).
- The get_X docstring/schema: new optional parameter, default behavior unchanged.

Which phase gets this? Phase 2 (the generic update) — the splice belongs in the adapter (shared helper `_splice_body` in general/tools or a shared private module; a `general/tools/_splice.py`? or inside update.py — keep it inside update.py as a private function + a shared pure module if set_status needs it (it doesn't). Keep it in update.py.) And the get_X raw parameter: 7 domain tools — that's **not** in general, it's in the domain (get_req.py etc.). So Phase 2 also touches the 7 get\_<d> tools (additive parameter) + their tests. Phase 2 grows: new update tool + splice + raw parameter on 7 gets. Still one coherent phase ("generic update + its enabling read path"). Alternatively split raw-get into its own phase (Phase 2: generic update with splice; Phase 3: raw parameter on get_X; …). I think **one** phase is fine — the work is mechanical (the same small edit ×7).

Hmm, wait — actually, let me reconsider whether get_X's raw is really needed or if I'm over-engineering. The user's motivation: "This can make tool calls faster and smaller". The LLM benefits only if it can identify the lines reliably. Without raw text, the LLM has to count lines from the JSON — I assessed that as fragile. With raw body text — trivial. So yes, the companion is the difference between a useful feature and a risky one. Recommend it; present alternatives (B: without it).

Also **note**: the raw parameter — `get_adr` too? ADR's `update` doesn't take ranges; ADR has update_section which addresses by **section key**, not lines. So no. But for **consistency**… the ADR surface is intentionally different; skip.

What about the **narration** (Phase 5): the update instruction files must teach the range update: "For a small, localized change, prefer get_X(id, raw=True), identify the 1-based body line range, and call update(id, type, content, begin, end) with **only** the replacement lines; for large or multi-section changes, use whole-body update (no begin/end); when in doubt, whole-body is safe". Also qa_refine (which does an append — an append can be a range update with begin=end=last line+1? Hmm — insertion: does the contract support begin=end=N+1? I defined end ≤ len(lines). For appending at the end: begin=end=len(lines)+1 would mean "insert after the last line"… simpler: an append = begin=end=last line with content = "last line's text + new lines" — ugly. Alternative: allow end == len+1 as an insert-at-EOF? Let me define: allow begin in [1, len+1] and end in [begin, len] when… hmm, getting complex.

Simpler, more robust contract: **begin** and **end** are 1-based **inclusive** line numbers of the current body; if begin > end… no.

Let me define an **insertion** case explicitly: `begin == end == N+1` (where N = body line count) is not possible under begin ≤ len. Options:

- Allow `begin = end = N+1` as "insert at end" (a special case), and in general `begin = end = k` with k ≤ N means "replace line k", while `begin = k, end = k-1`… no, negative ranges are confusing.
- Or: define the range as \[begin, end) half-open? The user said begin/end — inclusive feels natural.
- Or: allow end to be N+1, meaning "to the end of the body" (common in editors: line 5 to end). And allow begin to be N+1 for appending (begin=end=N+1 → insert at EOF). So the rule: 1 ≤ begin ≤ N+1, begin ≤ end ≤ N+1, where N+1 means "past the last line" (EOF). Range [b, e] is inclusive on the current lines: replace lines b..e; if e = N+1, the range extends to EOF (i.e., b..N); if b = N+1, the range is empty at EOF → pure append. This covers: middle replace, trailing replace (b..N via end=N+1? hmm — b..N is expressible as end=N; end=N+1 = "to EOF" = same as N unless there's an insertion). Slight redundancy but harmless and very editor-like.

Wait, simpler: keep it **strict**: 1 ≤ begin ≤ end ≤ N (N = current body line count). Appending = begin=end=N with content = (current line N text + "\\n" + new lines) — no, that requires the LLM to echo line N. Ugh.

The N+1 EOF sentinel is cleaner for LLM use (append is a first-class need — qa_refine **appends** question pairs; a tsk task list appends tasks). Adopt: `1 ≤ begin ≤ N+1`, `begin ≤ end ≤ N+1`, and `end = N+1` or `begin = N+1` denotes the position past the last line (insertion point at EOF). Replace semantics: lines [begin..end] are deleted (skipping the virtual N+1) and content is inserted at begin. So:

- begin=3, end=5, N=20 → replace lines 3-5.
- begin=21, end=21 (N=20) → append at EOF.
- begin=17, end=21 → replace lines 17-20 (to EOF).
- begin=17, end=17 → replace line 17.
  This is a clean, total contract. Validation: both or neither; integer ≥1; begin ≤ end; end ≤ N+1.

And the whole-body default (no begin/end): content **is** the whole body (today's behavior) — **not** interpreted as begin=end=1..N. Important: don't conflate.

Also: does the splice use the **on-disk** raw body (frontmatter.loads's content) — yes, same as set_status. Note: python-frontmatter's `content` — does it preserve the body exactly? set_status_X already relies on this (raw_body is re-persisted verbatim), so precedent exists. The trailing newline: the file ends with "\\n"; `frontmatter.loads(...).content` probably keeps the body including the trailing "\\n"? The splice implementation handles it: N = the line count of the body text with the trailing newline stripped.

OK. Now the **other** part of the user's message #2: "Use 'Recent Updates' instead of 'Updates'". This is about the README's wording — the phase-end task says "a dated Updates entry" — I'll use the exact section name "Recent Updates". Trivial; acknowledged. (Probably I wrote "Updates" in the plan's phase description. Fixed in the README draft: "add a dated entry to the Recent Updates section".)

Now, should I ask the user about the get_X raw companion (option A vs B)? Yes — it's a real surface decision. Options:

- A: `get_<d>(id, raw=False)` on the 7 domain get tools — raw=True returns the body text (frontmatter stripped), which begin/end index into. (Recommended)
- B: no read-side change; the LLM derives line numbers from the structured get_X output (higher mis-targeting risk).
- C: skip begin/end entirely (keep the original plan).

Also, maybe I should verify my claim that get_X's output doesn't contain the raw text — let me quickly check the body model's serialization to be sure before I assert it. Let me read a bit of req/models/v1/body.py and a MarkdownSection1 to confirm the fields (text-based, no raw). Actually, the JSON **does** contain all the text content (section texts) — my point is that it doesn't contain line numbers or the exact line layout (blank-line placement is only implicit). I'm confident enough from feat-18's evidence (byte-for-byte round-trip is via __str__ rendering, not a stored raw field — wait, is it stored? If the model stored the raw text, __str__ could just return it. Hmm. Let me check quickly: does MarkdownSection1 or the body model have a field holding the original text? Let me grep for "raw" or "__str__" in models/md.)

Let me do one quick verification read to ground the claim, then write the answer + one question.

Two things to process: the line-range design (let me verify one assumption first), and the "Recent Updates" wording fix (noted — the phase-end tasks will name that exact section).

Quick check on what `get_X` actually returns — whether the structured output carries line information at all, which determines how a client would target lines:

**Tool: bash**

**Input:**

```json
{
  "command": "grep -n \"__str__\\|raw\\|lines\\|lineno\\|line_no\" src/biz/dfch/specmgr/models/md/markdown.py src/biz/dfch/specmgr/models/md/markdown_section1.py src/biz/dfch/specmgr/models/md/markdown_paragraph.py 2>/dev/null | head -20; echo ===; sed -n '1,60p' src/biz/dfch/specmgr/models/md/markdown.py | grep -n \"class\\|def\" "
}
```

**Output:**

```
src/biz/dfch/specmgr/models/md/markdown_paragraph.py:43:    `get_extent`/`from_text`/`__str__` docstrings below for the full
src/biz/dfch/specmgr/models/md/markdown_paragraph.py:136:        sentence) so that `__str__` can re-emit it without duplicating what
src/biz/dfch/specmgr/models/md/markdown_paragraph.py:170:        own_lines = own_map[1]
src/biz/dfch/specmgr/models/md/markdown_paragraph.py:172:        body_lines = text.splitlines()[own_lines:]
src/biz/dfch/specmgr/models/md/markdown_paragraph.py:173:        body_text = format_text("\n".join(body_lines)) if body_lines else ""
src/biz/dfch/specmgr/models/md/markdown_paragraph.py:179:    def __str__(self) -> str:
src/biz/dfch/specmgr/models/md/markdown_paragraph.py:184:        defers to `super().__str__()` (`MarkdownStr.__str__`'s leaf branch,
src/biz/dfch/specmgr/models/md/markdown_paragraph.py:188:        Composite case: `MarkdownStr.__str__` would only concatenate the
src/biz/dfch/specmgr/models/md/markdown_paragraph.py:192:        `from_text`). Prepends `_value` to `super().__str__()`'s children
src/biz/dfch/specmgr/models/md/markdown_paragraph.py:193:        output -- unlike `MarkdownSection.__str__`, there is no heading
src/biz/dfch/specmgr/models/md/markdown_paragraph.py:197:            return super().__str__()
src/biz/dfch/specmgr/models/md/markdown_paragraph.py:199:        body = super().__str__()
===
27:#: default cannot make this distinction, since `None` is also a legitimate,
35:def markdown(
41:    """Decorator to add markdown-it metadata to MarkdownStr subclasses.
43:    Attaches metadata (type, tag, and end_marker) to a MarkdownStr subclass
44:    via the `_metadata` class attribute. This decorator focuses on
53:    keyword-only and default to a private sentinel (`_UNSET`), not `None`,

```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 354.3s)

_Thinking:_

Confirmed: the model reconstructs markdown via the `__str__` rendering logic (line mapping, `_value` + children), and does not retain the raw source text with line numbers. Therefore `get_X`'s JSON output is a structured tree, and line numbers cannot be obtained directly. My claim holds: for the LLM to reliably target lines, we need a read path that returns raw text.

Now to draft the reply:

**1. Does begin/end make sense?** — Yes, with a precise contract. And the one gap: clients need line numbers, but `get_X` returns a structured model (I verified: the body is re-rendered by `__str__`, and no raw text or line metadata is stored). Therefore, recommend a read side that pairs an optional `raw: bool = False` on the 7 `get_<d>` tools: `raw=True` returns the frontmatter-stripped body text verbatim — which is exactly the text that `begin`/`end` indexes into.

The contract to specify in the plan:

- `update(id, type, content, begin=None, end=None)`
- When begin/end are omitted: behavior unchanged today (content = the whole body, validated as the whole body, written verbatim).
- When both are specified: content is a replacement fragment for the current body lines. Coordinates: 1-based, inclusive on both ends, indexed into the body (frontmatter is excluded, and by construction is never addressable). `N` = number of lines in the current body. Valid range: `1 ≤ begin ≤ end ≤ N+1`, where `N+1` is the virtual position just past the last line (i.e. begin=end=N+1 = append at end of file; end=N+1 = extend to end of file). If only one of begin/end is specified → error.
- Mechanics (shared, inside the adapter): read the raw body from disk (same `frontmatter.loads(...).content` mechanism that `set_status_X` already uses), splice the lines, then validate the resulting whole body via `X.from_text(format_text(spliced))` — the whole-document invariant is absolute; nothing is written unless the splice result passes validation. Unchanged regions remain byte-identical to disk (better fidelity than today's re-emission by the LLM).
- The spliced text is persisted verbatim (in the unchanged regions, not re-rendered).
- An empty content fragment = deletion of the line range (legal if the result passes validation) — a capability that is useful for removing optional sections.

Benefits: smaller/faster calls + eliminates the "carry over all the other sections" drop hazard in targeted edits; the whole-document validation remains the safety net; the whole-body default keeps backward compatibility and a fallback.

Risks (honestly):

- Line numbers go stale if the file is modified after the read → the splice lands in the wrong place; structural validation catches most of it, but semantically similar regions can pass through. Mitigation: keep the "read the current state first" flow in the narration; whole-body remains the fallback.
- The feature is only as good as the client's ability to count lines → hence the paired `raw` read (option A). Without it (option B), the LLM has to reconstruct line layout from the structured JSON — fragile.

**2. "Recent Updates"** — noted: the phase-end task in the README says "add a dated entry to the Recent Updates section."

Next, ask one question: option A (paired raw parameter on the 7 get tools) vs B (no read-side change) vs C (drop begin/end). Recommend A.

Should I also confirm the N+1 append semantics? That's a design detail I can decide myself and record in the plan; if the user picks A/B they'll see the contract in the updated plan. Actually, I'll briefly state the contract in the reply and let the question focus on the read side. Keep the reply concise.

Phase-structure impact if A is chosen:

- Phase 2 (generic update + splice + tests) also adds `raw: bool = False` to the 7 `get_<d>` tools + their tests + docstrings (server.py docstring mentions get? The server docstring lists tool names, not parameters — no change beyond what Phase 2 already does… the docstring of `get_X` in each domain's tools changes → `specmgr docs` (docs/api) regeneration — already in the gate).
- Phase 5 narration: the update instructions teach the range-update flow (raw=True read → identify lines → update with begin/end; whole body if it spans many sections / when in doubt).
- ACC: extend ACC-001 with the range-update behavior + raw read behavior.

The tool count is unchanged (no new tools: 71/25/19 still holds — the raw parameter does not add tools).

Now to write the reply: concise assessment + contract + one question.

Confirmed the key assumption: `get_X` returns a structured model — the body markdown is *re-rendered* via `__str__` (verified in `models/md/markdown_paragraph.py:179`); no raw source text or line metadata is stored. That matters for your idea.

**1. Line ranges: yes, this makes sense — it's actually a safety win, not just a size optimization.**

- **Today's failure mode:** whole-body replace requires the LLM to re-emit *every* unchanged section; the narration even warns "carry forward every section … or it will be dropped." A range update eliminates that hazard for targeted edits, and unchanged regions stay **byte-identical to disk** (better fidelity than today).
- **The invariant stays absolute:** with `begin`/`end`, the tool splices the fragment into the *current on-disk body*, then validates the **resulting whole body** before writing. A partial update can never write an invalid document; the frontmatter is never addressable (body lines only).
- **Contract I'd spec:** `update(id, type, content, begin=None, end=None)`. Omitted → exactly today's whole-body behavior (backward-compatible default + fallback). Both given → 1-based, inclusive, body-relative coordinates with an `N+1` EOF sentinel so append is first-class (`begin=end=N+1` = append; `end=N+1` = through end of body; one of the two given = error; empty `content` = delete the range, legal if the result still validates).

**The one gap:** the client needs reliable line numbers, and `get_X`'s structured JSON doesn't provide them — an LLM reconstructing line layout from a section tree is a mis-targeting risk (and a mis-targeted splice into a structurally similar region can pass validation). So I recommend pairing it with a small, additive read-side change:

- **`get_<d>(id, raw=False)`** on the 7 domain get-tools: `raw=True` returns the frontmatter-stripped body text verbatim — *exactly* the text `begin`/`end` index into. Zero offset confusion, zero new tools (count stays 71/25/19), default behavior unchanged.

**2.** Noted — the README's phase-end tasks will say "add a dated entry to the **Recent Updates** section" (the exact section name from the template), not "Updates".

Impact on the phase plan if you agree: Phase 2 grows to "generic `update` + splice + `raw` on the 7 `get_<d>` tools + tests for both"; Phase 5's narration teaches the range-update flow ("for a localized change: `get_X(id, raw=True)` → find the line range → `update(…, begin, end)`; for multi-section or uncertain changes: whole-body"). Everything else (Phases 1, 3–7) is unchanged.

**Tool: question**

**Input:**

```json
{
  "questions": [
    {
      "header": "Line ranges",
      "options": [
        {
          "description": "update(id, type, content, begin, end) with the N+1 EOF sentinel contract, plus get_<d>(id, raw=False) on the 7 domain get-tools so clients can see the exact body text the coordinates index into.",
          "label": "begin/end + raw read (Recommended)"
        },
        {
          "description": "begin/end on update only; the LLM derives line numbers from get_X's structured output. No read-side change, but higher mis-targeting risk.",
          "label": "begin/end only"
        },
        {
          "description": "Keep the plan as previously approved; whole-body replace stays the only update mode.",
          "label": "Drop begin/end"
        }
      ],
      "question": "Which shape do you want for the partial-update feature?"
    }
  ]
}
```

**Output:**

```
User has answered your questions: "Which shape do you want for the partial-update feature?"="Option A sounds good. But just a quick thought: would it be better to re-introduce resource/{id} to get raw markdown instead of adjusting get_X with optional begin/end parameters?". You can now continue with the user's answers in mind.
```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 78.2s)

_Thinking:_

The user selected Option A, but is asking a design question: instead of adding a `raw` parameter to `get_X`, should we re-introduce the `specmgr://X/{id}` resource in order to fetch raw markdown?

Let me think about this carefully. Background: ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614 ("Expose id-based REQ document reads as a tool (get_req), not as a resource") deliberately removed `specmgr://req/{id}`. The ADRs for UC, QA, PRB, GOL, RSK also state "no specmgr://X/{id} — id-based reads are get_X-only (ADR ddfb1109-...)".

Why was it a tool rather than a resource? Let me recall/verify the ADR's rationale. I'll read the ADR to ground my answer.

Key technical facts about MCP resources:

- Resources are URI-addressable content that the host can list (`list_resources`) and read (`read_resource`). Clients subscribe/list resources. Resources are generally for static or enumerable content, whereas tools are for actions with parameters.
- `specmgr://X/{id}` would be a *resource template* (parameterized URI). In MCP, resource templates are listed via `list_resource_templates`, and the client reads them with a concrete URI.
- Practical considerations in this codebase:
  1. How does the MCP client (OpenCode/LLM) actually consume resources vs tools? In OpenCode, MCP resources can be referenced/fetched. Tool calls are the primary means by which an LLM reads content during a conversation.
  2. The former `specmgr://req/{id}` resource returned… what? A parsed document, or raw markdown? Let me check git history / the ADR. ADR ddfb1109 will state the rationale. Let me read it.
  3. If re-introduced, what does it return? If raw markdown, that answers the line-numbering problem. But in that case, `get_X` (structured) + `specmgr://X/{id}` (raw) = two read paths per domain → the surface grows by 7 resources + registration + pyproject packaging? No, no packaging needed — it's a dynamic resource that reads from disk. The ADR removed it, in part… let me read why.

I'll read ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614.

Also to consider: the mcp SDK's resource templates — the server currently has "1 resource template" (per the header in docs/MCP.md). Adding 7 `{id}` templates would increase the count. And ADR ddfb1109 is an accepted ADR — re-introducing `/{id}` resources would *contradict/supersede* an accepted ADR, which per AGENTS.md/ADR rules requires writing a new ADR that supersedes it (status "superseded by"). That's a heavyweight move: it reverses a deliberate cross-domain decision (applied to REQ, UC, QA, PRB, GOL, RSK).

Let me read the ADR to recall the actual rationale.

Good question — that decision was made deliberately (ADR ddfb1109). Let me re-read it before answering, since re-introducing `/{id}` resources would mean reversing an accepted, cross-domain ADR.

**Tool: read**

**Input:**

```json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/docs/adr/ddfb1109-422d-4507-8dbc-dc5e4bec9614-expose-id-based-req-document-reads-as-a-tool-get-req-not-a-r.md"
}
```

**Output:**

```
<path>/home/user/src/biz.dfch.SpecMgr/docs/adr/ddfb1109-422d-4507-8dbc-dc5e4bec9614-expose-id-based-req-document-reads-as-a-tool-get-req-not-a-r.md</path>
<type>file</type>
<content>
1: ---
2: status: accepted
3: date: '2026-08-15'
4: decision-makers: OpenCode agent + user decision
5: id: ddfb1109-422d-4507-8dbc-dc5e4bec9614
6: version: 1.0.0
7: ---
8: 
9: # Expose id-based REQ document reads as a tool (get_req), not a resource
10: 
11: ## Context and Problem Statement
12: 
13: feat-6-requirement-artifact Task 3.17 deliberately exposed id-based single-document reads for the REQ domain only as an MCP resource (`specmgr://req/{id}`, `req/resources/req_get.py`), explicitly superseding an earlier-considered `get_req` tool -- the stated rationale was "id-based single-document read is a resource only, everything else in this surface is a tool". This mirrored the *shape* of the ADR domain's `specmgr://adr/{id}` resource, except ADR also ships a `get_adr` tool alongside it, so the two domains were never actually symmetric.
14: 
15: In practice, LLM/agent clients calling this MCP server fail to reliably invoke `specmgr://req/{id}` to retrieve a requirement by id -- resources are a much less-used affordance for on-demand, parameterized lookups than tools are, in current agent tool-use patterns. This defeats the purpose of exposing the lookup at all: the calling model either skips the read entirely, or falls back to less reliable paths (e.g. reading `specmgr://req/list` and guessing, or trying to read the underlying `.md` file directly off disk). This was raised as feat-7-various-improvements Task 0.9, which also asks whether the same reasoning should retroactively apply to the already-shipped `get_adr` tool / `specmgr://adr/{id}` resource pair.
16: 
17: ## Decision Drivers
18: 
19: - Reliability: in observed practice, LLM agents invoke tools far more reliably than resources for on-demand, parameterized (id-based) data retrieval.
20: - Consistency across document domains (`adr`, `req`, and future `uc`/`ac`) for the same conceptual operation ("read one document by id").
21: - Avoid permanently maintaining two parallel code paths (tool and resource) for the same read when the resource path is rarely, if ever, actually exercised by callers.
22: - Minimize churn to the already-shipped, working ADR domain surface, which has no reported reliability problem to date.
23: 
24: ## Considered Options
25: 
26: - Option 1: Add `get_req` tool, keep `specmgr://req/{id}` resource (tool and resource coexist, mirroring how ADR already works)
27: - Option 2: Add `get_req` tool, remove `specmgr://req/{id}` resource entirely (REQ becomes tool-only for id-based reads)
28: - Option 3: Do nothing -- keep REQ resource-only, reaffirming feat-6 Task 3.17's original decision
29: 
30: ## Decision Outcome
31: 
32: Chosen option: "Option 2: Add `get_req` tool, remove `specmgr://req/{id}` resource entirely", because the resource has demonstrated the exact reliability problem this ADR describes, and keeping a rarely-invoked resource around after adding the tool would only add maintenance surface (two code paths, two test suites, two docstring entries) for a path that isn't actually helping callers.
33: 
34: This ADR explicitly does **not** extend the change to the ADR domain: `specmgr://adr/{id}` (`adr_get`) stays coexisting with the already-shipped `get_adr` tool, unchanged. This is a deliberate, accepted cross-domain divergence -- not an oversight -- recorded here so a future reader does not assume the two domains were meant to be symmetric. Any future document domain (`uc`/`get_uc`, `ac`/`get_ac`, ...) should follow the newer REQ precedent (tool-only for id-based reads) rather than the older ADR precedent, unless a specific reason to add a resource counterpart is identified at that time.
35: 
36: ### Consequences
37: 
38: Good, because REQ's id-based read becomes reliably invocable by agents via a normal tool call, matching every other REQ lifecycle operation (`create_req`, `update_req`, `set_status_req`, `validate_req`), which are already tools.
39: Good, because it establishes a clear default for future document domains: id-based single-document read is a tool first; a resource counterpart is only added if a concrete need for non-tool-mediated context retrieval emerges.
40: Bad, because the ADR and REQ domains now visibly diverge in their tool/resource surface for the same conceptual operation (ADR keeps both `get_adr` tool and `adr_get` resource; REQ has only `get_req`) -- readers of both domains side by side must know this is intentional, not a bug, which is why it is written down here.
41: Neutral, because this reverses part of feat-6 Task 3.17's original design without reopening feat-6 itself -- feat-6's README is annotated with a pointer to this ADR rather than rewritten.
42: 
43: ## More Information
44: 
45: Supersedes the `specmgr://req/{id}`-only decision recorded in feat-6-requirement-artifact/README.md Task 3.17. Tracked as feat-7-various-improvements Task 0.9 (sub-tasks 0.9.1-0.9.13).

(End of file - total 45 lines)
</content>
```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 310.4s)

_Thinking:_

The ADR's rationale is clear, and directly answers the user's question:

1. **Empirical reliability finding**: LLM/agent clients fail to reliably invoke parameterized resources like `specmgr://req/{id}` for on-demand lookups — "resources are a far less used affordance than tools for on-demand parameterized lookups in current agent tool-use patterns." As a result, the calling model either skips the read or falls back to less reliable paths. This was the very reason `get_req` was added and the resource removed (2026-08-15, based on observed practice).

2. **Cross-domain default established**: "For future document domains, id-based single-document reads are tool-first. Resource counterparts are only added if a concrete need for non-tool-mediated context retrieval emerges."

3. **Maintenance cost**: Two parallel code paths (tool + resource), two test suites, two docstring entries — for a path that "is rarely, if ever, actually exercised by callers."

4. **Precedent**: Every domain after REQ (uc, tsk, qa, prb, gol, rsk) followed the tool-only precedent. Re-introducing `/{id}` resources for 7 domains would mean reversing an accepted ADR across all of those domains, and would require a superseding ADR.

Now, is there any merit in the user's alternative? What `specmgr://X/{id}` would offer:

- A resource template the host could enumerate. Resources in OpenCode: MCP resources can be browsed, and in some hosts can be attached as context. The ADR's finding is that *agents* don't reliably *invoke* them.
- If the resource returned raw markdown… but wait, what did the old `specmgr://req/{id}` resource return? Presumably a parsed document (structured). A raw-markdown resource would be a new semantic.
- In this MCP SDK (2.0.0), resources with URI templates: `specmgr://req/{id}` would be registered as a resource template, and the client would read it by concrete URI. For an LLM in a conversation, reading a resource means a `resources/read` call — in OpenCode, that is available to the model (list_mcp_resources/read_mcp_resource tools exist in this environment!). So it's not entirely unusable — but the ADR records observed unreliability with exactly this pattern (feat-7 Task 0.9 was raised from real experience).

Further note: in this very environment I have `list_mcp_resources`/`read_mcp_resource` tools — so resources are mechanically accessible to agents. But the ADR's empirical claim stands: in practice, agent flows reliably use tools for parameterized on-demand reads.

Another consideration: the `raw` parameter on `get_X` solves the need (line numbers for range updates) with a single call inside the existing reliable tool path, and the narration can say "call get_X(id, raw=True)". A resource would require the agent to discover the template, construct the URI, and read it — three failure points, plus the resource surface the ADR explicitly moved away from (and the "minimize churn"/"consistency" drivers point the other way: get_X is what every domain's narration already tells the agent to call in step 1).

Also worth noting: ADR's own divergence — `specmgr://adr/{id}` still exists alongside `get_adr`. If the user wants the resource pattern for raw reads, the ADR domain already demonstrates the coexistence pattern works mechanically. But for the 7 domains, the established cross-domain default is tool-first.

My recommendation: **keep `get_X(raw=True)` and do not re-introduce `/{id}` resources.** Reasons:

1. Reverses an accepted ADR whose core finding (agent reliability with parameterized resources) was empirical, not theoretical.
2. Would create 7 new resource templates + code paths + tests + docs for a need (raw body text) that `get_X(raw=True)` satisfies with zero new surface objects and the exact same single-call shape the narration already prescribes ("read current state first" = get_X).
3. Consistency: every other on-demand id-based operation (get, update, set_status, validate, list) is a tool. The read that feeds range updates should be the same.
4. If the user still wants resources, the proper path is a superseding ADR — heavyweight for a marginal benefit.

I should present this concisely and then confirm the final decision so we can close the plan. Should I ask a question, or just recommend and confirm? The user asked "would it be better?" — a direct answer: No, and here's why. Then confirm Option A as locked. I think a short answer + one confirmation question (or just stating it's locked unless they object). Per plan-mode guidance, when trade-offs are involved I should ask the user's opinion — but I've already asked, and they responded with a sub-question. I'll answer the sub-question with a clear recommendation and ask for final confirmation via the question tool (re-introduce resource vs keep raw parameter) — that's cleanest: one binary question, my recommendation first.

Actually — let me reconsider whether I should just decide. The user's message: "Option A sounds good. But just a quick thought: would it be better to re-introduce resource/{id}...?" They're leaning A and probing the alternative. A well-grounded "no, because X" plus a confirmation is appropriate. I'll answer with the ADR evidence, give my recommendation, and ask one confirmation question (keep A vs switch to resource).

Keep the response concise: the ADR's empirical finding, the cross-domain default, the maintenance cost, what the resource would still require (a superseding ADR), and the point that `raw=True` satisfies the need with the same single-call shape the narration already uses. Then the question.

Short answer: **no — I'd keep `get_X(raw=True)` and not re-introduce `/{id}` resources.** The reasoning is recorded in the very ADR that removed them (ddfb1109, accepted 2026-08-15):

1. **It was an empirical finding, not a style preference.** In observed practice, LLM/agent clients *fail to reliably invoke* parameterized resources like `specmgr://req/{id}` for on-demand lookups — the model either skips the read or falls back to guessing from `list` or reading the `.md` off disk. That unreliability is exactly what `get_req` (feat-7 Task 0.9) fixed, and it's the core problem statement of the ADR.
2. **A cross-domain default was deliberately established:** "id-based single-document read is tool first; a resource counterpart is only added if a concrete need for non-tool-mediated context retrieval emerges." All six domains built after REQ (uc, tsk, qa, prb, gol, rsk) followed it.
3. **Cost/benefit for your specific need:** re-introducing the resource means 7 new resource templates + 7 code paths + 7 test suites + docs/MCP.md entries, and the agent still has to *discover the template, construct the URI, and issue a resources/read* — three failure points — for something the narration's step 1 ("read current state first") already prescribes as a single `get_X(id)` tool call. `get_X(id, raw=True)` is that same call with one optional flag.
4. **Reversing it would need a superseding ADR** (it's `accepted`, and it's cited in six domains' AGENTS.md bullets). Heavyweight machinery for a marginal benefit.

One honest nuance: the ADR domain keeps `specmgr://adr/{id}` alongside `get_adr` (a deliberate, documented divergence), so the pattern *works* mechanically. But ADR isn't affected by line-range updates, and the finding about agent reliability with parameterized resources applies to it too.

So the need — "client sees the exact body text that `begin`/`end` index into" — is served by the tool-first path.

**Tool: question**

**Input:**

```json
{
  "questions": [
    {
      "header": "Raw read path",
      "options": [
        {
          "description": "get_<d>(id, raw=False) on the 7 domain get-tools; raw=True returns the frontmatter-stripped body text verbatim. No ADR reversal, no new surface objects.",
          "label": "Keep raw param on get_X (Recommended)"
        },
        {
          "description": "Re-introduce specmgr://X/{id} resource templates returning raw markdown for the 7 domains, superseding ADR ddfb1109 (would need its own superseding ADR in Phase 1).",
          "label": "Re-introduce {id} resources"
        }
      ],
      "question": "Final call on how range-update clients obtain line numbers?"
    }
  ]
}
```

**Output:**

```
User has answered your questions: "Final call on how range-update clients obtain line numbers?"="Keep raw param on get_X (Recommended)". You can now continue with the user's answers in mind.
```

---

## Assistant (Plan · qwen3.8-27b-bf16-896k · 160.2s)

_Thinking:_

All decisions are finalized. Now let me put together the final, consolidated plan. Summary of all locked-in decisions:

1. `update(id, type, content, begin=None, end=None)` — 7 whole-body domains; line-range contract with N+1 EOF sentinel; no begin/end → current whole-body behavior; splice then validate the whole; frontmatter is never addressable.
2. `set_status(id, type, status, superseded_by=None)` — 8 types including adr; superseded_by is adr-only.
3. `get_<d>(id, raw=False)` — 7 domain get tools; raw=True → body text verbatim (frontmatter stripped).
4. The old 15 tools are removed entirely.
5. Per-domain prompts are retained, and all narration text is rewritten (11 data files + ADR 4 files + prompt docstrings + tests).
6. Create a short ADR via specmgr_create_adr (Phase 1) — should it now also record the line-range + raw read decision? The ADR's content should cover: type dispatch vs uuid only; exclusion of ADR from update; superseded_by; and the new: line-range update contract (begin/end, N+1 sentinel, splice-then-validate-whole) + the decision on the raw read path (get_X(raw=True) vs re-introducing /{id} resources — referencing ADR ddfb1109 as the basis for tool-first). Good — the ADR's options/considerations can be compact.
7. Phases (adjusted):
   - Phase 1: ADR
   - Phase 2: generic update (splice) + get_X raw parameter (7 tools) + tests + smoke test
   - Phase 3: retire the 7 update\_\*
   - Phase 4: generic set_status + retire 8
   - Phase 5: narration (15 data files: 7 update instructions + qa_refine + ADR 4 = 12… recounting: 7 × *_update_instructions.md + qa_refine_instructions.md + adr_create/adr_create_test/adr_update/adr_update_test_instructions.md = 12 data files; plus prompt Python docstrings: 7 prompts/update_*.py + 4 ADR prompt modules; plus tests: 7 domain prompt tests + 4 ADR prompt tests = 11 prompt test files)
   - Phase 6: cross-cutting docs (AGENTS.md, CHANGELOG, regen, zero drift)
   - Phase 7: final verification (ACC walkthrough, live e2e including range update + raw read + ADR superseded_by, tool count 71/25/19, status done)
8. "Recent Updates" exact section name in phase-end tasks.
9. Step 0: create README (me) → /implement-feature feat-0-consolidate-mutation-tools.

Changes in tool count: 84 − 15 + 2 = 71 tools; resources 25 (unchanged — no /{id} resources); prompts 19 (unchanged).

Acceptance criteria — final list:

- ACC-001: `update` whole-body mode: per-type semantics preserved (7 types), frontmatter carry-over, updated timestamp bump, status not settable, validation failure writes nothing, unknown id → domain NotFound. (Phase 2)
- ACC-002: `update` range mode: splice contract (1-based inclusive, N+1 sentinel, both-or-neither, empty content = delete), unchanged regions byte-identical to disk, whole-result validation absolute (structural + field negative cases, file unchanged on failure), append via begin=end=N+1, begin=1/end=N ≡ whole-body replace. (Phase 2)
- ACC-003: `get_<d>(raw=True)` returns body text verbatim (frontmatter stripped) for all 7 domains; raw=False behavior unchanged (regression). (Phase 2)
- ACC-004: `set_status`: 8 types, per-domain closed vocab enforced (including rsk's open/mitigating and uc's 5-value), ADR superseded_by composes "superseded by X", superseded_by on non-adr → ValueError, body unchanged (7 domains byte-identical, ADR render round-trip). (Phase 4)
- ACC-005: 15 tools removed from source and registration; grep-clean of `update_<d>`/`set_status_<d>` in src/ and docs/; vulture clean. (Phases 3/4)
- ACC-006: All narration references generic tools with correct signatures (12 data files, prompt docstrings, 11 prompt test files green). (Phase 5)
- ACC-007: Docs zero drift (docs/api, docs/MCP.md, docs/adr/README.md); server.py docstring is accurate; AGENTS.md updated; CHANGELOG breaking entries. (Phase 6)
- ACC-008: ADR recorded and accepted; live end-to-end against a temp SPECMGR_DOCS_DIR: for req/rsk/uc create→get(raw=True)→range update→set_status; ADR superseded_by composition; 71/25/19 on the actual mcp instance; fresh-import smoke test. (Phases 1/7)

Hmm, 8 ACCs. No problem.

Requirements:

- REQ-001: generic update (whole-body, 7 types)
- REQ-002: range update (begin/end contract)
- REQ-003: get_X raw parameter
- REQ-004: generic set_status (8 types, superseded_by)
- REQ-005: remove 15 old tools
- REQ-006: narration rewrite
- REQ-007: docs/registration/ADR/CHANGELOG consistency

Design notes to add: splice mechanics (frontmatter.loads's content, splitlines, N+1 sentinel rule, verbatim persistence of the spliced text, format_text for validation), raw read definition (body = frontmatter-stripped text as on disk — same read path as splice, guaranteeing coordinate consistency: "what raw returns is exactly what begin/end index into" — this is a critical invariant: raw=True's output must be the very text used for splicing, so implement both from the same helper), import-order smoke test, Literal enum, union return types.

That invariant is worth making explicit: raw read and splice share the same body-extraction helper, so the coordinates the client sees == the coordinates the server splices against.

Now to write the final plan message. Since everything is approved, it should be a concise, complete "final plan" the user can approve for execution. Structure:

- Locked-in decisions (including new: range contract, raw parameter)
- Step 0 (me): README at .specmgr/feat/feat-0-consolidate-mutation-tools/
- Feature README: requirements, ACC, phase table (with "Recent Updates" wording), orchestration
- Final state numbers: 71/25/19

Keep it concise — use the phase table again, with the updated Phase 2 scope. No more questions needed. Close with "approve and I'll write the README."

All decisions are locked. Final consolidated plan:

## Feature: `feat-0-consolidate-mutation-tools`

**Locked design**

1. **`update(id, type, content, begin=None, end=None)`** — 7 whole-body domains (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`):
   - No `begin`/`end` → exactly today's whole-body replace (default + fallback).
   - Both given → `content` is a fragment replacing body lines `begin`…`end`: **1-based, inclusive**, body-relative (frontmatter excluded, never addressable), with an **`N+1` EOF sentinel** (`begin=end=N+1` = append, `end=N+1` = through end of body, one-of-two = error, empty `content` = delete the range).
   - **Splice-then-validate-whole:** fragment is spliced into the current on-disk body, and the *result* must pass the domain's full validation before anything is written; unchanged regions stay byte-identical to disk.
2. **`get_<d>(id, raw=False)`** on the 7 domain get-tools — `raw=True` returns the frontmatter-stripped body text verbatim. **Invariant:** raw-read and splice share the same body-extraction helper, so the text the client counts lines in *is* the text the server splices. (Tool-first per ADR ddfb1109 — no `/{id}` resources re-introduced.)
3. **`set_status(id, type, status, superseded_by=None)`** — all 8 types incl. `adr`; per-domain closed vocab enforced via each domain's frontmatter class; `superseded_by` composes `"superseded by X"` for `adr` only, `ValueError` otherwise.
4. **15 old tools deleted outright** (7 `update_*`, 7 `set_status_*`, ADR `set_status`); per-domain prompts kept, all narration rewritten; **short ADR** records the conventions (type over uuid-only, ADR excluded from `update`, range contract, raw-read-over-resource).

**Step 0 (me, on approval):** create the feature README from the v1 template — requirements (REQ-001…007), acceptance criteria (ACC-001…008), scope, design notes, and the phase task list below, frontmatter `status: planning`.

**Phases** (each phase ends with: full quality gate — `ruff format --check`, `ruff check`, `vulture`, full `unittest` suite, plus the `specmgr docs`/`mcp-docs`/`adr-toc`/`schema` drift checks it touches — and a dated entry in the **Recent Updates** section + Current Status + task-line flip):

| Phase | Scope |
|---|---|
| 1 — ADR | Create via `specmgr_create_adr` (status `accepted`); `specmgr adr-toc` |
| 2 — Generic `update` + raw read | `general/tools/update.py` (7 verbatim adapters + splice helper + dispatch + tool), `raw` param on 7 `get_<d>` tools, registration, `server.py` docstring, `tests/general/tools/test_update.py` (whole-body + range: N+1 append, delete-range, byte-identity, all negatives with file-unchanged proofs), raw-read tests (7 domains, `raw=False` regression), fresh-import + `list_tools()` smoke test; gate verifies `type` renders as enum in MCP.md |
| 3 — Retire `update_*` | Delete 7 modules + 7 test files; fix 7 `tools/__init__.py` + 7 domain `__init__.py` docstrings; `server.py` −7 lines; narration files untouched (Phase 5 owns them) |
| 4 — Generic `set_status` + retire 8 | `general/tools/set_status.py` (8 adapters + `superseded_by` guard); delete ADR `set_status` + 7 `set_status_*` + 8 test files (name-collision forces one phase); registration + docstrings; `tests/general/tools/test_set_status.py` (8 types, vocab negatives incl. rsk/uc, composition, ValueError) |
| 5 — Narration | Grep-driven rewrite of 12 data files (7 `*_update_instructions.md`, `qa_refine_instructions.md`, 4 ADR instruction files) teaching the range flow ("localized change → `get_X(id, raw=True)` → find lines → `update(…, begin, end)`; multi-section/uncertain → whole-body"); prompt Python docstrings (7 + 4 ADR); 11 prompt test files |
| 6 — Cross-cutting docs | `AGENTS.md` (per-domain bullets, `general` bullet, "missing" list), `CHANGELOG.md` `[Unreleased]` breaking entry, final regeneration — zero drift |
| 7 — Final verification | Walk ACC-001…008 with evidence; live end-to-end in temp `SPECMGR_DOCS_DIR`: `create`→`get(raw=True)`→**range** `update`→`set_status` for req/rsk/uc, ADR `superseded_by` composition; confirm **71 tools / 25 resources / 19 prompts** on the real `mcp` instance; set README `status: done` |

**Hand-off (you):** `/implement-feature feat-0-consolidate-mutation-tools` → phase-orchestrator drives Phases 1–7 (one fresh phase-implementer per phase, independent gate re-verification, one Conventional Commit per phase with your confirmation, blockers/questions surfaced to you).

Approve and I'll write the README (Step 0).

---

## User

go

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 340.1s)

_Thinking:_

The user approved. Now I'll execute Step 0: create the feature README at `.specmgr/feat/feat-0-consolidate-mutation-tools/README.md`.

Wait — the feature id. The user selected "0 (no issue yet)", so the id is `feat-0-consolidate-mutation-tools`.

The README needs to contain a complete plan. The Phase-Orchestrator reads it, and the Phase-Implementer implements each phase. Following the template (`.specmgr/_template/v1/README.md`) and ADR e369ee2e, let me carefully draft the complete content:

Frontmatter:

```yaml
---
id: feat-0-consolidate-mutation-tools
version: 1.0.0
status: planning
created: 2026-08-26
updated: 2026-08-26
---
```

Note: feat-18's frontmatter was key-sorted (created, id, status, updated, version) — probably because specmgr mdformat or their habit sorts frontmatter keys. The template shows the order id, version, status, created, updated. feat-18 (the actual feature) shows alphabetical order: created, id, status, updated, version. Let me match the actual repo convention (alphabetical) — the existing feature READMEs probably use it. Let me quickly check one more feature's frontmatter… feat-18's was `created, id, status, updated, version`. I'll use that order.

Title: `# Feature: Consolidate update and set_status tools into generic type-dispatched tools`

Sections:

- ## Plan
  - ### Overview
  - ### Requirements (REQ-001..007)
  - ### Acceptance Criteria (ACC-001..008)
  - ### Scope (what's included / what's explicitly out of scope)
  - ### Dependencies
  - ### Design Notes (detailed: tool signatures, splice contract, raw-read invariants, dispatch architecture, import ordering, naming conventions, per-domain status vocabularies, return types, ADR notes, doc discipline)
  - ### Related ADRs
  - ### Task List (phases 1..7, with tasks, dependencies, status: not-started)
- ## Progress
  - ### Current Status
  - ### Blockers (none)
  - ### Recent Updates (initial entry: feature planned)
  - ### Decisions Made (record the decisions made during planning — these are already in the design, but the Decisions Made log is for decisions made *during implementation*; still, I can seed the key planning-session decisions dated 2026-08-26: explicit type over uuid-only; ADR out of scope for update; full deletion (no deprecated wrappers); prompts kept per-domain; short ADR; begin/end line ranges with N+1 sentinel; get_X(raw=True) over reintroducing /{id} resources (per ADR ddfb1109). This is useful for the implementer.)
  - ### Related PRs / Commits (empty / "none yet")

Now let me carefully write the task list — it needs to be detailed enough for a fresh phase-implementer. What the phase-implementer gets: the plan path, the phase heading, the task verbatim, dependencies, gate instructions. So each task line should be self-contained.

Phase structure (from the approved plan):

#### Phase 1: ADR

- Task 1.1: Create ADR via `specmgr_create_adr` MCP tool (never hand-write the file — ADR 898bfcd0). Title: "Consolidate whole-body update and status-change tools into generic type-dispatched tools". Status: `accepted`. Contents:
  - Context: 15 near-duplicate mutation tools (7 whole-body `update_<d>`, 7 `set_status_<d>`, ADR `set_status`) each taking (id, content/status); future domains (ac) would add more; LLM clients see 15 near-identical tools.
  - Decision drivers: simplify tool surface; no write-path directory scan (uuid-only resolution would require scanning all domain directories, cost grows with domains, plus independent v4 UUIDs per domain are not guaranteed-unique); client already knows the domain; keep the filesystem-as-source-of-truth + full-validation invariant.
  - Considered options: (1) generic tools with explicit `type` parameter [chosen]; (2) uuid-only resolution (scan all domains); (3) keep per-domain tools.
  - Decision outcome + consequences: breaking (14 per-domain tools removed; ADR `set_status` signature gains a required `type`); ADR is excluded from `update` (its section-level MADR contract — update_frontmatter/update_section/option\_\* — is deliberate, no whole-body replace); ADR is included in `set_status` with a `superseded_by` special case; future domains add one dispatch entry (and a `raw` getter parameter), no new tool; the `update` line-range contract (1-based inclusive begin/end, N+1 EOF sentinel, splice-then-validate-whole, frontmatter not addressable) and `get_<d>(raw=True)` body-text read — the raw read is tool-first per ADR ddfb1109 (reintroducing `specmgr://<d>/{id}` resource was considered and rejected).
  - Related: ddfb1109 (tool-first id reads), ece4554b (domain-first layout — the generic tools live in `general/tools/` per the cross-cutting rule), 3bf0326f (mcp singleton module), 71fd95d7 (ADR's update_section — the contract `update` does not adopt for ADR).
- Task 1.2: Run `uv run --frozen specmgr adr-toc`; verify the new ADR appears in `docs/adr/README.md`; verify ADR is `specmgr mdformat` clean (validate_adr via MCP `specmgr_validate_adr`).
- Task 1.3: Phase-end quality gate — full gate (ruff format --check, ruff check, vulture src/ whitelist.py --min-confidence 60, full unittest suite); add a dated entry to the Recent Updates section, update Current Status, flip task lines to done in place.

#### Phase 2: Generic `update` tool + `raw` read parameter

- Task 2.1: `general/tools/update.py`:
  - Private body-extraction helper: returns the frontmatter-stripped body text of the file at `path` exactly as it appears on disk (same `frontmatter.loads(path.read_text()).content` mechanism the 7 `set_status_<d>` tools already use) — shared by the splice path (and by Task 2.3's raw read, via the per-domain `_io`/`read_<d>`? Hmm — the raw read is inside get\_<d>, which returns a `str`. The helper is… let me define: `general/tools/_body_text.py`? Or a function in `general/tools/update.py` that the get tool imports. Domain get tool importing from general.tools is an established pattern (get\_\*\_example imports _packaged_data). So: `general/tools/_update_core.py`? Simpler: put `body_text(path: Path) -> str` + `splice_body(current: str, begin: int, end: int, content: str) -> str` + `resolve_range(...)` in `general/tools/_splice.py` (private, no mcp dependency). update.py imports; domain get_<d>.py imports for raw. Good.
  - `splice_body(current_body, begin, end, content)`: N = len(current_body.splitlines()); validate 1 ≤ begin ≤ end ≤ N+1; lines = current.splitlines(); del lines[begin-1:end] (if end ≤ N); insert content lines at begin-1 (content.split("\\n"), drop trailing empty if content ends with "\\n"); result = "\\n".join(lines) + "\\n".
  - 7 private adapter functions `_update_<d>(id_, content, begin, end)` — verbatim port of each `update_<d>` body, with the range branch added: no begin/end → current behavior (validate `X.from_text(format_text(content))`, write content verbatim); with range → load raw body via helper, splice, validate `X.from_text(format_text(spliced))`, write spliced verbatim. Frontmatter carry-over + updated-timestamp bump + lock + write_X_file + XNotFoundError preserved as-is.
  - Dispatch table: `dict[str, Callable]` with module-level ALL_CAPS constants? Convention: comparison constants. Use `UPDATE_TYPES = ("req","uc","tsk","qa","prb","gol","rsk")` and a `_DISPATCH: dict[str, ...]`.
  - `@mcp.tool(name="update", title="Update document", description=...)` `def update(id: str, type: Literal["req","uc","tsk","qa","prb","gol","rsk"], content: str, begin: int | None = None, end: int | None = None) -> ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument | GolDocument | RskDocument`.
  - Convention compliance: assert on parameters (both-or-neither rule for begin/end is a user-facing error → ValueError, not assert! Convention rule 3: assert is only for program invariants; user-controlled inputs → proper exceptions. The 7-value type is enforced by the schema (Literal); begin/end given-one-only / out-of-range / begin>end → ValueError with a clear message (client-facing), since these are user-controlled. Hmm — existing tools propagate AssertionError/ValidationError uncaught. For the new range-parameter misuse, ValueError with a clear message is the right choice (document it).
  - docstring: full numpy-style per convention.
- Task 2.2: Register in `general/tools/__init__.py` (import + `__all__` + docstring update).
- Task 2.3: `raw` parameter on the 7 domain get tools (`req/tools/get_req.py`, `uc/tools/get_uc.py`, `tsk/tools/get_tsk.py`, `qa/tools/get_qa.py`, `prb/tools/get_prb.py`, `gol/tools/get_gol.py`, `rsk/tools/get_rsk.py`): signature `get_<d>(id: str, raw: bool = False) -> XDocument | str`; `raw=False` → unchanged behavior (returns the parsed document); `raw=True` → returns the frontmatter-stripped body text verbatim (via the shared helper in Task 2.1 — same text the splice indexes, so coordinates the client sees == coordinates the server splices). Update docstring (Returns section) + `@mcp.tool` description. Note: the raw read must resolve the path under the same base directory; no lock needed (read-only, matching other get\_).
- Task 2.4: `server.py` module docstring: add `update` to the General tools line, with a one-line description (whole-body or line-range replace, `type` is the domain, `begin`/`end` are optional 1-based inclusive body-line range with N+1 EOF sentinel); note the `raw` parameter on the get\_<d> lines (concise: "…`get_req` (with optional `raw` flag returning body text)…" — actually, keep the server docstring concise; the get lines are already listed in the per-domain Tools lines. Update the Tools section wording accordingly).
- Task 2.5: `tests/general/tools/test_update.py` — per type (parameterize over all 7):
  - Whole-body mode (no begin/end): body replaced; frontmatter preserved (id/type/status/created/version); `updated` bumped; status is not settable (content has no frontmatter); invalid content → AssertionError (structural) or pydantic.ValidationError (field), file unchanged (byte-identical before/after); unknown id → domain `XNotFoundError`.
  - Range mode: replace a middle paragraph → resulting file = on-disk lines outside the range byte-identical + fragment at the range; append via begin=end=N+1; replace to EOF via end=N+1; delete an optional section (range covering heading+content+trailing blank, empty content) → doc valid; begin=1&end=N ≡ whole-body replace (resulting file equals whole-body mode with the same text); negative: begin given without end / end without begin → ValueError; begin>end → ValueError; begin\<1 → ValueError; end>N+1 → ValueError; range deleting the H1 → AssertionError, file unchanged; range producing an invalid field value (e.g. REQ `## Level` value outside the closed set / RSK `### Probability 6`) → ValidationError, file unchanged.
  - Fixture strategy mirrors existing tests (temp SPECMGR_DOCS_DIR, seed docs via the domain create tools or fixtures).
- Task 2.6: Raw-read tests — extend each domain's `tests/<d>/tools/test_get_<d>.py` (or add a new test class inside the existing file): `raw=True` returns body text verbatim (byte-identical to the frontmatter-stripped on-disk body), `raw=False` unchanged (regression), unknown id → XNotFoundError in both modes.
- Task 2.7: Registration smoke test: fresh import of `biz.dfch.specmgr.server` (subprocess `uv run --frozen python -c "import biz.dfch.specmgr.server"` as part of the gate, plus a unittest that `asyncio.run(mcp.list_tools())` contains "update" and the tool's inputSchema renders `type` as a 7-value enum and `begin`/`end` as optional integers).
- Task 2.8: Phase-end quality gate — full gate (ruff format --check, ruff check, vulture, full unittest suite including the new tests) + `specmgr mcp-docs` + `specmgr docs` regeneration, then verify zero drift (`git diff --exit-code -- docs/`); verify docs/MCP.md shows the `update` entry with the enum; add a dated entry to Recent Updates, update Current Status, flip task lines.

#### Phase 3: Retire the per-domain `update_*` tools

- Task 3.1: Delete the 7 modules: `req/tools/update_req.py`, `uc/tools/update_uc.py`, `tsk/tools/update_tsk.py`, `qa/tools/update_qa.py`, `prb/tools/update_prb.py`, `gol/tools/update_gol.py`, `rsk/tools/update_rsk.py`.
- Task 3.2: Delete the 7 test files: `tests/req/tools/test_update_req.py`, `tests/uc/tools/test_update_uc.py`, `tests/tsk/tools/test_update_tsk.py`, `tests/qa/tools/test_update_qa.py`, `tests/prb/tools/test_update_prb.py`, `tests/gol/tools/test_update_gol.py`, `tests/rsk/tools/test_update_rsk.py`.
- Task 3.3: Fix the 7 domain `tools/__init__.py` (remove import + `__all__` entry + update the module docstring's tool list) and the 7 domain `__init__.py` docstrings (remove `update_<d>` from the tool enumeration).
- Task 3.4: `server.py` module docstring: remove `update_<d>` from the 7 per-domain Tools lines (the `set_status_<d>` lines stay until Phase 4).
- Task 3.5: Grep verification: `grep -rn "update_req\|update_uc\|update_tsk\|update_qa\|update_prb\|update_gol\|update_rsk" src/ tests/` returns only: prompt Python modules + their data files (narration owned by Phase 5) — no code references in tools/models/general; document the residual list in the Progress entry.
- Task 3.6: Phase-end quality gate — full gate + `specmgr mcp-docs` + `specmgr docs` regeneration, zero drift (docs/MCP.md loses the 7 tool entries; docs/api loses the 7 pages… wait, docs/api is generated from modules — deleted modules → pages disappear; that's fine, the regeneration handles it); Recent Updates + Current Status + flip task lines.

#### Phase 4: Generic `set_status` + retire the 8 old status tools

- Task 4.1: `general/tools/set_status.py`:
  - 8 private adapters: the 7 verbatim ports of `set_status_<d>` (raw body re-read, frontmatter reconstruction via domain class so closed vocab validates, updated-timestamp bump, write verbatim, XNotFoundError) + the ADR port (load_by_id, `models.adr.v1.mutations.set_status(adr, status, superseded_by)`, write_adr render round-trip, adr_lock, AdrNotFoundError).
  - Guard: `superseded_by` is non-None and type != "adr" → ValueError (message: superseded_by is only supported for type "adr").
  - Dispatch table + `@mcp.tool(name="set_status", title="Set document status", description="...")` `def set_status(id: str, type: Literal["req","uc","tsk","qa","prb","gol","rsk","adr"], status: str, superseded_by: str | None = None) -> <8-way union>`.
- Task 4.2: Delete `adr/tools/set_status.py` + the 7 `set_status_<d>.py` modules + the 8 test files (`tests/adr/tools/test_set_status.py`, `tests/<d>/tools/test_set_status_<d>.py` ×7).
- Task 4.3: Register in `general/tools/__init__.py`; fix `adr/tools/__init__.py` (import/__all__/docstring) + the 7 domain `tools/__init__.py` + the 8 domain `__init__.py` docstrings (remove set_status enumeration; note in the adr domain docstring that status changes go through the generic `set_status`).
- Task 4.4: `server.py` module docstring: remove `set_status_<d>` from the 7 per-domain lines, remove `set_status` from the ADR line, add `set_status` to the General tools line (note the adr-only superseded_by).
- Task 4.5: `tests/general/tools/test_set_status.py` — per type (all 8): status changed + `updated` bumped + body unchanged (7 domains: raw body byte-identical; ADR: render round-trip, re-parsed doc equal to pre-doc except status/updated); per-domain closed-vocab enforcement (negative with an out-of-set value — e.g. "implemented" for rsk? Note: rsk's vocab — I've confirmed open/mitigating/… but not the full set; the test should use a value that is valid in one domain and invalid in another, e.g. "implemented" (valid for req/gol, invalid for rsk/uc/prb/qa/tsk? uc's set is draft/proposed/accepted/deprecated/superseded — no implemented, no rejected!; prb/qa/tsk are "draft", "active", … — need the full set. Instruction to the implementer: read each domain's `_ALLOWED_STATUSES` and build the positive/negative cases from the actual sets) — plus ADR: `set_status(id, "adr", "superseded", superseded_by="<other id>")` composes to "superseded by <other id>"; plain status values work for ADR; `superseded_by` with any non-adr type → ValueError, file unchanged; unknown id → domain/AdrNotFoundError.
- Task 4.6: Phase-end quality gate — full gate + `specmgr mcp-docs` + `specmgr docs` regeneration, zero drift; Recent Updates + Current Status + flip task lines.

#### Phase 5: Rewrite the narration (prompts + instruction data)

- Task 5.1: Grep-driven: find all references in `src/biz/dfch/specmgr/**/data/*.md` to `update_<d>`, `set_status_<d>`, bare `set_status(`. Rewrite (12 files expected):
  - 7 × `<d>_update_instructions.md` (req, uc, tsk, qa, prb, gol, rsk): `update_<d>(id, content)` → `update(id, type="<d>", content)`; `set_status_<d>(id, status)` → `set_status(id, type="<d>", status)`; add a range-update section: "for a localized change (a single paragraph/field/section), first call `get_<d>(id, raw=True)` to see the exact body text, identify the 1-based line range (an optional `begin`/`end` pair; `N+1` = end of body), and pass only the replacement lines to `update(..., begin=…, end=…)`; for multi-section or uncertain changes, use the whole-body replace (no begin/end)"; fix per-domain status-vocab prose where it differs (rsk's open/mitigating/…, uc's 5-value).
  - `qa/data/qa_refine_instructions.md`: `update_qa` references → `update(id, type="qa", …)` (refine is append → use the N+1 append range if the append is clean, otherwise whole-body; keep the existing "carry-forward" guidance for the whole-body path).
  - 4 × ADR instruction files (`adr_create_instructions.md`, `adr_create_test_instructions.md`, `adr_update_instructions.md`, `adr_update_test_instructions.md`): `set_status(id, status[, superseded_by])` → `set_status(id, type="adr", status[, superseded_by])`.
- Task 5.2: Fix prompt Python module docstrings that enumerate retired tools: 7 × `prompts/update_<d>.py` (docstring mentions `update_<d>` tool) + the 4 ADR prompt modules (`create_adr.py`, `create_adr_test.py`, `update_adr.py`, `update_adr_test.py` mention `set_status` — the name is still correct (now generic); verify the wording stays accurate, e.g. "the `set_status` tool (now generic, `type="adr"`)" — adjust only where it would become false).
- Task 5.3: Update the 11 prompt test files (7 × `tests/<d>/prompts/test_update_<d>.py` — note: rsk's prompt is named `update_risk` → `tests/rsk/prompts/test_update_risk.py`; 4 × `tests/adr/prompts/test_*.py`) so the rendered-text assertions match the rewritten instruction files (assert the new call shapes appear; keep the existing structural assertions).
- Task 5.4: Phase-end quality gate — full gate (prompt data files are package data; `specmgr docs` regeneration if docstrings changed — they did in Task 5.2) + zero drift; Recent Updates + Current Status + flip task lines.

#### Phase 6: Cross-cutting docs and release notes

- Task 6.1: `AGENTS.md`: per-domain bullet points — remove `update_<d>`/`set_status_<d>` from each domain's tool enumeration (req/uc/tsk/qa/prb/gol/rsk); ADR bullet — remove `set_status` from the 12-wrapper enumeration (now 11); `general/` bullet — add `update` (7-type whole-body/line-range replace with begin/end + N+1 sentinel) and `set_status` (8-type with adr-only superseded_by), and note the `raw` parameter on the get tools; update the "Still genuinely missing / not yet done" list as needed (the validate\_ line unchanged; add a note that future domains (ac) add one dispatch entry + a raw getter, no new update/set_status tool); note the new ADR id in the relevant spots.
- Task 6.2: `CHANGELOG.md` `[Unreleased]`: **Breaking**: removed 14 MCP tools (`update_req`, `update_uc`, `update_tsk`, `update_qa`, `update_prb`, `update_gol`, `update_rsk`, `set_status_req`, `set_status_uc`, `set_status_tsk`, `set_status_qa`, `set_status_prb`, `set_status_gol`, `set_status_rsk`); ADR `set_status` signature changes from `(id, status, superseded_by)` to `(id, type, status, superseded_by)` with `type="adr"` required. **Added**: generic `update(id, type, content, begin, end)` (7 types; optional 1-based inclusive body-line range, N+1 EOF sentinel, splice-then-validate-whole) and generic `set_status(id, type, status, superseded_by)` (8 types); optional `raw: bool = False` on the 7 `get_<d>` tools (returns the body text verbatim, frontmatter-stripped — the text `begin`/`end` indexes into). Reference the new ADR.
- Task 6.3: Final regeneration: `specmgr docs`, `specmgr mcp-docs`, `specmgr adr-toc`, `specmgr schema` (models unchanged → expect zero changes); verify zero drift with `git diff --exit-code -- docs/`.
- Task 6.4: Phase-end quality gate — full gate; Recent Updates + Current Status + flip task lines.

#### Phase 7: Final cross-cutting verification

- Task 7.1: Walk all of ACC-001…008 and verify each with concrete evidence (annotate the Acceptance Criteria section inline, as feat-18 did); live end-to-end in a temp SPECMGR_DOCS_DIR (no mocks): for req, rsk, uc — `create_<d>` → `get_<d>(id, raw=True)` → `update(id, type, content, begin, end)` (middle-range replace + one N+1 append) → `get_<d>` (verify) → `set_status(id, type, status)` (domain-valid value) → `get_<d>`; ADR — `create_adr` → `set_status(id, type="adr", status="superseded", superseded_by=…)` → verify the composed status string; verify `asyncio.run(mcp.list_tools()/list_resources()/list_prompts())` on the real server.mcp: **71 tools / 25 resources / 19 prompts**; fresh-import subprocess check.
- Task 7.2: Set the README frontmatter `status: done`; final Recent Updates + Current Status; flip Task 7.1.

ACC list (final):

- ACC-001: verifies REQ-001 — `update` whole-body mode preserves the per-type semantics of all 7 domains (body replaced; id/type/status/created/version preserved; `updated` bumped; status not settable; structural/field validation failure writes nothing; unknown id → domain NotFound).
- ACC-002: verifies REQ-002 — range mode honors the contract (1-based inclusive; both-or-neither; N+1 sentinel for append and through-EOF; empty fragment = range deletion; unchanged regions byte-identical to disk; begin=1/end=N ≡ whole-body; all out-of-range/misuse cases raise without writing).
- ACC-003: verifies REQ-003 — `get_<d>(raw=True)` returns the frontmatter-stripped body verbatim for all 7 domains; the returned text is the very text the splice indexes (shared helper); `raw=False` regression-clean.
- ACC-004: verifies REQ-004 — `set_status` works for all 8 types; per-domain closed vocab enforced (including rsk and uc's differing sets); ADR `superseded_by` composes "superseded by X"; `superseded_by` on non-adr → ValueError; body unchanged.
- ACC-005: verifies REQ-005 — 15 tools removed from source and registration; grep-clean (residual references only in Phase-5-owned narration, then zero); vulture clean.
- ACC-006: verifies REQ-006 — all 12 instruction data files + prompt docstrings reference the generic tools with correct signatures; the 11 prompt test files green; the range-update flow is taught in all 7 domain update instructions.
- ACC-007: verifies REQ-007 — zero doc drift (docs/api, docs/MCP.md, docs/adr/README.md, schema); server.py docstring accurate; AGENTS.md updated; CHANGELOG breaking entry.
- ACC-008: verifies REQ-001/004/005 — ADR recorded and accepted; live end-to-end runs (per the Phase 7.1 list) pass; 71/25/19 on the real mcp instance; fresh import clean.

Requirements:

- REQ-001: A generic `update(id, type, content)` tool for the 7 whole-body domains with per-type semantics preserved 1:1.
- REQ-002: Optional `begin`/`end` line range on `update` (contract in Design Notes).
- REQ-003: Optional `raw: bool = False` on the 7 `get_<d>` tools returning the body text verbatim.
- REQ-004: A generic `set_status(id, type, status, superseded_by=None)` for 8 types (adr-only superseded_by).
- REQ-005: Removal of 15 per-domain/ADR mutation tools.
- REQ-006: All prompt narration (data files + docstrings + tests) references the generic tools.
- REQ-007: Docs/registration consistency: server.py docstring, docs/MCP.md, docs/api, docs/adr/README.md, AGENTS.md, CHANGELOG.md, plus the ADR.

Scope:
Included:

- `general/tools/update.py`, `general/tools/set_status.py`, `general/tools/_splice.py` (helpers), registration.
- `raw` parameter on 7 get tools.
- Removal of 15 tools + their tests.
- Narration rewrite (12 data files + docstrings + 11 test files).
- Docs/AGENTS/CHANGELOG/ADR.
  Out of scope:
- ADR's section-level tools (update_frontmatter, update_section, option\_\*) unchanged; no whole-body `update` for ADR.
- No reintroduction of `specmgr://<d>/{id}` resources (ADR ddfb1109).
- No consolidation of create\_*/get\_*/validate\_*/delete\_* (delete\_\* remain stubs).
- No schema/model changes (status vocabularies unchanged).
- No version bump (release-time concern).
- No `ac` domain (doesn't exist yet).
- No changes to `set_status`/`update` for the `tsk` implement_task prompt? — hmm, implement_task's instruction file: does it reference update_tsk? It reads the task list via get_tsk and builds a TodoWrite… my Phase 5 grep-driven task catches any references in any data file, so I'll list it as covered by the grep. Fine.

Dependencies:

- Depends on: ADR ddfb1109 (tool-first id reads — the basis for raw over resource), ADR ece4554b (domain-first; general/ cross-cutting home), ADR 3bf0326f (mcp singleton in its own module — import-order concern), ADR 71fd95d7 (ADR update_section contract — what update does not adopt for ADR), ADR 898bfcd0 (ADRs only authored via MCP tools), ADR 33c5ab08 (filesystem is sole source of truth — splice-then-write preserves), existing `general/tools/_doc_paths.py`/`_packaged_data.py` infrastructure.
- Blocks: none. Future `ac` domain work must add a dispatch entry, not a new tool.

Design Notes — what to include:

1. Dispatch architecture (adapter = verbatim port; table; why general/tools/; conventions: assert vs ValueError).
2. update signature + return union.
3. Splice contract (N definition, sentinel rule, algorithm, verbatim persistence, format_text validation, empty fragment, whole-range equivalence).
4. raw read invariant (shared body-extraction helper; frontmatter.loads content; read-only, no lock).
5. set_status contract (8 adapters; guard; per-domain vocab table — req/gol 7-value; uc 5-value (draft/proposed/accepted/deprecated/superseded); rsk (open/mitigating/… — implementer to read the actual set); prb/qa/tsk (draft/active/…); ADR 6 + "superseded by" pattern; note ADR's superseded_by composition delegates to mutations.set_status).
6. Import-order risk + smoke test (general is imported 2nd at server.py:211; new modules pull domain packages earlier; `from ...server import mcp` partial-init pattern is already proven; submodule-import form for \_packaged_data is safe).
7. Name/parameter notes: `type` parameter (ruff E/F/W clean — no builtin-shadow rule; matches the frontmatter field vocabulary); both tools registered in general/tools/__init__.py.
8. Docs discipline: server.py docstring updated per phase; MCP.md/docs/api regenerated per phase gate (zero drift at each commit); the ADR in Phase 1 is created via the MCP tool.
9. Expected final registration counts: 71/25/19 (from 84/25/19: −15 +2).

Related ADRs:

- ddfb1109: id-based reads as tools (basis for raw over /{id} resources)
- ece4554b: domain-first layout (general/ home for the cross-cutting tools)
- 3bf0326f: mcp singleton in its own module
- 71fd95d7: ADR update_section (the contract `update` does not extend to ADR)
- 898bfcd0: ADRs only authored via MCP structured tools
- 33c5ab08: filesystem is sole source of truth
- ec9f5262? (list paging — not directly relevant; skip)
- New ADR created in Phase 1 (id TBD — reference by title).

Decisions Made (seed, dated 2026-08-26):

- Explicit `type` parameter over uuid-only resolution — rationale (no write-path scan; per-domain v4 not guaranteed-unique; client already knows the domain; ADR out of scope for update anyway).
- ADR excluded from `update` (section-level MADR contract), included in `set_status` with superseded_by special case.
- Full removal, no deprecated wrappers (0.x, tool list is the contract).
- Prompts kept per-domain (domain-tuned guidance), text rewritten.
- Short ADR over README-only decision log (a repo-wide convention that future domains follow).
- begin/end line ranges with N+1 EOF sentinel + splice-then-validate-whole (user request; safety + size win).
- get\_<d>(raw=True) over reintroducing /{id} resources (ADR ddfb1109's empirical reliability finding).

Progress:

- Current Status: **As of 2026-08-26**: planned — README drafted, all 7 phases not started.
- Blockers: none.
- Recent Updates: initial entry (planning complete, awaiting /implement-feature).
- Decisions Made: as above.
- Related PRs / Commits: none yet.

Now — one more point about frontmatter `status`: planning (per the template) — flip to in-progress when Phase 1 starts (the orchestrator/instrumenter does it in Phase 1's Progress update… actually the phase-end task says "update Current Status + Recent Updates"; the frontmatter status flip planning→in-progress should happen on Phase 1 start. Let me add to Task 1.1 or 1.3: "set the README frontmatter status: planning → in-progress". I'll put it in Task 1.3's gate task (or 1.1). Let me make it part of Task 1.3: "…update this README's Progress section (Recent Updates entry, Current Status, frontmatter status → in-progress)".

Also, the template's task-line format: `- [ ] Task 1.1: [description] — depends on: none — status: not-started`.

Length: this README will be long (feat-18's was ~900+ lines). That's the convention. I need to write it in full — the orchestrator and implementer rely on it being self-contained.

One more check: `tsk`'s prompt file names: `tsk/prompts/update_task.py` (not update_tsk), data file `tsk_update_instructions.md`. And rsk's prompt: `rsk/prompts/update_risk.py`. Phase 5's test files: `tests/tsk/prompts/test_update_task.py`, `tests/rsk/prompts/test_update_risk.py`. I listed 7 domain prompt tests — the correct set: tests/req/prompts/test_update_req.py, tests/uc/prompts/… wait, does UC have prompts? Per AGENTS.md, UC does not have a prompts subpackage ("uc only registers tools and resources — no prompts subpackage yet"). Confirming: my earlier file listing showed no uc/prompts. And the find for prompt test files showed: gol, prb, qa, req, rsk, tsk update prompt tests + adr's — that's 6 domain + 4 ADR = 10, not 11! Recounting the prompt tests found by the earlier `find tests -name "*update*"`:

- tests/adr/prompts/test_update_adr.py
- tests/adr/prompts/test_update_adr_test.py
- tests/gol/prompts/test_update_gol.py
- tests/prb/prompts/test_update_prb.py
- tests/qa/prompts/test_update_qa.py
- tests/req/prompts/test_update_req.py
- tests/rsk/prompts/test_update_risk.py
- tests/tsk/prompts/test_update_task.py
  = 8 (2 adr + 6 domain). UC has no update prompt (no prompts package at all).

So Phase 5:

- Data files: 6 domain update instructions (req, uc? — wait, does UC have an update instructions data file? My earlier glob showed uc/data/ has only uc_template.md and uc_example.md — no uc_create/uc_update instructions! UC has no prompts so no instruction files. Confirmed: uc/data has only uc_template.md and uc_example.md.)
  So domain update instructions: req_update_instructions.md, tsk_update_instructions.md, qa_update_instructions.md, rsk_update_instructions.md, prb_update_instructions.md, gol_update_instructions.md = 6 files. Plus qa_refine_instructions.md = 7. Plus 4 ADR files = 11 data files total (not 12).
- Prompt Python modules to fix: 6 domain `prompts/update_<d>.py` (req, tsk, qa, rsk (update_risk.py), prb, gol) — uc has none. Plus 4 ADR prompt modules.
- Prompt test files: 6 domain + 4 ADR = 10 files.

Recount for ACC-006: "11 instruction data files + prompt docstrings + 10 prompt test files".

Hmm wait — but UC's update: UC has no prompt, but UC does have update_uc tool + tests (tests/uc/tools/test_update_uc.py exists). Fine.

And the raw parameter: 7 get tools including uc's get_uc (UC has a tools package). Yes, 7.

Also the `qa_refine_instructions.md` — part of the 11 (6 update + 1 refine + 4 ADR = 11).

Phase 5 task 5.1 wording: "11 files expected: 6 × `<d>_update_instructions.md` (req, tsk, qa, rsk, prb, gol — uc has no prompts), qa_refine_instructions.md, 4 × ADR instruction files".

Now — one more point about `update` tool's MCP schema: the mcp SDK builds the input schema from the signature. `begin: int | None = None` → optional integer. Literal → enum. Good.

Also — a note about the splice helper name: I said `general/tools/_splice.py`. The functions: `body_text(path: Path) -> str`, `splice_body(current_body: str, begin: int, end: int, content: str) -> str` (raise ValueError on misuse), maybe `count_body_lines(text) -> int`. Keep it simple: 2 public-in-module functions.

Wait, actually there's a subtlety about `body_text`: python-frontmatter's `Post.content` — for a file `---\nyaml\n---\nbody\n`, content = "body\\n" (with trailing newline? python-frontmatter splits on the closing `---` line; content includes everything after, typically preserving the trailing newline). The 7 set_status tools already use exactly this and re-persist verbatim, so it's the established mechanism. For raw=True return: return the content as-is (the text the client counts). N = len(content.splitlines()) — with a trailing "\\n", splitlines excludes the empty final. Consistent.

Splice: lines = content.splitlines(); delete [begin-1:end] when end ≤ N; insert the fragment lines at begin-1; fragment lines = content_arg.splitlines() (splitlines handles the trailing newline cleanly — no empty final). result = "\\n".join(lines) + "\\n". If the body is empty (N=0): only begin=end=1=N+1 append allowed. Edge case documented.

OK. Also the whole-range equivalence (begin=1, end=N): splice result = fragment verbatim (with trailing-newline normalization) — equivalent to whole-body mode up to trailing whitespace (python-frontmatter strips it anyway per \_write docstring).

Now let me write the README. It'll be big. Let me structure carefully.

Also: should I `git add` the new file? The phase-implementer convention: "new files must be git add-visible for pylint/CI, but do not commit". For Step 0, I'm creating the README — I won't commit (commits are per-phase, owned by the orchestrator). Should I git add? The orchestrator commits per phase with user confirmation. The README is… part of Phase 1's commit? In feat-18, the README existed before the phases (created in the planning session, probably committed in the planning commit). I'm not committing anything (policy: don't commit unless explicitly asked; the per-phase commit happens under the orchestrator with user confirmation). I'll just create the file and leave it staged/unstaged — I won't even git add (leave it to the user/orchestrator flow). Hmm — but pylint only sees git-tracked files; the README is markdown, not relevant. Fine, I'll leave it untracked.

Let me also double-check `rsk`'s full status set and prb/qa/tsk's, so I can write the exact vocab in the Design Notes (better for the implementer than "read the actual set" — though the implementer should read the code as source of truth anyway; I'll list what I know and note "the code is authoritative"). Let me grep the full sets.

Approved — executing Step 0. First, let me pull the exact per-domain status vocabularies for the Design Notes (so the implementer doesn't have to guess):

**Tool: bash**

**Input:**

```json
{
  "command": "for f in req uc tsk qa prb gol rsk; do echo \"== $f ==\"; grep -A12 \"_ALLOWED_STATUSES = frozenset\" src/biz/dfch/specmgr/$f/models/*/frontmatter.py 2>/dev/null | grep -E '\"' | head -12; done"
}
```

**Output:**

```
== req ==
        "draft",
        "proposed",
        "accepted",
        "superseded",
        "deprecated",
        "rejected",
        "implemented",
== uc ==
_ALLOWED_STATUSES = frozenset({"draft", "proposed", "accepted", "deprecated", "superseded"})
    """Use-case frontmatter: `MarkdownFrontmatter` narrowed for the `uc` document type.
        Fixed discriminator, always `"uc"`. Narrows the base's mandatory,
        default-less `str` field to a `Literal["uc"] = "uc"`, so a document
== tsk ==
        "draft",
        "active",
        "done",
        "cancelled",
    """TaskList frontmatter: `MarkdownFrontmatter` narrowed for the ``tsk`` document type.
== qa ==
        "draft",
        "active",
        "done",
        "cancelled",
    """Question and Answer (QA) frontmatter: `MarkdownFrontmatter` narrowed for the ``qa`` document type.
== prb ==
        "draft",
        "active",
        "resolved",
        "cancelled",
    """Problem Statement (PRB) frontmatter: `MarkdownFrontmatter` narrowed for the ``prb`` document type.
== gol ==
        "draft",
        "proposed",
        "accepted",
        "superseded",
        "deprecated",
        "rejected",
        "implemented",
== rsk ==
        "open",
        "mitigating",
        "accepted",
        "occurred",
        "closed",
        "dropped",

```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 51.3s)

_Thinking:_

Now I have the complete status vocabulary:

- req: draft, proposed, accepted, superseded, deprecated, rejected, implemented (7)
- gol: same 7 as req
- uc: draft, proposed, accepted, deprecated, superseded (5)
- tsk: draft, active, done, cancelled (4)
- qa: draft, active, done, cancelled (4)
- prb: draft, active, resolved, cancelled (4)
- rsk: open, mitigating, accepted, occurred, closed, dropped (6)
- adr: draft, proposed, rejected, accepted, deprecated, superseded + "superseded by X" (6 + pattern)

Next, I'll create the feature directory and README. Let's create the complete README.

Directory: `.specmgr/feat/feat-0-consolidate-mutation-tools/`

Alright, let's write out the full text. I'll follow the template structure and the level of detail of feat-18. Front matter in alphabetical order (same as feat-18): created, id, status, updated, version.

Vocabularies captured. Now creating the feature folder and the full plan README:

**Tool: bash**

**Input:**

```json
{
  "command": "mkdir -p .specmgr/feat/feat-0-consolidate-mutation-tools && ls .specmgr/feat/ | tail -3"
}
```

**Output:**

```
feat-7-various-improvements
feat-8-coverage-badge
feat-9-doc-in-specmgr

```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 531.1s)

_Thinking:_

Directory has been created. Next, I'll write the README. This is the important deliverable, so it must be complete and self-contained for the orchestrator/implementer.

**Tool: write**

**Input:**

````json
{
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-0-consolidate-mutation-tools/README.md",
  "content": "---\ncreated: 2026-08-26\nid: feat-0-consolidate-mutation-tools\nstatus: planning\nupdated: 2026-08-26\nversion: 1.0.0\n---\n\n# Feature: Consolidate update and set_status tools into generic type-dispatched tools\n\n## Plan\n\n### Overview\n\nReplace the 15 near-duplicate per-domain mutation MCP tools with two generic,\ncross-cutting tools that live in `general/tools/`: `update(id, type, content,\nbegin, end)` for whole-body (and now line-range) document replacement across\nthe seven whole-body domains (`req`, `uc`, `tsk`, `qa`, `prb`, `gol`, `rsk`),\nand `set_status(id, type, status, superseded_by)` for status changes across\nall eight domains including `adr`. The per-domain tools\n(`update_req`/`update_uc`/`update_tsk`/`update_qa`/`update_prb`/`update_gol`/\n`update_rsk`, `set_status_req`/`set_status_uc`/`set_status_tsk`/`set_status_qa`/\n`set_status_prb`/`set_status_gol`/`set_status_rsk`, and ADR's own `set_status`)\nare deleted outright (breaking; the package is 0.x and the MCP tool list is the\nonly contract). The generic `update` gains optional 1-based, inclusive\n`begin`/`end` body-line parameters so a client can replace a line range\nwithout re-sending the whole body — spliced into the current on-disk body and\nvalidated as a *whole* document before anything is written (the\nfilesystem-is-source-of-truth and validate-before-write invariants are\nuntouched). To make line targeting reliable, the seven `get_<d>` tools gain an\noptional `raw: bool = False` parameter returning the frontmatter-stripped body\ntext verbatim — the exact text `begin`/`end` index into (tool-first per ADR\nddfb1109; re-introducing `specmgr://<d>/{id}` resources was considered and\nrejected). ADR keeps its section-level mutation surface\n(`update_frontmatter`/`update_section`/`option_*`) unchanged — ADR is\ndeliberately *excluded* from `update` because it has no whole-body replace by\ndesign (MADR contract), but is *included* in `set_status` with its\n`superseded_by`-composition special case. A short ADR records the new\nconventions so future domains (e.g. `ac`) add one dispatch entry instead of a\nnew tool. Expected end state: **71 tools / 25 resources / 19 prompts**\n(today 84/25/19: −15 +2).\n\n### Requirements\n\n- REQ-001: A generic `update(id, type, content)` MCP tool in\n  `general/tools/update.py` covering the seven whole-body domains\n  (`type: Literal[\"req\",\"uc\",\"tsk\",\"qa\",\"prb\",\"gol\",\"rsk\"]`), preserving each\n  domain's existing whole-body semantics 1:1: body-only `content` (no\n  frontmatter block) validated via the domain's own\n  `X.from_text(format_text(content))` two-channel contract\n  (`AssertionError` structural / `pydantic.ValidationError` field-level,\n  nothing written on failure); under the domain's own lock, `load_by_id`,\n  every frontmatter field preserved except `updated` (bumped to the current\n  microsecond timestamp); `status` never settable through `update`; the\n  caller's raw `content` persisted verbatim via the domain's `write_X_file`;\n  unknown id raises the domain's own `XNotFoundError`.\n- REQ-002: Optional `begin: int | None` / `end: int | None` parameters on\n  `update`. When both are absent, behavior is exactly REQ-001 (backward-\n  compatible default). When both are given, `content` is a replacement\n  *fragment* for the current body's 1-based, inclusive line range\n  `begin..end`, where `N` = number of lines of the current frontmatter-\n  stripped body and `N+1` is a virtual position past the last line\n  (`begin = end = N+1` → append at end of body; `end = N+1` → range extends\n  through end of body). Misuse (exactly one of the two given, `begin < 1`,\n  `begin > end`, `end > N+1`) raises `ValueError` with a clear message and\n  writes nothing. The spliced *result* is validated as a whole body (REQ-001's\n  validation contract) before writing; unchanged regions of the on-disk body\n  remain byte-identical. An empty `content` fragment deletes the range (legal\n  iff the result still validates). The YAML frontmatter is never addressable\n  (coordinates are body-relative by construction).\n- REQ-003: The seven `get_<d>` tools (`get_req`, `get_uc`, `get_tsk`,\n  `get_qa`, `get_prb`, `get_gol`, `get_rsk`) gain an optional\n  `raw: bool = False` parameter. `raw=False` (default) behaves exactly as\n  today (returns the parsed `XDocument`). `raw=True` returns the\n  frontmatter-stripped body text of the document verbatim as a plain string —\n  produced by the *same* body-extraction helper the REQ-002 splice uses, so\n  the text a client counts lines in is byte-for-byte the text the server\n  splices against. Unknown id raises the domain's `XNotFoundError` in both\n  modes. No `get_adr` change (ADR is not a `update` type).\n- REQ-004: A generic `set_status(id, type, status, superseded_by=None)` MCP\n  tool in `general/tools/set_status.py` covering all eight domains\n  (`type: Literal[\"req\",\"uc\",\"tsk\",\"qa\",\"prb\",\"gol\",\"rsk\",\"adr\"]`). For the\n  seven whole-body domains, semantics are preserved 1:1 from the deleted\n  `set_status_<d>` tools: under the domain lock, `load_by_id`, the raw body\n  re-read and re-persisted verbatim (body never touched), the frontmatter\n  reconstructed through the domain's own `XFrontmatter` constructor so each\n  domain's closed status vocabulary validates (invalid `status` →\n  `pydantic.ValidationError`, nothing written), `updated` bumped, unknown id →\n  domain `XNotFoundError`. For `type=\"adr\"`, semantics are preserved 1:1 from\n  the deleted ADR `set_status` tool: delegates to\n  `models.adr.v1.mutations.set_status(adr, status, superseded_by)` (which\n  composes `status` as `\"superseded by {superseded_by}\"` when\n  `superseded_by` is given), `write_adr` render round-trip, `adr_lock`,\n  `AdrNotFoundError`. `superseded_by` given with any `type` other than\n  `\"adr\"` raises `ValueError` and writes nothing.\n- REQ-005: The 15 superseded tools are removed from source and from MCP\n  registration: `update_req`, `update_uc`, `update_tsk`, `update_qa`,\n  `update_prb`, `update_gol`, `update_rsk`, `set_status_req`,\n  `set_status_uc`, `set_status_tsk`, `set_status_qa`, `set_status_prb`,\n  `set_status_gol`, `set_status_rsk`, and ADR `set_status`. No deprecated\n  wrappers are kept (user decision; 0.x breaking change, recorded in\n  `CHANGELOG.md`).\n- REQ-006: All prompt narration referencing the superseded tools is rewritten\n  to the generic tools with correct signatures: the six domain\n  `<d>_update_instructions.md` files (req, tsk, qa, rsk, prb, gol — `uc` has\n  no prompts sub-package), `qa/data/qa_refine_instructions.md`, and the four\n  ADR instruction files (`adr_create_instructions.md`,\n  `adr_create_test_instructions.md`, `adr_update_instructions.md`,\n  `adr_update_test_instructions.md` — their `set_status(id, …)` call sites\n  gain `type=\"adr\"`). The six domain update-instruction files additionally\n  teach the REQ-002 range-update flow. Prompt Python module docstrings that\n  name the superseded tools are corrected (6 domain `prompts/update_<d>.py`\n  modules + 4 ADR prompt modules whose surface mentions become inaccurate).\n  The 10 corresponding prompt test files (6 domain + 4 ADR) are updated to\n  match the rewritten narration.\n- REQ-007: Documentation and registration consistency: `server.py` module\n  docstring (the authoritative tool/resource/prompt list) updated in the same\n  phase that changes the surface it describes; `docs/MCP.md`, `docs/api/`,\n  `docs/adr/README.md` regenerated with zero drift at every phase gate;\n  `AGENTS.md` per-domain bullets and the `general/` bullet updated;\n  `CHANGELOG.md` `[Unreleased]` carries the breaking-change and\n  addition entries; a short ADR (Phase 1) records the conventions (explicit\n  `type` over uuid-only resolution; ADR excluded from `update` but included\n  in `set_status`; the REQ-002 range contract; the REQ-003 raw-read-over-\n  resource decision; \"future domains add one dispatch entry, not a new\n  tool\").\n\n### Acceptance Criteria\n\n- [ ] ACC-001: Verifies REQ-001 — for every one of the seven types, `update`\n      in whole-body mode (no `begin`/`end`) replaces the body, preserves\n      `id`/`type`/`status`/`created`/`version`, bumps `updated` (microsecond\n      timestamp), never sets `status`, propagates structural\n      `AssertionError` / field `pydantic.ValidationError` with the file left\n      byte-identical on disk, and raises the domain's own `XNotFoundError`\n      for an unknown id.\n- [ ] ACC-002: Verifies REQ-002 — for every one of the seven types: a\n      middle-range replace leaves all out-of-range body lines byte-identical\n      and inserts the fragment at the range; `begin = end = N+1` appends at\n      end of body; `end = N+1` replaces through end of body; empty `content`\n      deletes the range (verified with an optional-section deletion that\n      yields a still-valid document); `begin = 1`, `end = N` produces the same\n      file as whole-body mode with the identical text; each misuse case (one\n      parameter only, `begin < 1`, `begin > end`, `end > N+1`, range deleting\n      the H1, range producing an out-of-vocabulary field value) raises\n      (`ValueError` / `AssertionError` / `ValidationError`) with the file left\n      byte-identical on disk.\n- [ ] ACC-003: Verifies REQ-003 — for all seven domains,\n      `get_<d>(id, raw=True)` returns the frontmatter-stripped body text\n      byte-identical to the on-disk body (the text whose lines `begin`/`end`\n      address — proven by a test that reads `raw`, picks a line range, calls\n      `update` with that range, and confirms the splice landed exactly there);\n      `get_<d>(id)` (`raw=False`) returns the parsed document exactly as\n      before (regression); unknown id raises the domain `XNotFoundError` in\n      both modes.\n- [ ] ACC-004: Verifies REQ-004 — for all eight types, `set_status` changes\n      `status`, bumps `updated`, and leaves the body untouched (seven\n      domains: raw body byte-identical; ADR: re-render round-trip equal apart\n      from status/updated); each domain's closed vocabulary is enforced\n      (out-of-set value → `pydantic.ValidationError`, nothing written —\n      including domain-distinct sets: `uc` 5-value, `tsk`/`qa` 4-value,\n      `prb` 4-value, `rsk` 6-value); ADR `superseded_by` composes\n      `\"superseded by X\"`; `superseded_by` with a non-`adr` type raises\n      `ValueError`, nothing written; unknown id raises the domain\n      `XNotFoundError` / `AdrNotFoundError`.\n- [ ] ACC-005: Verifies REQ-005 — the 15 superseded tools are absent from\n      `src/` and from the live MCP registration; a grep over `src/` and\n      `tests/` finds no code references to the removed tool names (any\n      residual mention before Phase 5 is limited to the Phase-5-owned prompt\n      narration files, and zero afterwards); `vulture` is clean.\n- [ ] ACC-006: Verifies REQ-006 — all 11 instruction data files reference the\n      generic tools with the correct signatures (`update(id, type=\"<d>\",\n      content[,...])`, `set_status(id, type=..., status[, superseded_by])`);\n      the six domain update-instruction files teach the range-update flow\n      (`get_<d>(id, raw=True)` → identify the 1-based range → `update(...,\n      begin, end)`; whole-body for multi-section or uncertain changes); the\n      10 prompt test files pass against the rewritten narration.\n- [ ] ACC-007: Verifies REQ-007 — `specmgr docs`, `specmgr mcp-docs`,\n      `specmgr adr-toc`, and `specmgr schema` all report zero drift;\n      `docs/MCP.md` shows the two new general tools (with `type` rendered as\n      a 7- / 8-value enum) and none of the 15 removed tools; `server.py`'s\n      docstring lists exactly the post-feature surface; `AGENTS.md` and\n      `CHANGELOG.md` are updated per REQ-007.\n- [ ] ACC-008: Verifies REQ-001/002/004/005 — the Phase-1 ADR exists in\n      `docs/adr/` with status `accepted` and is listed in\n      `docs/adr/README.md`; a live, un-mocked end-to-end run in a temporary\n      `SPECMGR_DOCS_DIR` passes for `req`, `rsk`, and `uc`:\n      `create_<d>` → `get_<d>(id, raw=True)` → `update(id, type, content,\n      begin, end)` (one middle-range replace, one `N+1` append) → `get_<d>`\n      (content verified) → `set_status(id, type, status)` (domain-valid\n      value) → `get_<d>` (status verified); for ADR: `create_adr` →\n      `set_status(id, type=\"adr\", status=\"superseded\", superseded_by=…)` →\n      status reads `\"superseded by …\"`; `asyncio.run(mcp.list_tools()/\n      list_resources()/list_prompts())` on the real `server.mcp` instance\n      reports **71 tools / 25 resources / 19 prompts**; a fresh subprocess\n      import of `biz.dfch.specmgr.server` succeeds.\n\n### Scope\n\n**Included in this feature:**\n\n- `general/tools/update.py`, `general/tools/set_status.py`, and the shared\n  body-text/splice helpers (private module under `general/tools/`), plus\n  their registration in `general/tools/__init__.py`.\n- The `raw` parameter on the seven `get_<d>` tools.\n- Deletion of the 15 superseded tool modules, their test files, and all\n  code/docstring references outside Phase-5-owned narration.\n- The narration rewrite (11 instruction data files, prompt module\n  docstrings, 10 prompt test files).\n- The Phase-1 ADR, `AGENTS.md`, `CHANGELOG.md`, and all generated docs.\n\n**Explicitly out of scope:**\n\n- Any change to ADR's section-level mutation tools (`update_frontmatter`,\n  `update_section`, `option_*`) or to ADR's `specmgr://adr/{id}` resource —\n  ADR has no whole-body replace by design and is therefore not a `update`\n  type; its `set_status` behavior moves to the generic tool unchanged.\n- Re-introducing `specmgr://<d>/{id}` resources for the seven domains —\n  rejected in the planning session on ADR ddfb1109's empirical reliability\n  finding (agents invoke tools more reliably than parameterized resources);\n  `get_<d>(raw=True)` serves the same need (recorded in the Phase-1 ADR).\n- Consolidation of `create_*`, `get_*` (beyond the `raw` parameter),\n  `list_*`, `validate_*`, `parse_*`, or the `delete_*` stubs.\n- Any schema/model change: the per-domain status vocabularies, body schemas,\n  and `specmgr schema` outputs are untouched.\n- A version bump of `pyproject.toml` (release-time concern per `AGENTS.md`;\n  the breaking change lands in `[Unreleased]`).\n- The `ac` domain (does not exist yet) — but its *convention* is fixed by the\n  ADR: it will add one dispatch entry to the two generic tools, not new\n  tools.\n- The pre-existing, already-documented AGENTS.md staleness items (e.g. the\n  historical \"REQ, UC, and TSK were built after that refactor\" enumeration)\n  — fixing unrelated stale text is not part of this feature.\n\n### Dependencies\n\n- Depends on: ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614 (id-based reads are\n  tool-first — the basis for `raw` on `get_<d>` instead of `/{id}`\n  resources); ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first\n  hierarchy — the generic tools live in the cross-cutting `general/`\n  package, reusing each domain's private helpers); ADR\n  3bf0326f-065a-424c-a2b9-87e5d5bcfa99 (the `mcp` singleton lives in\n  `server.py` — import-order consideration, see Design Notes); ADR\n  71fd95d7-07f2-466f-81aa-d29b7e3ef34c (ADR's `update_section` contract —\n  what `update` deliberately does *not* extend to ADR); ADR\n  898bfcd0-85f9-462f-93a8-747bda4166c8 (ADRs are authored/edited only\n  through the MCP structured tools — Phase 1 must use\n  `specmgr_create_adr`); ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3\n  (filesystem is the sole source of truth — the splice re-reads the on-disk\n  body and the validate-before-write invariant is preserved); the existing\n  `general/tools/_doc_paths.py`/`_packaged_data.py` infrastructure and each\n  domain's `_paths`/`_io`/`_write`/`_lock` private helpers (reused as-is,\n  not modified).\n- Blocks: none. Future domain work (e.g. `ac`) must follow the ADR's\n  dispatch-entry convention.\n\n### Design Notes\n\n**Dispatch architecture.** Each of the two generic tools is a thin MCP\nwrapper around a dispatch table `dict[str, Callable]` mapping the `type`\nvalue to a private adapter function (`_update_<d>` / `_set_status_<d>`).\nEach adapter is a **verbatim port** of the corresponding deleted tool's\nfunction body (same lock, same `load_by_id`, same frontmatter carry-over /\n`updated` bump, same `write_X_file`, same domain `XNotFoundError`) — for\n`update`, plus the REQ-002 range branch; for `set_status`, the ADR adapter\nports `adr/tools/set_status.py` including its delegation to\n`models.adr.v1.mutations.set_status`. Domain private helpers (`_paths`,\n`_io`, `_write`, `_lock`) and domain models are **not modified** — `create_*`/\n`get_*`/`validate_*`/`list_*` keep using them exactly as today, and the new\nadapters import them the same way the old tools did. The adapters and table\nlive in `general/tools/` because the tools are cross-cutting (the\n`general/` package is the documented home for non-domain-specific tools, per\n`AGENTS.md`); no new shared *code* is added to the domain packages.\n\n**`update` signature and return type.**\n\n```python\n@mcp.tool(\n    name=\"update\",\n    title=\"Update document\",\n    description=(...),  # whole-body or line-range replace; type = domain;\n)                       # begin/end optional 1-based inclusive body-line range\ndef update(\n    id: str,\n    type: Literal[\"req\", \"uc\", \"tsk\", \"qa\", \"prb\", \"gol\", \"rsk\"],\n    content: str,\n    begin: int | None = None,\n    end: int | None = None,\n) -> ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument | GolDocument | RskDocument:\n```\n\nThe parameter is named `type` (matches the frontmatter field vocabulary the\nclient already knows; ruff's enabled rule set E/F/W has no builtin-shadowing\nrule). The 7-way union return type is annotation-only — the MCP input schema\nis built from the parameters, and the SDK serializes whichever concrete\ndocument is returned. The `type` value must render as a 7-entry JSON-schema\n`enum` in `docs/MCP.md` (verify in the Phase 2 gate).\n\n**Range contract (REQ-002), precisely.** Let `N` be the number of lines of\nthe current frontmatter-stripped body (`len(body_text.splitlines())`).\nCoordinates are 1-based and inclusive. `N+1` is a virtual position past the\nlast line:\n\n- `begin = end = k` (1 ≤ k ≤ N) → replace line `k` only.\n- `begin = k`, `end = m` (k ≤ m ≤ N) → replace lines `k..m`.\n- `end = N+1` → the range extends through the last line (`k..N`).\n- `begin = end = N+1` → the range is empty at end-of-body: pure append.\n- `begin = 1`, `end = N` → whole-body replace, file-identical to whole-body\n  mode with the same text (test this equivalence).\n- Empty `content` → the range is deleted (legal iff the result validates).\n\nMisuse → `ValueError` (client-controlled input, **not** `assert` — per\n`.specmgr/conventions.md` Rule 3): exactly one of `begin`/`end` given;\n`begin < 1`; `begin > end`; `end > N + 1`. The error message names the\noffending value(s) and the allowed range. Splice algorithm: take the on-disk\nbody lines, drop lines `begin..min(end, N)`, insert `content.splitlines()` at\nposition `begin - 1`, rejoin with `\"\\n\"` plus a single trailing `\"\\n\"`. The\n**result** is validated exactly like whole-body mode (`X.from_text(\nformat_text(spliced))`) and the spliced text (not the fragment) is persisted\nverbatim via the domain `write_X_file` — so out-of-range regions are\nbyte-identical to disk and no renderer ever touches them. Frontmatter\naddressing is impossible by construction: the body text is extracted with\nthe frontmatter block removed, and coordinates are defined relative to that\ntext only.\n\n**Shared body extraction + `raw` invariant (REQ-003).** One private helper\n(live in a new `general/tools/_splice.py` alongside the splice function, no\n`mcp` dependency — plain file I/O, mirroring `_doc_paths.py`'s placement)\nreturns the frontmatter-stripped body text of a file using the established\n`frontmatter.loads(path.read_text(encoding=\"utf-8\")).content` mechanism (the\nsame one all seven `set_status_<d>` tools use today). Both the REQ-002 splice\nand each `get_<d>(raw=True)` call go through this one helper, which *is* the\n\"what the client counts is what the server splices\" invariant of ACC-003.\n`get_<d>` with `raw=True` stays read-only: no lock, no directory creation —\nmatching every existing `get_<d>`.\n\n**`set_status` signature and the `superseded_by` guard (REQ-004).**\n\n```python\n@mcp.tool(\n    name=\"set_status\",\n    title=\"Set document status\",\n    description=(...),  # type = domain (8 values, incl. adr);\n)                       # superseded_by: adr only\ndef set_status(\n    id: str,\n    type: Literal[\"req\", \"uc\", \"tsk\", \"qa\", \"prb\", \"gol\", \"rsk\", \"adr\"],\n    status: str,\n    superseded_by: str | None = None,\n) -> ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument | GolDocument | RskDocument | Adr:\n```\n\nPer-domain closed status vocabularies (authoritative source: each domain's\n`_ALLOWED_STATUSES` in `models/<v>/frontmatter.py` — re-read them when\nimplementing; the table below reflects 2026-08-26): `req` and `gol`:\n`draft`/`proposed`/`accepted`/`superseded`/`deprecated`/`rejected`/\n`implemented` (7); `uc`: `draft`/`proposed`/`accepted`/`deprecated`/\n`superseded` (5); `tsk` and `qa`: `draft`/`active`/`done`/`cancelled` (4);\n`prb`: `draft`/`active`/`resolved`/`cancelled` (4); `rsk`: `open`/\n`mitigating`/`accepted`/`occurred`/`closed`/`dropped` (6); `adr`: 6 values\n(`draft`/`proposed`/`rejected`/`accepted`/`deprecated`/`superseded`) plus the\n`\"superseded by X\"` pattern. The guard `superseded_by is not None and type !=\n\"adr\"` → `ValueError` runs **before** any file access.\n\n**Import-order consideration.** `server.py` imports the domain packages in\none bottom-of-file line, with `general` second\n(`from . import adr, general, gol, prb, qa, req, rsk, tsk, uc`). Once\n`general/tools/__init__.py` registers the new tools, importing `general`\npulls in **all** seven domain `tools` (and `prompts`) packages earlier than\ntoday. This is safe by construction: every domain tool module already does\n`from ...server import mcp` while `server.py` is still executing its import\nline (the `mcp` name is bound at `server.py:197`, before the import line at\n`server.py:211`), and every `general.tools._packaged_data` import in domain\nprompts/resources uses the submodule form (`from ...general.tools._packaged_\ndata import read_packaged_text`), which is safe mid-initialization. The\nPhase 2 gate's fresh-subprocess import smoke test (ACC-008) proves it rather\nthan assuming it.\n\n**Docs discipline.** `server.py`'s module docstring is updated *inside* each\nphase that changes the surface it describes (Phase 2 adds both tools' lines\nas they are added; Phase 3 removes the `update_<d>` lines; Phase 4 removes\nthe `set_status_<d>` + ADR `set_status` lines). `docs/MCP.md` and `docs/api/`\nare regenerated in every phase gate and must be drift-free\n(`git diff --exit-code -- docs/`) at every phase commit — the pre-commit\nhooks enforce this for any commit touching `src/`.\n\n**Name-collision constraint.** ADR's existing tool is already named\n`set_status`. Registering the generic `set_status` while `adr/tools/\nset_status.py` still exists would double-register the name, which is why\nPhase 4 adds the generic tool and deletes all eight old status tools in one\nphase. (No such constraint exists for `update` — Phase 2 is purely additive,\nPhase 3 deletes the seven `update_<d>` tools.)\n\n**Phase-end quality gate (every phase).** Unless a phase task says otherwise:\n`uv run --frozen ruff format --check`, `uv run --frozen ruff check`,\n`uv run --frozen vulture src/ whitelist.py --min-confidence 60`, `uv run\n--frozen python -m unittest discover -v -s tests -t . -p \"test_*.py\"`, plus\nthe `specmgr docs` / `specmgr mcp-docs` / `specmgr adr-toc` / `specmgr schema`\nregenerations the phase touches, then `git diff --exit-code -- docs/`. Fix\nfailures and re-run until green — a phase is not done with a red gate. Then\nupdate this README: a dated entry in the **Recent Updates** section, Current\nStatus, and the phase's task lines flipped to done in place.\n\n### Related ADRs\n\n- ddfb1109-422d-4507-8dbc-dc5e4bec9614: Expose id-based document reads as a\n  tool (`get_<d>`), not a resource — the basis for `get_<d>(raw=True)`\n  instead of re-introducing `specmgr://<d>/{id}` resources\n- ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by document-\n  type domain — the generic tools live in the cross-cutting `general/`\n  package, reusing domain-private helpers\n- 3bf0326f-065a-424c-a2b9-87e5d5bcfa99: Extract the `mcp` singleton into its\n  own module — the import-order consideration in Design Notes\n- 71fd95d7-07f2-466f-81aa-d29b7e3ef34c: Generic `update_section` (ADR\n  domain) — the section-level contract that `update` deliberately does not\n  extend to ADR\n- 898bfcd0-85f9-462f-93a8-747bda4166c8: Author and edit ADRs only through MCP\n  structured tools — Phase 1 must use `specmgr_create_adr`, never a\n  hand-written file\n- 33c5ab08-ff58-4c73-8c32-23abaf3838e3: Filesystem is the sole source of\n  truth — the splice re-reads the on-disk body; validate-before-write\n- (Phase 1 creates the feature's own short ADR; its id is recorded in\n  Decisions Made once created)\n\n### Task List\n\nSingle, canonical breakdown of work phases and tasks. Status lives on the\ntask itself. Each phase ends with a mandatory phase-end quality-gate task\n(full gate per Design Notes + this README's Progress update), and the\nphase-orchestrator commits each accepted phase as one Conventional Commit.\n\n#### Phase 1: ADR\n\n- [ ] Task 1.1: Create the feature's ADR with the `specmgr_create_adr` MCP\n  tool (never hand-write the file — ADR 898bfcd0), status `accepted`,\n  title \"Consolidate whole-body update and status-change tools into generic\n  type-dispatched tools\": Context (15 near-duplicate mutation tools; LLM\n  clients see 15 entries for 2 conceptual operations; each new domain would\n  add more); Decision Drivers (simpler tool surface; no all-directories\n  write-path scan and no per-domain v4-UUID-collision ambiguity — uuid-only\n  resolution was rejected; the client already knows the domain; preserve the\n  filesystem-source-of-truth and validate-before-write invariants); Considered\n  Options (1: generic tools with explicit `type` — chosen; 2: uuid-only id\n  resolution scanning all domain directories; 3: keep per-domain tools);\n  Decision Outcome (Option 1) with Consequences (breaking: 14 per-domain\n  tools removed and ADR `set_status`'s signature gains a required `type`;\n  ADR is excluded from `update` — its section-level MADR contract has no\n  whole-body replace — but included in `set_status` with the `superseded_by`\n  special case; the `update` line-range contract: 1-based inclusive\n  `begin`/`end`, `N+1` EOF sentinel, splice-then-validate-whole, frontmatter\n  never addressable; `get_<d>(raw=True)` as the line-number source — tool-\n  first per ADR ddfb1109, re-introducing `specmgr://<d>/{id}` resources was\n  considered and rejected; future domains add one dispatch entry per generic\n  tool, not new tools) — depends on: none — status: not-started\n- [ ] Task 1.2: Validate the new ADR with `specmgr_validate_adr`; run `uv run\n  --frozen specmgr adr-toc` and confirm the ADR appears in\n  `docs/adr/README.md` — depends on: Task 1.1 — status: not-started\n- [ ] Task 1.3: Phase-end quality gate — full gate (ruff format --check,\n  ruff check, vulture, full unittest suite; no `src/` changes are expected,\n  so `docs/` drift checks cover `specmgr adr-toc` output only); set this\n  README's frontmatter `status: planning` → `status: in-progress`; add a\n  dated entry to the Recent Updates section, update Current Status, flip the\n  phase's task lines to done in place; record the new ADR's id — depends on:\n  Task 1.2 — status: not-started\n\n#### Phase 2: Generic `update` tool + `raw` read parameter\n\n- [ ] Task 2.1: Create `general/tools/_splice.py` (no `mcp` dependency, plain\n  file I/O + text manipulation, module docstring explaining the raw/splice\n  invariant): `body_text(path: Path) -> str` (frontmatter-stripped body text\n  via the established `frontmatter.loads(...).content` mechanism) and\n  `splice_body(current_body: str, begin: int, end: int, content: str) -> str`\n  (implements the Design-Notes range contract exactly: `N` = `len(\n  current_body.splitlines())`; `ValueError` with a clear message for exactly-\n  one-of-`begin`/`end` handled by the caller, `begin < 1`, `begin > end`,\n  `end > N + 1`; drop lines `begin..min(end, N)`; insert\n  `content.splitlines()` at `begin - 1`; rejoin `\"\\n\"` + single trailing\n  `\"\\n\"`; empty `content` = deletion) — depends on: none — status: not-started\n- [ ] Task 2.2: Create `general/tools/update.py`: seven private adapter\n  functions `_update_<d>(id_, content, begin, end)` — verbatim ports of the\n  current `update_<d>` function bodies (same `X_lock`, `load_by_id`,\n  frontmatter carry-over + microsecond `updated` bump, `write_X_file`,\n  domain `XNotFoundError`) with the range branch added (no `begin`/`end` →\n  today's behavior: validate `X.from_text(format_text(content))`, persist\n  `content` verbatim; both given → `body_text` + `splice_body`, validate the\n  *result* via `X.from_text(format_text(spliced))`, persist the *spliced*\n  text verbatim; the both-or-neither `ValueError` guard runs before any file\n  access); a dispatch table; and `@mcp.tool(name=\"update\", ...)`\n  `def update(id: str, type: Literal[\"req\",\"uc\",\"tsk\",\"qa\",\"prb\",\"gol\",\"rsk\"],\n  content: str, begin: int | None = None, end: int | None = None) ->\n  ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument |\n  GolDocument | RskDocument` with a full numpy-style docstring (including the\n  range contract and the error types) — depends on: Task 2.1 — status:\n  not-started\n- [ ] Task 2.3: Register `update` in `general/tools/__init__.py` (import,\n  `__all__`, module docstring) — depends on: Task 2.2 — status: not-started\n- [ ] Task 2.4: Add the `raw: bool = False` parameter to the seven `get_<d>`\n  tools (`req/tools/get_req.py`, `uc/tools/get_uc.py`, `tsk/tools/get_tsk.py`,\n  `qa/tools/get_qa.py`, `prb/tools/get_prb.py`, `gol/tools/get_gol.py`,\n  `rsk/tools/get_rsk.py`): signature `get_<d>(id: str, raw: bool = False) ->\n  XDocument | str`; `raw=True` resolves the id as today (no lock — read-only)\n  and returns `body_text(path)` (the same helper the splice uses, per the\n  Design-Notes invariant); `raw=False` returns the parsed document exactly as\n  today; update each tool's `@mcp.tool` description and docstring Returns\n  section — depends on: Task 2.1 — status: not-started\n- [ ] Task 2.5: Update `server.py`'s module docstring: add `update` to the\n  General-tools lines (one line describing whole-body *and* line-range\n  replace, the 7-value `type`, optional `begin`/`end`); note the `raw`\n  parameter where the seven `get_<d>` tools are enumerated — depends on:\n  Task 2.2, Task 2.4 — status: not-started\n- [ ] Task 2.6: `tests/general/tools/test_update.py` — parameterized over all\n  seven types (seed a document per type, e.g. via the domain `create_<d>`\n  tool in a temp `SPECMGR_DOCS_DIR`, mirroring the fixture strategy of the\n  deleted `tests/<d>/tools/test_update_<d>.py` files still on disk at this\n  phase): whole-body mode (ACC-001 cases: body replaced; id/type/status/\n  created/version preserved; `updated` bumped; status not settable;\n  structural `AssertionError` and field `ValidationError` each leave the\n  file byte-identical; unknown id → domain `XNotFoundError`); range mode\n  (ACC-002 cases: middle-range replace with out-of-range lines byte-identical;\n  `N+1` append; `end=N+1` replace-through-EOF; empty-fragment deletion of an\n  optional section yielding a valid document; `begin=1`/`end=N` ≡ whole-body;\n  every `ValueError` misuse case; range deleting the H1 → `AssertionError`,\n  file untouched; range producing an out-of-vocabulary field value →\n  `ValidationError`, file untouched) — depends on: Task 2.2 — status:\n  not-started\n- [ ] Task 2.7: Extend each domain's existing `tests/<d>/tools/test_get_<d>.py`\n  (seven files) with `raw` coverage (ACC-003 cases): `raw=True` returns the\n  body text byte-identical to the on-disk frontmatter-stripped body; the\n  coordinate invariant (read `raw`, pick a real line range, `update` with it,\n  assert the splice landed exactly there); `raw=False` regression (parsed\n  document as before); unknown id → `XNotFoundError` in both modes — depends\n  on: Task 2.4, Task 2.2 — status: not-started\n- [ ] Task 2.8: Registration smoke test: a unittest asserting\n  `asyncio.run(mcp.list_tools())` contains `update` with `type` rendered as a\n  7-value `enum` and optional integer `begin`/`end` in the input schema, plus\n  a fresh-subprocess `uv run --frozen python -c \"import biz.dfch.specmgr.\n  server\"` check run inside the phase gate (import-order proof, Design Notes)\n  — depends on: Task 2.3 — status: not-started\n- [ ] Task 2.9: Phase-end quality gate — full gate including Tasks 2.6–2.8's\n  new tests; `uv run --frozen specmgr mcp-docs` and `uv run --frozen specmgr\n  docs` regeneration, then `git diff --exit-code -- docs/` zero drift;\n  confirm `docs/MCP.md` shows the `update` entry (enum) and the `raw` note on\n  the `get_<d>` entries; add a dated entry to the Recent Updates section,\n  update Current Status, flip the phase's task lines to done in place —\n  depends on: Tasks 2.3, 2.5, 2.8 — status: not-started\n\n#### Phase 3: Retire the per-domain `update_*` tools\n\n- [ ] Task 3.1: Delete the seven tool modules: `req/tools/update_req.py`,\n  `uc/tools/update_uc.py`, `tsk/tools/update_tsk.py`, `qa/tools/update_qa.py`,\n  `prb/tools/update_prb.py`, `gol/tools/update_gol.py`,\n  `rsk/tools/update_rsk.py` — depends on: Phase 2 complete — status: not-\n  started\n- [ ] Task 3.2: Delete the seven test files: `tests/req/tools/\n  test_update_req.py`, `tests/uc/tools/test_update_uc.py`, `tests/tsk/tools/\n  test_update_tsk.py`, `tests/qa/tools/test_update_qa.py`, `tests/prb/tools/\n  test_update_prb.py`, `tests/gol/tools/test_update_gol.py`, `tests/rsk/\n  tools/test_update_rsk.py` — depends on: Task 3.1 — status: not-started\n- [ ] Task 3.3: Update the seven domain `tools/__init__.py` files (remove the\n  `update_<d>` import, `__all__` entry, and the module-docstring tool-list\n  mention) and the seven domain `__init__.py` files (remove `update_<d>` from\n  the docstring tool enumeration; note that whole-body updates go through the\n  generic `update` tool in `general/tools/`) — depends on: Task 3.1 — status:\n  not-started\n- [ ] Task 3.4: Update `server.py`'s module docstring: remove `update_<d>`\n  from the seven per-domain Tools lines (the `set_status_<d>` entries stay\n  until Phase 4) — depends on: Task 3.1 — status: not-started\n- [ ] Task 3.5: Grep verification: `grep -rn \"update_req\\|update_uc\\|\n  update_tsk\\|update_qa\\|update_prb\\|update_gol\\|update_rsk\" src/ tests/`\n  must return only prompt-narration matches (the six `prompts/update_<d>.py`\n  module docstrings and their `data/*.md` files — Phase 5's ownership) and\n  nothing in `tools/`, `models/`, or `general/`; record the residual match\n  list in the Progress entry — depends on: Tasks 3.2, 3.3, 3.4 — status:\n  not-started\n- [ ] Task 3.6: Phase-end quality gate — full gate; `specmgr mcp-docs` +\n  `specmgr docs` regeneration, then `git diff --exit-code -- docs/` zero\n  drift (`docs/MCP.md` loses the seven `update_<d>` entries; `docs/api/`\n  loses the seven module pages); add a dated entry to the Recent Updates\n  section, update Current Status, flip the phase's task lines to done in\n  place — depends on: Task 3.5 — status: not-started\n\n#### Phase 4: Generic `set_status` + retire the eight old status tools\n\n- [ ] Task 4.1: Create `general/tools/set_status.py`: eight private adapters\n  `_set_status_<d>` — seven verbatim ports of the `set_status_<d>` bodies\n  (lock, `load_by_id`, raw body re-read via the established\n  `frontmatter.loads(...).content` mechanism, frontmatter reconstructed\n  through the domain `XFrontmatter` constructor so the closed vocabulary\n  validates, `updated` bump, body persisted verbatim, domain\n  `XNotFoundError`) plus the ADR port (lock, `load_by_id`, delegation to\n  `models.adr.v1.mutations.set_status(adr, status, superseded_by)`,\n  `write_adr` render round-trip, `AdrNotFoundError`); the guard\n  (`superseded_by is not None` and `type != \"adr\"` → `ValueError`, before any\n  file access); a dispatch table; and `@mcp.tool(name=\"set_status\", ...)`\n  `def set_status(id: str, type: Literal[\"req\",\"uc\",\"tsk\",\"qa\",\"prb\",\"gol\",\n  \"rsk\",\"adr\"], status: str, superseded_by: str | None = None) ->\n  ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument |\n  GolDocument | RskDocument | Adr` with a full numpy-style docstring —\n  depends on: Phase 3 complete (the `set_status` tool name must be free\n  before this tool registers — see Design Notes, Name-collision constraint) —\n  status: not-started\n- [ ] Task 4.2: Delete the eight superseded modules: `adr/tools/set_status.py`,\n  `req/tools/set_status_req.py`, `uc/tools/set_status_uc.py`,\n  `tsk/tools/set_status_tsk.py`, `qa/tools/set_status_qa.py`,\n  `prb/tools/set_status_prb.py`, `gol/tools/set_status_gol.py`,\n  `rsk/tools/set_status_rsk.py` — depends on: Task 4.1 — status: not-started\n- [ ] Task 4.3: Delete the eight test files: `tests/adr/tools/\n  test_set_status.py`, `tests/req/tools/test_set_status_req.py`,\n  `tests/uc/tools/test_set_status_uc.py`, `tests/tsk/tools/\n  test_set_status_tsk.py`, `tests/qa/tools/test_set_status_qa.py`,\n  `tests/prb/tools/test_set_status_prb.py`, `tests/gol/tools/\n  test_set_status_gol.py`, `tests/rsk/tools/test_set_status_rsk.py` — depends\n  on: Task 4.1 — status: not-started\n- [ ] Task 4.4: Register `set_status` in `general/tools/__init__.py` (import,\n  `__all__`, module docstring); update `adr/tools/__init__.py` and the seven\n  domain `tools/__init__.py` files (remove the `set_status*` imports,\n  `__all__` entries, and docstring mentions; note status changes go through\n  the generic `set_status` in `general/tools/`); update the eight domain\n  `__init__.py` docstring enumerations likewise — depends on: Tasks 4.2, 4.3 —\n  status: not-started\n- [ ] Task 4.5: Update `server.py`'s module docstring: remove `set_status`\n  from the ADR tools line and `set_status_<d>` from the seven per-domain\n  lines; add `set_status` to the General-tools lines (8-value `type`;\n  `superseded_by` is ADR-only) — depends on: Tasks 4.1, 4.4 — status: not-\n  started\n- [ ] Task 4.6: `tests/general/tools/test_set_status.py` — parameterized over\n  all eight types (ACC-004 cases): status changed + `updated` bumped + body\n  untouched (seven domains: raw body byte-identical; ADR: re-parsed document\n  equal apart from status/updated); closed-vocabulary enforcement per domain\n  (positive value from the domain's own set; negative value — re-read each\n  domain's `_ALLOWED_STATUSES` and pick a value valid in one domain but\n  invalid in the tested one, e.g. `implemented` against `rsk`/`uc`/`tsk`/`qa`/\n  `prb`, `open` against `req` — each → `pydantic.ValidationError`, file\n  untouched); ADR `superseded_by` composes `\"superseded by X\"` in the file;\n  ADR plain `status` values work with `superseded_by=None`; `superseded_by`\n  with any non-`adr` type → `ValueError`, file untouched; unknown id →\n  domain `XNotFoundError` / `AdrNotFoundError` — depends on: Task 4.1 —\n  status: not-started\n- [ ] Task 4.7: Phase-end quality gate — full gate including Task 4.6's new\n  tests; `specmgr mcp-docs` + `specmgr docs` regeneration, then `git diff\n  --exit-code -- docs/` zero drift; add a dated entry to the Recent Updates\n  section, update Current Status, flip the phase's task lines to done in\n  place — depends on: Tasks 4.5, 4.6 — status: not-started\n\n#### Phase 5: Narration rewrite (prompts + instruction data)\n\n- [ ] Task 5.1: Grep-driven rewrite of every instruction data file naming a\n  superseded tool (`grep -rn \"update_req\\|update_uc\\|update_tsk\\|update_qa\\|\n  update_prb\\|update_gol\\|update_rsk\\|set_status_\" src/biz/dfch/specmgr/\n  */data/` plus bare `set_status(` in the ADR data files). Eleven files\n  expected: the six `<d>_update_instructions.md` (req, tsk, qa, rsk, prb,\n  gol — `uc` has no prompts sub-package): `update_<d>(id, content)` →\n  `update(id, type=\"<d>\", content)`; `set_status_<d>(id, status)` →\n  `set_status(id, type=\"<d>\", status)`; **add a range-update passage** — for\n  a localized change (one paragraph/field/section), first call\n  `get_<d>(id, raw=True)` to see the exact body text, identify the 1-based\n  line range (the `N+1` position is end-of-body), and call\n  `update(id, type=\"<d>\", content, begin=…, end=…)` passing only the\n  replacement lines; for multi-section or uncertain changes, use the whole-\n  body replace (no `begin`/`end`); correct each file's status-vocabulary\n  prose where it differs per the Design-Notes table. `qa/data/\n  qa_refine_instructions.md`: its `update_qa` call sites → `update(id,\n  type=\"qa\", …)` (refine appends — use the `N+1` append range for a clean\n  append, else whole-body; keep the existing carry-forward guidance for the\n  whole-body path). The four ADR instruction files: `set_status(id, status[,\n  superseded_by])` → `set_status(id, type=\"adr\", status[, superseded_by])` —\n  depends on: Phase 4 complete — status: not-started\n- [ ] Task 5.2: Correct prompt Python module docstrings that name superseded\n  tools: the six `prompts/update_<d>.py` modules (rsk's is `update_risk.py`,\n  tsk's is `update_task.py`) — their module docstrings narrate the `update_<d>`\n  / `set_status_<d>` surface; the four ADR prompt modules (`create_adr.py`,\n  `create_adr_test.py`, `update_adr.py`, `update_adr_test.py`) — their\n  surface mentions of `set_status` stay true (the tool still exists, now\n  generic) but are made precise where they imply the old ADR-only signature.\n  No behavioral change to any prompt function — depends on: Task 5.1 —\n  status: not-started\n- [ ] Task 5.3: Update the ten prompt test files to assert the rewritten\n  narration: `tests/req/prompts/test_update_req.py`, `tests/tsk/prompts/\n  test_update_task.py`, `tests/qa/prompts/test_update_qa.py`, `tests/rsk/\n  prompts/test_update_risk.py`, `tests/prb/prompts/test_update_prb.py`,\n  `tests/gol/prompts/test_update_gol.py`, `tests/adr/prompts/\n  test_create_adr.py`, `tests/adr/prompts/test_create_adr_test.py`,\n  `tests/adr/prompts/test_update_adr.py`, `tests/adr/prompts/\n  test_update_adr_test.py` — assertions must confirm the generic call shapes\n  (and, for the six domain update prompts, the range-update passage) —\n  depends on: Tasks 5.1, 5.2 — status: not-started\n- [ ] Task 5.4: Phase-end quality gate — full gate (the prompt data files are\n  package data; `specmgr docs` regeneration covers Task 5.2's docstring\n  changes), then `git diff --exit-code -- docs/` zero drift; add a dated\n  entry to the Recent Updates section, update Current Status, flip the\n  phase's task lines to done in place — depends on: Task 5.3 — status: not-\n  started\n\n#### Phase 6: Cross-cutting documentation and release notes\n\n- [ ] Task 6.1: Update `AGENTS.md`: the seven per-domain bullets — remove\n  `update_<d>`/`set_status_<d>` from each tool enumeration and note that\n  whole-body/line-range updates go through the generic `update` tool and\n  status changes through the generic `set_status` tool (both in\n  `general/tools/`); the ADR bullet — remove `set_status` from its 12-wrapper\n  enumeration (11 remain); the `general/` bullet — add `update` (7-type;\n  optional `begin`/`end` range with the `N+1` sentinel) and `set_status`\n  (8-type; ADR-only `superseded_by`), and note the `raw` parameter on the\n  seven `get_<d>` tools; the \"Still genuinely missing / not yet done\" list —\n  add the convention note that future domains (e.g. `ac`) add one dispatch\n  entry to the two generic tools (plus a `raw` getter parameter) instead of\n  new `update_<d>`/`set_status_<d>` tools, citing the Phase-1 ADR id —\n  depends on: Phase 5 complete — status: not-started\n- [ ] Task 6.2: Update `CHANGELOG.md`'s `[Unreleased]` section: **Breaking** —\n  removed 14 MCP tools (`update_req`, `update_uc`, `update_tsk`,\n  `update_qa`, `update_prb`, `update_gol`, `update_rsk`, `set_status_req`,\n  `set_status_uc`, `set_status_tsk`, `set_status_qa`, `set_status_prb`,\n  `set_status_gol`, `set_status_rsk`) and ADR `set_status`'s signature\n  changes from `(id, status, superseded_by)` to `(id, type, status,\n  superseded_by)` with `type=\"adr\"` now required; **Added** — generic\n  `update(id, type, content, begin, end)` (7 types; optional 1-based\n  inclusive body-line range, `N+1` EOF sentinel, splice-then-validate-whole)\n  and generic `set_status(id, type, status, superseded_by)` (8 types);\n  optional `raw: bool = False` on the seven `get_<d>` tools (returns the\n  frontmatter-stripped body text verbatim — the text `begin`/`end` index\n  into); cite the Phase-1 ADR id — depends on: Phase 5 complete — status:\n  not-started\n- [ ] Task 6.3: Final regeneration: `uv run --frozen specmgr docs`, `uv run\n  --frozen specmgr mcp-docs`, `uv run --frozen specmgr adr-toc`, `uv run\n  --frozen specmgr schema` (models are untouched — expect no schema\n  changes); confirm `git diff --exit-code -- docs/` exits zero — depends on:\n  Task 6.1, Task 6.2 — status: not-started\n- [ ] Task 6.4: Phase-end quality gate — full gate; add a dated entry to the\n  Recent Updates section, update Current Status, flip the phase's task lines\n  to done in place — depends on: Task 6.3 — status: not-started\n\n#### Phase 7: Final cross-cutting verification\n\n- [ ] Task 7.1: Walk ACC-001…ACC-008 and confirm each with concrete evidence,\n  annotating the Acceptance Criteria section inline in the style of\n  feat-18-goal: live, un-mocked end-to-end in a temporary\n  `SPECMGR_DOCS_DIR` — for `req`, `rsk`, and `uc`: `create_<d>` →\n  `get_<d>(id, raw=True)` → `update(id, type, content, begin, end)` (one\n  middle-range replace verified byte-exact, one `N+1` append) → `get_<d>`\n  (content verified) → `set_status(id, type, status)` (domain-valid value\n  from the Design-Notes table) → `get_<d>` (status verified); for ADR:\n  `create_adr` → `set_status(id, type=\"adr\", status=\"superseded\",\n  superseded_by=…)` → status reads `\"superseded by …\"`; confirm\n  `asyncio.run(mcp.list_tools()/list_resources()/list_prompts())` on the\n  real `server.mcp` instance reports 71 tools / 25 resources / 19 prompts;\n  fresh-subprocess import check; full quality gate (ruff format/check, pylint\n  advisory, vulture, unittest, `specmgr docs`/`mcp-docs`/`adr-toc`/`schema`\n  zero drift); remove the temporary docs directory and confirm `git status`\n  shows no residue — depends on: Phases 1–6 complete — status: not-started\n- [ ] Task 7.2: Set this README's frontmatter `status: in-progress` →\n  `status: done`; final Recent Updates entry and Current Status summary —\n  depends on: Task 7.1 — status: not-started\n\n**Note:** If a task's scope changes mid-flight, edit its description in\nplace; rely on git history (`git log -p` on this file) to recover what was\noriginally planned, rather than keeping a second copy of the task around.\n\n## Progress\n\n### Current Status\n\n**As of 2026-08-26**: Planned. This README was drafted in the planning\nsession (all decisions in \"Decisions Made\" below are locked); all seven\nphases are not started. Execution is handed to the phase-orchestrator via\n`/implement-feature feat-0-consolidate-mutation-tools` (one phase-\nimplementer per phase, one Conventional Commit per accepted phase).\n\n### Blockers\n\nNone.\n\n### Recent Updates\n\n#### Update 2026-08-26 (planning session)\n\n- Completed: Feature planned end to end with the user. Design locked:\n  generic `update(id, type, content, begin, end)` for the seven whole-body\n  domains (line-range contract with the `N+1` EOF sentinel, splice-then-\n  validate-whole), generic `set_status(id, type, status, superseded_by)` for\n  all eight domains (ADR-only `superseded_by`), `get_<d>(raw=True)` body-text\n  read, outright deletion of the 15 superseded tools, per-domain prompts\n  kept with rewritten narration, and a short ADR (Phase 1).\n- Next: Phase 1 (ADR) via `/implement-feature feat-0-consolidate-mutation-\n  tools`.\n- Notes: Phase 4 is deliberately atomic (add generic `set_status` + delete\n  all eight old status tools) because ADR's existing tool already occupies\n  the `set_status` name. Target end state: 71 tools / 25 resources / 19\n  prompts (from 84/25/19).\n\n### Decisions Made\n\n- **2026-08-26**: Explicit `type` parameter on both generic tools rather\n  than bare-uuid resolution — per-domain v4 UUIDs are not *guaranteed*\n  unique, uuid-only would force an all-domains directory scan (parsing every\n  file) on the write path with cost growing per domain, and the calling\n  client always already knows the domain.\n- **2026-08-26**: ADR is excluded from `update` (its section-level MADR\n  contract — `update_frontmatter`/`update_section`/`option_*` — has no\n  whole-body replace by design) but included in `set_status` with the\n  `superseded_by` special case.\n- **2026-08-26**: The 15 superseded tools are deleted outright — no\n  deprecated wrapper release; the package is 0.x and the MCP tool list is\n  the only contract (breaking change recorded in `CHANGELOG.md`).\n- **2026-08-26**: The per-domain `update_*` prompts are kept (domain-\n  tailored interview guidance) and their narration text rewritten to the\n  generic tools — rather than consolidating seven near-duplicate prompts\n  into one generic prompt and losing domain-specific section names.\n- **2026-08-26**: The decision is recorded as a short ADR (Phase 1) rather\n  than README-only — it fixes a repo-wide convention future domains must\n  follow (per AGENTS.md's \"when in doubt, write the ADR\").\n- **2026-08-26**: `update` gains optional 1-based, inclusive `begin`/`end`\n  body-line coordinates with an `N+1` EOF sentinel (append/through-EOF); the\n  spliced result is always validated as a whole document before writing, and\n  unchanged regions stay byte-identical to disk (user request: smaller,\n  faster, safer targeted updates).\n- **2026-08-26**: Line numbers are served by `get_<d>(raw=True)` (shared\n  body-extraction helper with the splice) rather than re-introducing\n  `specmgr://<d>/{id}` resources — ADR ddfb1109's empirical finding that\n  agents invoke tools more reliably than parameterized resources, plus the\n  maintenance cost of seven new resource templates, decided it.\n\n### Related PRs / Commits\n\nNone yet (one Conventional Commit per accepted phase, created by the phase-\norchestrator with user confirmation).\n"
}
````

**Output:**

```
Wrote file successfully.
```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 72.7s)

_Thinking:_

Next, let's verify that the README is in the correct format. The repository has a `specmgr mdformat` tool, which formats markdown in place while preserving the frontmatter. Feature READMEs are hand-maintained, but running mdformat is consistent with the repository's conventions (AGENTS.md states that mdformat preserves YAML frontmatter). Let's run it and check the diff — no, actually, the feature READMEs in the repository: have they been mdformat-clean? Let's check whether the existing feature READMEs pass mdformat. Run specmgr mdformat against the new README and check git diff... it's untracked so there's no git diff baseline. Let's just run it and see whether it modifies the file (returns True/False).

Also, let's verify that the file renders correctly (check that the frontmatter is preserved).

One more thing: the "Existing feature folders" paragraph in AGENTS.md — it enumerates the existing feature folders. Should I add feat-0? This paragraph in AGENTS.md states: "Existing feature folders: `.specmgr/feat/feat-9-doc-in-specmgr/` ..., `.specmgr/feat/feat-4-use-cases/` ..., `.specmgr/feat/feat-5-md-model-parser/` ...". This is already outdated (feat-0 through 18 exist). Updating AGENTS.md is Phase 6's job, and the scope section explicitly excludes fixing existing outdated descriptions. Leave it as is.

Let's run mdformat to confirm the file is in the correct format (the phase implementer's gate will probably include ruff etc., but the mdformat cleanliness of the README itself isn't gated — feat-18's gate stated "verify that gol_reference.md is clean under specmgr mdformat" regarding data files. For feature READMEs, it's not required. Still, keeping it properly formatted is a good habit. Let's check whether existing feature READMEs are mdformat-clean, and align with that.)

I've created the README. Next, I'll verify whether it conforms to the repository's formatting conventions (comparing against the existing feature READMEs, I'll check the cleanliness of mdformat):

**Tool: bash**

**Input:**

```json
{
  "command": "uv run --frozen python -c \"\nfrom biz.dfch.specmgr.general.tools.mdformat import mdformat\nimport sys\nfor f in ['.specmgr/feat/feat-18-goal/README.md', '.specmgr/feat/feat-0-consolidate-mutation-tools/README.md']:\n    print(f, '->', mdformat(f))\n\""
}
```

**Output:**

```
.specmgr/feat/feat-18-goal/README.md -> True
.specmgr/feat/feat-0-consolidate-mutation-tools/README.md -> True

```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 52.0s)

_Thinking:_

Both got changed (True = file was modified). Wait — feat-18's README was changed by my run?! That means the existing feature README is *not* mdformat-clean, and I just modified feat-18's README as a side effect. Let me check what changed in feat-18 — I have to revert it (out of scope, and it would pollute the working tree).

Let me check git status and diff.

`mdformat` returned `True` for both — including the **existing** feat-18 README, which means I just modified a file that's out of scope. Let me check and revert:

**Tool: bash**

**Input:**

```json
{
  "command": "git status --short && git diff --stat"
}
```

**Output:**

```
 M .specmgr/feat/feat-18-goal/README.md
?? .specmgr/feat/feat-0-consolidate-mutation-tools/
 .specmgr/feat/feat-18-goal/README.md | 134 +++++++++++++----------------------
 1 file changed, 48 insertions(+), 86 deletions(-)

```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 64.7s)

_Thinking:_

Confirmed: existing feature READMEs are not mdformat-clean (the feat-18 README was significantly reformatted — 48 insertions / 86 deletions). So the repo convention is: feature READMEs are hand-maintained and are **not** subject to mdformat (the mdformat tool is for spec documents like ADRs, per AGENTS.md: "mdformat — formats a markdown file in place, preserving the YAML frontmatter block (for ADR/UC files)"). I mistakenly applied it.

Required actions:

1. Revert the feat-18 README: `git checkout -- .specmgr/feat/feat-18-goal/README.md`
2. Revert the formatting changes to my new README too? My README was also modified by mdformat. The question is: should my README be in the mdformat style, or in the hand-maintained style matching other feature READMEs? Other feature READMEs are **not** mdformat-clean, and this convention (hand-written, long lines, free prose) is consistent across feat-\*. My README before mdformat was in that hand-written style. mdformat reformatted it (line wrapping, list indentation, etc.).

Since existing feature READMEs aren't mdformat-formatted, I should revert my README to the hand-written version I originally created (to match the sibling files). Let me check what mdformat did to my file — it's untracked, so git checkout won't restore it. I'd need to rewrite the file… or I could just check the current state and decide.

Hmm, wait — actually let me think about which is better. Options:
A. Revert both files; keep my README in the hand-written style (matching all sibling feature READMEs).
B. Revert feat-18; keep my README in the mdformat-formatted version.

Consistency with sibling files wins: feature READMEs are hand-maintained and not subject to mdformat. If my README is the only mdformat-formatted one, it'll look inconsistent, and future phase updates (the implementer editing it) won't preserve the formatting (they'll just be editing lines, not re-running mdformat) — and nobody's gating it. So option A.

I need to restore my README to its pre-mdformat contents. I wrote it, so I can rewrite it exactly (I have the full text I passed to `write`). Let me do that.

First, revert feat-18.

Both feature READMEs in the repo are hand-maintained and are not mdformat-clean (mdformat is for ADR/spec documents). I applied it by mistake — I'll revert feat-18 and restore the hand-written style of my README to match the sibling files:

**Tool: bash**

**Input:**

```json
{
  "command": "git checkout -- .specmgr/feat/feat-18-goal/README.md && git status --short"
}
```

**Output:**

```
?? .specmgr/feat/feat-0-consolidate-mutation-tools/

```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 587.9s)

_Thinking:_

feat-18 has been reverted. Next, I'll rewrite my README with the original handwritten content (the one I wrote before mdformat touched it). Let me rewrite the same content as before (I have it verbatim from the write call).

feat-18 restored. Now rewriting my README back to the hand-written version (pre-mdformat), matching the sibling convention:

**Tool: write**

**Input:**

```json
{
  "content": "---\ncreated: 2026-08-26\nid: feat-0-consolidate-mutation-tools\nstatus: planning\nupdated: 2026-08-26\nversion: 1.0.0\n---\n\n# Feature: Consolidate update and set_status tools into generic type-dispatched tools\n\n## Plan\n\n### Overview\n\nReplace the 15 near-duplicate per-domain mutation MCP tools with two generic,\ncross-cutting tools that live in `general/tools/`: `update(id, type, content,\nbegin, end)` for whole-body (and now line-range) document replacement across\nthe seven whole-body domains (`req`, `uc`, `tsk`, `qa`, `prb`, `gol`, `rsk`),\nand `set_status(id, type, status, superseded_by)` for status changes across\nall eight domains including `adr`. The per-domain tools\n(`update_req`/`update_uc`/`update_tsk`/`update_qa`/`update_prb`/`update_gol`/\n`update_rsk`, `set_status_req`/`set_status_uc`/`set_status_tsk`/`set_status_qa`/\n`set_status_prb`/`set_status_gol`/`set_status_rsk`, and ADR's own `set_status`)\nare deleted outright (breaking; the package is 0.x and the MCP tool list is the\nonly contract). The generic `update` gains optional 1-based, inclusive\n`begin`/`end` body-line parameters so a client can replace a line range\nwithout re-sending the whole body — spliced into the current on-disk body and\nvalidated as a *whole* document before anything is written (the\nfilesystem-is-source-of-truth and validate-before-write invariants are\nuntouched). To make line targeting reliable, the seven `get_<d>` tools gain an\noptional `raw: bool = False` parameter returning the frontmatter-stripped body\ntext verbatim — the exact text `begin`/`end` index into (tool-first per ADR\nddfb1109; re-introducing `specmgr://<d>/{id}` resources was considered and\nrejected). ADR keeps its section-level mutation surface\n(`update_frontmatter`/`update_section`/`option_*`) unchanged — ADR is\ndeliberately *excluded* from `update` because it has no whole-body replace by\ndesign (MADR contract), but is *included* in `set_status` with its\n`superseded_by`-composition special case. A short ADR records the new\nconventions so future domains (e.g. `ac`) add one dispatch entry instead of a\nnew tool. Expected end state: **71 tools / 25 resources / 19 prompts**\n(today 84/25/19: −15 +2).\n\n### Requirements\n\n- REQ-001: A generic `update(id, type, content)` MCP tool in\n  `general/tools/update.py` covering the seven whole-body domains\n  (`type: Literal[\"req\",\"uc\",\"tsk\",\"qa\",\"prb\",\"gol\",\"rsk\"]`), preserving each\n  domain's existing whole-body semantics 1:1: body-only `content` (no\n  frontmatter block) validated via the domain's own\n  `X.from_text(format_text(content))` two-channel contract\n  (`AssertionError` structural / `pydantic.ValidationError` field-level,\n  nothing written on failure); under the domain's own lock, `load_by_id`,\n  every frontmatter field preserved except `updated` (bumped to the current\n  microsecond timestamp); `status` never settable through `update`; the\n  caller's raw `content` persisted verbatim via the domain's `write_X_file`;\n  unknown id raises the domain's own `XNotFoundError`.\n- REQ-002: Optional `begin: int | None` / `end: int | None` parameters on\n  `update`. When both are absent, behavior is exactly REQ-001 (backward-\n  compatible default). When both are given, `content` is a replacement\n  *fragment* for the current body's 1-based, inclusive line range\n  `begin..end`, where `N` = number of lines of the current frontmatter-\n  stripped body and `N+1` is a virtual position past the last line\n  (`begin = end = N+1` → append at end of body; `end = N+1` → range extends\n  through end of body). Misuse (exactly one of the two given, `begin < 1`,\n  `begin > end`, `end > N+1`) raises `ValueError` with a clear message and\n  writes nothing. The spliced *result* is validated as a whole body (REQ-001's\n  validation contract) before writing; unchanged regions of the on-disk body\n  remain byte-identical. An empty `content` fragment deletes the range (legal\n  iff the result still validates). The YAML frontmatter is never addressable\n  (coordinates are body-relative by construction).\n- REQ-003: The seven `get_<d>` tools (`get_req`, `get_uc`, `get_tsk`,\n  `get_qa`, `get_prb`, `get_gol`, `get_rsk`) gain an optional\n  `raw: bool = False` parameter. `raw=False` (default) behaves exactly as\n  today (returns the parsed `XDocument`). `raw=True` returns the\n  frontmatter-stripped body text of the document verbatim as a plain string —\n  produced by the *same* body-extraction helper the REQ-002 splice uses, so\n  the text a client counts lines in is byte-for-byte the text the server\n  splices against. Unknown id raises the domain's `XNotFoundError` in both\n  modes. No `get_adr` change (ADR is not a `update` type).\n- REQ-004: A generic `set_status(id, type, status, superseded_by=None)` MCP\n  tool in `general/tools/set_status.py` covering all eight domains\n  (`type: Literal[\"req\",\"uc\",\"tsk\",\"qa\",\"prb\",\"gol\",\"rsk\",\"adr\"]`). For the\n  seven whole-body domains, semantics are preserved 1:1 from the deleted\n  `set_status_<d>` tools: under the domain lock, `load_by_id`, the raw body\n  re-read and re-persisted verbatim (body never touched), the frontmatter\n  reconstructed through the domain's own `XFrontmatter` constructor so each\n  domain's closed status vocabulary validates (invalid `status` →\n  `pydantic.ValidationError`, nothing written), `updated` bumped, unknown id →\n  domain `XNotFoundError`. For `type=\"adr\"`, semantics are preserved 1:1 from\n  the deleted ADR `set_status` tool: delegates to\n  `models.adr.v1.mutations.set_status(adr, status, superseded_by)` (which\n  composes `status` as `\"superseded by {superseded_by}\"` when\n  `superseded_by` is given), `write_adr` render round-trip, `adr_lock`,\n  `AdrNotFoundError`. `superseded_by` given with any `type` other than\n  `\"adr\"` raises `ValueError` and writes nothing.\n- REQ-005: The 15 superseded tools are removed from source and from MCP\n  registration: `update_req`, `update_uc`, `update_tsk`, `update_qa`,\n  `update_prb`, `update_gol`, `update_rsk`, `set_status_req`,\n  `set_status_uc`, `set_status_tsk`, `set_status_qa`, `set_status_prb`,\n  `set_status_gol`, `set_status_rsk`, and ADR `set_status`. No deprecated\n  wrappers are kept (user decision; 0.x breaking change, recorded in\n  `CHANGELOG.md`).\n- REQ-006: All prompt narration referencing the superseded tools is rewritten\n  to the generic tools with correct signatures: the six domain\n  `<d>_update_instructions.md` files (req, tsk, qa, rsk, prb, gol — `uc` has\n  no prompts sub-package), `qa/data/qa_refine_instructions.md`, and the four\n  ADR instruction files (`adr_create_instructions.md`,\n  `adr_create_test_instructions.md`, `adr_update_instructions.md`,\n  `adr_update_test_instructions.md` — their `set_status(id, …)` call sites\n  gain `type=\"adr\"`). The six domain update-instruction files additionally\n  teach the REQ-002 range-update flow. Prompt Python module docstrings that\n  name the superseded tools are corrected (6 domain `prompts/update_<d>.py`\n  modules + 4 ADR prompt modules whose surface mentions become inaccurate).\n  The 10 corresponding prompt test files (6 domain + 4 ADR) are updated to\n  match the rewritten narration.\n- REQ-007: Documentation and registration consistency: `server.py` module\n  docstring (the authoritative tool/resource/prompt list) updated in the same\n  phase that changes the surface it describes; `docs/MCP.md`, `docs/api/`,\n  `docs/adr/README.md` regenerated with zero drift at every phase gate;\n  `AGENTS.md` per-domain bullets and the `general/` bullet updated;\n  `CHANGELOG.md` `[Unreleased]` carries the breaking-change and\n  addition entries; a short ADR (Phase 1) records the conventions (explicit\n  `type` over uuid-only resolution; ADR excluded from `update` but included\n  in `set_status`; the REQ-002 range contract; the REQ-003 raw-read-over-\n  resource decision; \"future domains add one dispatch entry, not a new\n  tool\").\n\n### Acceptance Criteria\n\n- [ ] ACC-001: Verifies REQ-001 — for every one of the seven types, `update`\n  in whole-body mode (no `begin`/`end`) replaces the body, preserves\n  `id`/`type`/`status`/`created`/`version`, bumps `updated` (microsecond\n  timestamp), never sets `status`, propagates structural `AssertionError` /\n  field `pydantic.ValidationError` with the file left byte-identical on disk,\n  and raises the domain's own `XNotFoundError` for an unknown id.\n- [ ] ACC-002: Verifies REQ-002 — for every one of the seven types: a middle-\n  range replace leaves all out-of-range body lines byte-identical and inserts\n  the fragment at the range; `begin = end = N+1` appends at end of body;\n  `end = N+1` replaces through end of body; empty `content` deletes the range\n  (verified with an optional-section deletion that yields a still-valid\n  document); `begin = 1`, `end = N` produces the same file as whole-body mode\n  with the identical text; each misuse case (one parameter only, `begin < 1`,\n  `begin > end`, `end > N+1`, range deleting the H1, range producing an\n  out-of-vocabulary field value) raises (`ValueError` / `AssertionError` /\n  `ValidationError`) with the file left byte-identical on disk.\n- [ ] ACC-003: Verifies REQ-003 — for all seven domains, `get_<d>(id,\n  raw=True)` returns the frontmatter-stripped body text byte-identical to the\n  on-disk body (the text whose lines `begin`/`end` address — proven by a test\n  that reads `raw`, picks a line range, calls `update` with that range, and\n  confirms the splice landed exactly there); `get_<d>(id)` (`raw=False`)\n  returns the parsed document exactly as before (regression); unknown id\n  raises the domain `XNotFoundError` in both modes.\n- [ ] ACC-004: Verifies REQ-004 — for all eight types, `set_status` changes\n  `status`, bumps `updated`, and leaves the body untouched (seven domains: raw\n  body byte-identical; ADR: re-render round-trip equal apart from\n  status/updated); each domain's closed vocabulary is enforced (out-of-set\n  value → `pydantic.ValidationError`, nothing written — including domain-\n  distinct sets: `uc` 5-value, `tsk`/`qa` 4-value, `prb` 4-value, `rsk`\n  6-value); ADR `superseded_by` composes `\"superseded by X\"`; `superseded_by`\n  with a non-`adr` type raises `ValueError`, nothing written; unknown id\n  raises the domain `XNotFoundError` / `AdrNotFoundError`.\n- [ ] ACC-005: Verifies REQ-005 — the 15 superseded tools are absent from\n  `src/` and from the live MCP registration; a grep over `src/` and `tests/`\n  finds no code references to the removed tool names (any residual mention\n  before Phase 5 is limited to the Phase-5-owned prompt narration files, and\n  zero afterwards); `vulture` is clean.\n- [ ] ACC-006: Verifies REQ-006 — all 11 instruction data files reference the\n  generic tools with the correct signatures (`update(id, type=\"<d>\", content\n  [,...])`, `set_status(id, type=..., status[, superseded_by])`); the six\n  domain update-instruction files teach the range-update flow (`get_<d>(id,\n  raw=True)` → identify the 1-based range → `update(..., begin, end)`; whole-\n  body for multi-section or uncertain changes); the 10 prompt test files pass\n  against the rewritten narration.\n- [ ] ACC-007: Verifies REQ-007 — `specmgr docs`, `specmgr mcp-docs`,\n  `specmgr adr-toc`, and `specmgr schema` all report zero drift;\n  `docs/MCP.md` shows the two new general tools (with `type` rendered as a 7-\n  / 8-value enum) and none of the 15 removed tools; `server.py`'s docstring\n  lists exactly the post-feature surface; `AGENTS.md` and `CHANGELOG.md` are\n  updated per REQ-007.\n- [ ] ACC-008: Verifies REQ-001/002/004/005 — the Phase-1 ADR exists in\n  `docs/adr/` with status `accepted` and is listed in `docs/adr/README.md`; a\n  live, un-mocked end-to-end run in a temporary `SPECMGR_DOCS_DIR` passes for\n  `req`, `rsk`, and `uc`: `create_<d>` → `get_<d>(id, raw=True)` →\n  `update(id, type, content, begin, end)` (one middle-range replace, one\n  `N+1` append) → `get_<d>` (content verified) → `set_status(id, type,\n  status)` (domain-valid value) → `get_<d>` (status verified); for ADR:\n  `create_adr` → `set_status(id, type=\"adr\", status=\"superseded\",\n  superseded_by=…)` → status reads `\"superseded by …\"`;\n  `asyncio.run(mcp.list_tools()/list_resources()/list_prompts())` on the real\n  `server.mcp` instance reports **71 tools / 25 resources / 19 prompts**; a\n  fresh subprocess import of `biz.dfch.specmgr.server` succeeds.\n\n### Scope\n\n**Included in this feature:**\n\n- `general/tools/update.py`, `general/tools/set_status.py`, and the shared\n  body-text/splice helpers (private module under `general/tools/`), plus\n  their registration in `general/tools/__init__.py`.\n- The `raw` parameter on the seven `get_<d>` tools.\n- Deletion of the 15 superseded tool modules, their test files, and all\n  code/docstring references outside Phase-5-owned narration.\n- The narration rewrite (11 instruction data files, prompt module\n  docstrings, 10 prompt test files).\n- The Phase-1 ADR, `AGENTS.md`, `CHANGELOG.md`, and all generated docs.\n\n**Explicitly out of scope:**\n\n- Any change to ADR's section-level mutation tools (`update_frontmatter`,\n  `update_section`, `option_*`) or to ADR's `specmgr://adr/{id}` resource —\n  ADR has no whole-body replace by design and is therefore not a `update`\n  type; its `set_status` behavior moves to the generic tool unchanged.\n- Re-introducing `specmgr://<d>/{id}` resources for the seven domains —\n  rejected in the planning session on ADR ddfb1109's empirical reliability\n  finding (agents invoke tools more reliably than parameterized resources);\n  `get_<d>(raw=True)` serves the same need (recorded in the Phase-1 ADR).\n- Consolidation of `create_*`, `get_*` (beyond the `raw` parameter),\n  `list_*`, `validate_*`, `parse_*`, or the `delete_*` stubs.\n- Any schema/model change: the per-domain status vocabularies, body schemas,\n  and `specmgr schema` outputs are untouched.\n- A version bump of `pyproject.toml` (release-time concern per `AGENTS.md`;\n  the breaking change lands in `[Unreleased]`).\n- The `ac` domain (does not exist yet) — but its *convention* is fixed by the\n  ADR: it will add one dispatch entry to the two generic tools, not new\n  tools.\n- The pre-existing, already-documented AGENTS.md staleness items (e.g. the\n  historical \"REQ, UC, and TSK were built after that refactor\" enumeration) —\n  fixing unrelated stale text is not part of this feature.\n\n### Dependencies\n\n- Depends on: ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614 (id-based reads are\n  tool-first — the basis for `raw` on `get_<d>` instead of `/{id}`\n  resources); ADR ece4554b-725c-4f76-bc04-5d2b760363d2 (domain-first\n  hierarchy — the generic tools live in the cross-cutting `general/`\n  package, reusing each domain's private helpers); ADR\n  3bf0326f-065a-424c-a2b9-87e5d5bcfa99 (the `mcp` singleton lives in\n  `server.py` — import-order consideration, see Design Notes); ADR\n  71fd95d7-07f2-466f-81aa-d29b7e3ef34c (ADR's `update_section` contract —\n  what `update` deliberately does *not* extend to ADR); ADR\n  898bfcd0-85f9-462f-93a8-747bda4166c8 (ADRs are authored/edited only\n  through the MCP structured tools — Phase 1 must use `specmgr_create_adr`);\n  ADR 33c5ab08-ff58-4c73-8c32-23abaf3838e3 (filesystem is the sole source of\n  truth — the splice re-reads the on-disk body and the validate-before-write\n  invariant is preserved); the existing `general/tools/_doc_paths.py`/\n  `_packaged_data.py` infrastructure and each domain's `_paths`/`_io`/\n  `_write`/`_lock` private helpers (reused as-is, not modified).\n- Blocks: none. Future domain work (e.g. `ac`) must follow the ADR's\n  dispatch-entry convention.\n\n### Design Notes\n\n**Dispatch architecture.** Each of the two generic tools is a thin MCP\nwrapper around a dispatch table `dict[str, Callable]` mapping the `type`\nvalue to a private adapter function (`_update_<d>` / `_set_status_<d>`). Each\nadapter is a **verbatim port** of the corresponding deleted tool's function\nbody (same lock, same `load_by_id`, same frontmatter carry-over / `updated`\nbump, same `write_X_file`, same domain `XNotFoundError`) — for `update`, plus\nthe REQ-002 range branch; for `set_status`, the ADR adapter ports\n`adr/tools/set_status.py` including its delegation to\n`models.adr.v1.mutations.set_status`. Domain private helpers (`_paths`,\n`_io`, `_write`, `_lock`) and domain models are **not modified** —\n`create_*`/`get_*`/`validate_*`/`list_*` keep using them exactly as today,\nand the new adapters import them the same way the old tools did. The adapters\nand table live in `general/tools/` because the tools are cross-cutting (the\n`general/` package is the documented home for non-domain-specific tools, per\n`AGENTS.md`); no new shared *code* is added to the domain packages.\n\n**`update` signature and return type.**\n\n    @mcp.tool(\n        name=\"update\",\n        title=\"Update document\",\n        description=(...),  # whole-body or line-range replace; type = domain;\n    )                       # begin/end optional 1-based inclusive body-line range\n    def update(\n        id: str,\n        type: Literal[\"req\", \"uc\", \"tsk\", \"qa\", \"prb\", \"gol\", \"rsk\"],\n        content: str,\n        begin: int | None = None,\n        end: int | None = None,\n    ) -> ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument | GolDocument | RskDocument:\n\nThe parameter is named `type` (matches the frontmatter field vocabulary the\nclient already knows; ruff's enabled rule set E/F/W has no builtin-shadowing\nrule). The 7-way union return type is annotation-only — the MCP input schema\nis built from the parameters, and the SDK serializes whichever concrete\ndocument is returned. The `type` value must render as a 7-entry JSON-schema\n`enum` in `docs/MCP.md` (verify in the Phase 2 gate).\n\n**Range contract (REQ-002), precisely.** Let `N` be the number of lines of\nthe current frontmatter-stripped body (`len(body_text.splitlines())`).\nCoordinates are 1-based and inclusive. `N+1` is a virtual position past the\nlast line:\n\n- `begin = end = k` (1 ≤ k ≤ N) → replace line `k` only.\n- `begin = k`, `end = m` (k ≤ m ≤ N) → replace lines `k..m`.\n- `end = N+1` → the range extends through the last line (`k..N`).\n- `begin = end = N+1` → the range is empty at end-of-body: pure append.\n- `begin = 1`, `end = N` → whole-body replace, file-identical to whole-body\n  mode with the same text (test this equivalence).\n- Empty `content` → the range is deleted (legal iff the result validates).\n\nMisuse → `ValueError` (client-controlled input, **not** `assert` — per\n`.specmgr/conventions.md` Rule 3): exactly one of `begin`/`end` given;\n`begin < 1`; `begin > end`; `end > N + 1`. The error message names the\noffending value(s) and the allowed range. Splice algorithm: take the on-disk\nbody lines, drop lines `begin..min(end, N)`, insert `content.splitlines()` at\nposition `begin - 1`, rejoin with `\"\\n\"` plus a single trailing `\"\\n\"`. The\n**result** is validated exactly like whole-body mode (`X.from_text(\nformat_text(spliced))`) and the spliced text (not the fragment) is persisted\nverbatim via the domain `write_X_file` — so out-of-range regions are\nbyte-identical to disk and no renderer ever touches them. Frontmatter\naddressing is impossible by construction: the body text is extracted with the\nfrontmatter block removed, and coordinates are defined relative to that text\nonly.\n\n**Shared body extraction + `raw` invariant (REQ-003).** One private helper\n(live in a new `general/tools/_splice.py` alongside the splice function, no\n`mcp` dependency — plain file I/O, mirroring `_doc_paths.py`'s placement)\nreturns the frontmatter-stripped body text of a file using the established\n`frontmatter.loads(path.read_text(encoding=\"utf-8\")).content` mechanism (the\nsame one all seven `set_status_<d>` tools use today). Both the REQ-002 splice\nand each `get_<d>(raw=True)` call go through this one helper, which *is* the\n\"what the client counts is what the server splices\" invariant of ACC-003.\n`get_<d>` with `raw=True` stays read-only: no lock, no directory creation —\nmatching every existing `get_<d>`.\n\n**`set_status` signature and the `superseded_by` guard (REQ-004).**\n\n    @mcp.tool(\n        name=\"set_status\",\n        title=\"Set document status\",\n        description=(...),  # type = domain (8 values, incl. adr);\n    )                       # superseded_by: adr only\n    def set_status(\n        id: str,\n        type: Literal[\"req\", \"uc\", \"tsk\", \"qa\", \"prb\", \"gol\", \"rsk\", \"adr\"],\n        status: str,\n        superseded_by: str | None = None,\n    ) -> ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument | GolDocument | RskDocument | Adr:\n\nPer-domain closed status vocabularies (authoritative source: each domain's\n`_ALLOWED_STATUSES` in `models/<v>/frontmatter.py` — re-read them when\nimplementing; the table below reflects 2026-08-26): `req` and `gol`:\n`draft`/`proposed`/`accepted`/`superseded`/`deprecated`/`rejected`/\n`implemented` (7); `uc`: `draft`/`proposed`/`accepted`/`deprecated`/\n`superseded` (5); `tsk` and `qa`: `draft`/`active`/`done`/`cancelled` (4);\n`prb`: `draft`/`active`/`resolved`/`cancelled` (4); `rsk`: `open`/\n`mitigating`/`accepted`/`occurred`/`closed`/`dropped` (6); `adr`: 6 values\n(`draft`/`proposed`/`rejected`/`accepted`/`deprecated`/`superseded`) plus the\n`\"superseded by X\"` pattern. The guard `superseded_by is not None and type !=\n\"adr\"` → `ValueError` runs **before** any file access.\n\n**Import-order consideration.** `server.py` imports the domain packages in\none bottom-of-file line, with `general` second (`from . import adr, general,\ngol, prb, qa, req, rsk, tsk, uc`). Once `general/tools/__init__.py` registers\nthe new tools, importing `general` pulls in **all** seven domain `tools` (and\n`prompts`) packages earlier than today. This is safe by construction: every\ndomain tool module already does `from ...server import mcp` while\n`server.py` is still executing its import line (the `mcp` name is bound at\n`server.py:197`, before the import line at `server.py:211`), and every\n`general.tools._packaged_data` import in domain prompts/resources uses the\nsubmodule form (`from ...general.tools._packaged_data import read_packaged_\ntext`), which is safe mid-initialization. The Phase 2 gate's fresh-subprocess\nimport smoke test (ACC-008) proves it rather than assuming it.\n\n**Docs discipline.** `server.py`'s module docstring is updated *inside* each\nphase that changes the surface it describes (Phase 2 adds both tools' lines\nas they are added; Phase 3 removes the `update_<d>` lines; Phase 4 removes\nthe `set_status_<d>` + ADR `set_status` lines). `docs/MCP.md` and\n`docs/api/` are regenerated in every phase gate and must be drift-free\n(`git diff --exit-code -- docs/`) at every phase commit — the pre-commit\nhooks enforce this for any commit touching `src/`.\n\n**Name-collision constraint.** ADR's existing tool is already named\n`set_status`. Registering the generic `set_status` while `adr/tools/\nset_status.py` still exists would double-register the name, which is why\nPhase 4 adds the generic tool and deletes all eight old status tools in one\nphase. (No such constraint exists for `update` — Phase 2 is purely additive,\nPhase 3 deletes the seven `update_<d>` tools.)\n\n**Phase-end quality gate (every phase).** Unless a phase task says otherwise:\n`uv run --frozen ruff format --check`, `uv run --frozen ruff check`, `uv run\n--frozen vulture src/ whitelist.py --min-confidence 60`, `uv run --frozen\npython -m unittest discover -v -s tests -t . -p \"test_*.py\"`, plus the\n`specmgr docs` / `specmgr mcp-docs` / `specmgr adr-toc` / `specmgr schema`\nregenerations the phase touches, then `git diff --exit-code -- docs/`. Fix\nfailures and re-run until green — a phase is not done with a red gate. Then\nupdate this README: a dated entry in the **Recent Updates** section, Current\nStatus, and the phase's task lines flipped to done in place.\n\n### Related ADRs\n\n- ddfb1109-422d-4507-8dbc-dc5e4bec9614: Expose id-based document reads as a\n  tool (`get_<d>`), not a resource — the basis for `get_<d>(raw=True)`\n  instead of re-introducing `specmgr://<d>/{id}` resources\n- ece4554b-725c-4f76-bc04-5d2b760363d2: Organize the codebase by document-\n  type domain — the generic tools live in the cross-cutting `general/`\n  package, reusing domain-private helpers\n- 3bf0326f-065a-424c-a2b9-87e5d5bcfa99: Extract the `mcp` singleton into its\n  own module — the import-order consideration in Design Notes\n- 71fd95d7-07f2-466f-81aa-d29b7e3ef34c: Generic `update_section` (ADR\n  domain) — the section-level contract that `update` deliberately does not\n  extend to ADR\n- 898bfcd0-85f9-462f-93a8-747bda4166c8: Author and edit ADRs only through MCP\n  structured tools — Phase 1 must use `specmgr_create_adr`, never a hand-\n  written file\n- 33c5ab08-ff58-4c73-8c32-23abaf3838e3: Filesystem is the sole source of\n  truth — the splice re-reads the on-disk body; validate-before-write\n- (Phase 1 creates the feature's own short ADR; its id is recorded in\n  Decisions Made once created)\n\n### Task List\n\nSingle, canonical breakdown of work phases and tasks. Status lives on the\ntask itself. Each phase ends with a mandatory phase-end quality-gate task\n(full gate per Design Notes + this README's Progress update), and the\nphase-orchestrator commits each accepted phase as one Conventional Commit.\n\n#### Phase 1: ADR\n\n- [ ] Task 1.1: Create the feature's ADR with the `specmgr_create_adr` MCP\n  tool (never hand-write the file — ADR 898bfcd0), status `accepted`, title\n  \"Consolidate whole-body update and status-change tools into generic type-\n  dispatched tools\": Context (15 near-duplicate mutation tools; LLM clients\n  see 15 entries for 2 conceptual operations; each new domain would add\n  more); Decision Drivers (simpler tool surface; no all-directories write-\n  path scan and no per-domain v4-UUID-collision ambiguity — uuid-only\n  resolution was rejected; the client already knows the domain; preserve the\n  filesystem-source-of-truth and validate-before-write invariants);\n  Considered Options (1: generic tools with explicit `type` — chosen; 2:\n  uuid-only id resolution scanning all domain directories; 3: keep per-\n  domain tools); Decision Outcome (Option 1) with Consequences (breaking: 14\n  per-domain tools removed and ADR `set_status`'s signature gains a required\n  `type`; ADR is excluded from `update` — its section-level MADR contract\n  has no whole-body replace — but included in `set_status` with the\n  `superseded_by` special case; the `update` line-range contract: 1-based\n  inclusive `begin`/`end`, `N+1` EOF sentinel, splice-then-validate-whole,\n  frontmatter never addressable; `get_<d>(raw=True)` as the line-number\n  source — tool-first per ADR ddfb1109, re-introducing `specmgr://<d>/{id}`\n  resources was considered and rejected; future domains add one dispatch\n  entry per generic tool, not new tools) — depends on: none — status: not-\n  started\n- [ ] Task 1.2: Validate the new ADR with `specmgr_validate_adr`; run `uv run\n  --frozen specmgr adr-toc` and confirm the ADR appears in\n  `docs/adr/README.md` — depends on: Task 1.1 — status: not-started\n- [ ] Task 1.3: Phase-end quality gate — full gate (ruff format --check, ruff\n  check, vulture, full unittest suite; no `src/` changes are expected, so\n  `docs/` drift checks cover `specmgr adr-toc` output only); set this\n  README's frontmatter `status: planning` → `status: in-progress`; add a\n  dated entry to the Recent Updates section, update Current Status, flip the\n  phase's task lines to done in place; record the new ADR's id — depends on:\n  Task 1.2 — status: not-started\n\n#### Phase 2: Generic `update` tool + `raw` read parameter\n\n- [ ] Task 2.1: Create `general/tools/_splice.py` (no `mcp` dependency, plain\n  file I/O + text manipulation, module docstring explaining the raw/splice\n  invariant): `body_text(path: Path) -> str` (frontmatter-stripped body text\n  via the established `frontmatter.loads(...).content` mechanism) and\n  `splice_body(current_body: str, begin: int, end: int, content: str) -> str`\n  (implements the Design-Notes range contract exactly: `N` = `len(\n  current_body.splitlines())`; `ValueError` with a clear message for `begin <\n  1`, `begin > end`, `end > N + 1`; drop lines `begin..min(end, N)`; insert\n  `content.splitlines()` at position `begin - 1`; rejoin `\"\\n\"` + single\n  trailing `\"\\n\"`; empty `content` = deletion) — depends on: none — status:\n  not-started\n- [ ] Task 2.2: Create `general/tools/update.py`: seven private adapter\n  functions `_update_<d>(id_, content, begin, end)` — verbatim ports of the\n  current `update_<d>` function bodies (same `X_lock`, `load_by_id`,\n  frontmatter carry-over + microsecond `updated` bump, `write_X_file`,\n  domain `XNotFoundError`) with the range branch added (no `begin`/`end` →\n  today's behavior: validate `X.from_text(format_text(content))`, persist\n  `content` verbatim; both given → `body_text` + `splice_body`, validate the\n  *result* via `X.from_text(format_text(spliced))`, persist the *spliced*\n  text verbatim; the both-or-neither `ValueError` guard runs before any file\n  access); a dispatch table; and `@mcp.tool(name=\"update\", ...)` `def\n  update(id: str, type: Literal[\"req\",\"uc\",\"tsk\",\"qa\",\"prb\",\"gol\",\"rsk\"],\n  content: str, begin: int | None = None, end: int | None = None) ->\n  ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument |\n  GolDocument | RskDocument` with a full numpy-style docstring (including\n  the range contract and the error types) — depends on: Task 2.1 — status:\n  not-started\n- [ ] Task 2.3: Register `update` in `general/tools/__init__.py` (import,\n  `__all__`, module docstring) — depends on: Task 2.2 — status: not-started\n- [ ] Task 2.4: Add the `raw: bool = False` parameter to the seven `get_<d>`\n  tools (`req/tools/get_req.py`, `uc/tools/get_uc.py`, `tsk/tools/get_tsk.py`,\n  `qa/tools/get_qa.py`, `prb/tools/get_prb.py`, `gol/tools/get_gol.py`,\n  `rsk/tools/get_rsk.py`): signature `get_<d>(id: str, raw: bool = False) ->\n  XDocument | str`; `raw=True` resolves the id as today (no lock — read-only)\n  and returns `body_text(path)` (the same helper the splice uses, per the\n  Design-Notes invariant); `raw=False` returns the parsed document exactly as\n  today; update each tool's `@mcp.tool` description and docstring Returns\n  section — depends on: Task 2.1 — status: not-started\n- [ ] Task 2.5: Update `server.py`'s module docstring: add `update` to the\n  General-tools lines (one line describing whole-body *and* line-range\n  replace, the 7-value `type`, optional `begin`/`end`); note the `raw`\n  parameter where the seven `get_<d>` tools are enumerated — depends on:\n  Task 2.2, Task 2.4 — status: not-started\n- [ ] Task 2.6: `tests/general/tools/test_update.py` — parameterized over all\n  seven types (seed a document per type, e.g. via the domain `create_<d>`\n  tool in a temp `SPECMGR_DOCS_DIR`, mirroring the fixture strategy of the\n  `tests/<d>/tools/test_update_<d>.py` files still on disk at this phase):\n  whole-body mode (ACC-001 cases: body replaced; id/type/status/created/\n  version preserved; `updated` bumped; status not settable; structural\n  `AssertionError` and field `ValidationError` each leave the file\n  byte-identical; unknown id → domain `XNotFoundError`); range mode (ACC-002\n  cases: middle-range replace with out-of-range lines byte-identical; `N+1`\n  append; `end=N+1` replace-through-EOF; empty-fragment deletion of an\n  optional section yielding a valid document; `begin=1`/`end=N` ≡ whole-body;\n  every `ValueError` misuse case; range deleting the H1 → `AssertionError`,\n  file untouched; range producing an out-of-vocabulary field value →\n  `ValidationError`, file untouched) — depends on: Task 2.2 — status: not-\n  started\n- [ ] Task 2.7: Extend each domain's existing `tests/<d>/tools/test_get_<d>.py`\n  (seven files) with `raw` coverage (ACC-003 cases): `raw=True` returns the\n  body text byte-identical to the on-disk frontmatter-stripped body; the\n  coordinate invariant (read `raw`, pick a real line range, `update` with it,\n  assert the splice landed exactly there); `raw=False` regression (parsed\n  document as before); unknown id → `XNotFoundError` in both modes — depends\n  on: Task 2.4, Task 2.2 — status: not-started\n- [ ] Task 2.8: Registration smoke test: a unittest asserting\n  `asyncio.run(mcp.list_tools())` contains `update` with `type` rendered as a\n  7-value `enum` and optional integer `begin`/`end` in the input schema, plus\n  a fresh-subprocess `uv run --frozen python -c \"import biz.dfch.specmgr.\n  server\"` check run inside the phase gate (import-order proof, Design Notes)\n  — depends on: Task 2.3 — status: not-started\n- [ ] Task 2.9: Phase-end quality gate — full gate including Tasks 2.6–2.8's\n  new tests; `uv run --frozen specmgr mcp-docs` and `uv run --frozen specmgr\n  docs` regeneration, then `git diff --exit-code -- docs/` zero drift;\n  confirm `docs/MCP.md` shows the `update` entry (enum) and the `raw` note on\n  the `get_<d>` entries; add a dated entry to the Recent Updates section,\n  update Current Status, flip the phase's task lines to done in place —\n  depends on: Tasks 2.3, 2.5, 2.8 — status: not-started\n\n#### Phase 3: Retire the per-domain `update_*` tools\n\n- [ ] Task 3.1: Delete the seven tool modules: `req/tools/update_req.py`,\n  `uc/tools/update_uc.py`, `tsk/tools/update_tsk.py`, `qa/tools/update_qa.py`,\n  `prb/tools/update_prb.py`, `gol/tools/update_gol.py`,\n  `rsk/tools/update_rsk.py` — depends on: Phase 2 complete — status: not-\n  started\n- [ ] Task 3.2: Delete the seven test files: `tests/req/tools/\n  test_update_req.py`, `tests/uc/tools/test_update_uc.py`, `tests/tsk/tools/\n  test_update_tsk.py`, `tests/qa/tools/test_update_qa.py`, `tests/prb/tools/\n  test_update_prb.py`, `tests/gol/tools/test_update_gol.py`, `tests/rsk/\n  tools/test_update_rsk.py` — depends on: Task 3.1 — status: not-started\n- [ ] Task 3.3: Update the seven domain `tools/__init__.py` files (remove the\n  `update_<d>` import, `__all__` entry, and the module-docstring tool-list\n  mention) and the seven domain `__init__.py` files (remove `update_<d>` from\n  the docstring tool enumeration; note that whole-body updates go through the\n  generic `update` tool in `general/tools/`) — depends on: Task 3.1 — status:\n  not-started\n- [ ] Task 3.4: Update `server.py`'s module docstring: remove `update_<d>`\n  from the seven per-domain Tools lines (the `set_status_<d>` entries stay\n  until Phase 4) — depends on: Task 3.1 — status: not-started\n- [ ] Task 3.5: Grep verification: `grep -rn \"update_req\\|update_uc\\|\n  update_tsk\\|update_qa\\|update_prb\\|update_gol\\|update_rsk\" src/ tests/`\n  must return only prompt-narration matches (the six `prompts/update_<d>.py`\n  module docstrings and their `data/*.md` files — Phase 5's ownership) and\n  nothing in `tools/`, `models/`, or `general/`; record the residual match\n  list in the Progress entry — depends on: Tasks 3.2, 3.3, 3.4 — status: not-\n  started\n- [ ] Task 3.6: Phase-end quality gate — full gate; `specmgr mcp-docs` +\n  `specmgr docs` regeneration, then `git diff --exit-code -- docs/` zero\n  drift (`docs/MCP.md` loses the seven `update_<d>` entries; `docs/api/`\n  loses the seven module pages); add a dated entry to the Recent Updates\n  section, update Current Status, flip the phase's task lines to done in\n  place — depends on: Task 3.5 — status: not-started\n\n#### Phase 4: Generic `set_status` + retire the eight old status tools\n\n- [ ] Task 4.1: Create `general/tools/set_status.py`: eight private adapters\n  `_set_status_<d>` — seven verbatim ports of the `set_status_<d>` bodies\n  (lock, `load_by_id`, raw body re-read via the established\n  `frontmatter.loads(...).content` mechanism, frontmatter reconstructed\n  through the domain `XFrontmatter` constructor so the closed vocabulary\n  validates, `updated` bump, body persisted verbatim, domain\n  `XNotFoundError`) plus the ADR port (lock, `load_by_id`, delegation to\n  `models.adr.v1.mutations.set_status(adr, status, superseded_by)`,\n  `write_adr` render round-trip, `AdrNotFoundError`); the guard (`\n  superseded_by is not None` and `type != \"adr\"` → `ValueError`, before any\n  file access); a dispatch table; and `@mcp.tool(name=\"set_status\", ...)`\n  `def set_status(id: str, type: Literal[\"req\",\"uc\",\"tsk\",\"qa\",\"prb\",\"gol\",\n  \"rsk\",\"adr\"], status: str, superseded_by: str | None = None) ->\n  ReqDocument | UcDocument | TskDocument | QaDocument | PrbDocument |\n  GolDocument | RskDocument | Adr` with a full numpy-style docstring —\n  depends on: Phase 3 complete (the `set_status` tool name must be free\n  before this tool registers — see Design Notes, Name-collision constraint) —\n  status: not-started\n- [ ] Task 4.2: Delete the eight superseded modules: `adr/tools/set_status.py`,\n  `req/tools/set_status_req.py`, `uc/tools/set_status_uc.py`,\n  `tsk/tools/set_status_tsk.py`, `qa/tools/set_status_qa.py`,\n  `prb/tools/set_status_prb.py`, `gol/tools/set_status_gol.py`,\n  `rsk/tools/set_status_rsk.py` — depends on: Task 4.1 — status: not-started\n- [ ] Task 4.3: Delete the eight test files: `tests/adr/tools/\n  test_set_status.py`, `tests/req/tools/test_set_status_req.py`,\n  `tests/uc/tools/test_set_status_uc.py`, `tests/tsk/tools/\n  test_set_status_tsk.py`, `tests/qa/tools/test_set_status_qa.py`,\n  `tests/prb/tools/test_set_status_prb.py`, `tests/gol/tools/\n  test_set_status_gol.py`, `tests/rsk/tools/test_set_status_rsk.py` — depends\n  on: Task 4.1 — status: not-started\n- [ ] Task 4.4: Register `set_status` in `general/tools/__init__.py` (import,\n  `__all__`, module docstring); update `adr/tools/__init__.py` and the seven\n  domain `tools/__init__.py` files (remove the `set_status*` imports,\n  `__all__` entries, and docstring mentions; note status changes go through\n  the generic `set_status` in `general/tools/`); update the eight domain\n  `__init__.py` docstring enumerations likewise — depends on: Tasks 4.2, 4.3 —\n  status: not-started\n- [ ] Task 4.5: Update `server.py`'s module docstring: remove `set_status`\n  from the ADR tools line and `set_status_<d>` from the seven per-domain\n  lines; add `set_status` to the General-tools lines (8-value `type`;\n  `superseded_by` is ADR-only) — depends on: Tasks 4.1, 4.4 — status: not-\n  started\n- [ ] Task 4.6: `tests/general/tools/test_set_status.py` — parameterized over\n  all eight types (ACC-004 cases): status changed + `updated` bumped + body\n  untouched (seven domains: raw body byte-identical; ADR: re-parsed document\n  equal apart from status/updated); closed-vocabulary enforcement per domain\n  (positive value from the domain's own set; negative value — re-read each\n  domain's `_ALLOWED_STATUSES` and pick a value valid in one domain but\n  invalid in the tested one, e.g. `implemented` against `rsk`/`uc`/`tsk`/`qa`/\n  `prb`, `open` against `req` — each → `pydantic.ValidationError`, file\n  untouched); ADR `superseded_by` composes `\"superseded by X\"` in the file;\n  ADR plain `status` values work with `superseded_by=None`; `superseded_by`\n  with any non-`adr` type → `ValueError`, file untouched; unknown id →\n  domain `XNotFoundError` / `AdrNotFoundError` — depends on: Task 4.1 —\n  status: not-started\n- [ ] Task 4.7: Phase-end quality gate — full gate including Task 4.6's new\n  tests; `specmgr mcp-docs` + `specmgr docs` regeneration, then `git diff\n  --exit-code -- docs/` zero drift; add a dated entry to the Recent Updates\n  section, update Current Status, flip the phase's task lines to done in\n  place — depends on: Tasks 4.5, 4.6 — status: not-started\n\n#### Phase 5: Narration rewrite (prompts + instruction data)\n\n- [ ] Task 5.1: Grep-driven rewrite of every instruction data file naming a\n  superseded tool (`grep -rn \"update_req\\|update_uc\\|update_tsk\\|update_qa\\|\n  update_prb\\|update_gol\\|update_rsk\\|set_status_\" src/biz/dfch/specmgr/\n  */data/` plus bare `set_status(` in the ADR data files). Eleven files\n  expected: the six `<d>_update_instructions.md` (req, tsk, qa, rsk, prb,\n  gol — `uc` has no prompts sub-package): `update_<d>(id, content)` →\n  `update(id, type=\"<d>\", content)`; `set_status_<d>(id, status)` →\n  `set_status(id, type=\"<d>\", status)`; **add a range-update passage** — for\n  a localized change (one paragraph/field/section), first call\n  `get_<d>(id, raw=True)` to see the exact body text, identify the 1-based\n  line range (the `N+1` position is end-of-body), and call\n  `update(id, type=\"<d>\", content, begin=…, end=…)` passing only the\n  replacement lines; for multi-section or uncertain changes, use the whole-\n  body replace (no `begin`/`end`); correct each file's status-vocabulary\n  prose where it differs per the Design-Notes table. `qa/data/\n  qa_refine_instructions.md`: its `update_qa` call sites → `update(id,\n  type=\"qa\", …)` (refine appends — use the `N+1` append range for a clean\n  append, else whole-body; keep the existing carry-forward guidance for the\n  whole-body path). The four ADR instruction files: `set_status(id, status[,\n  superseded_by])` → `set_status(id, type=\"adr\", status[, superseded_by])` —\n  depends on: Phase 4 complete — status: not-started\n- [ ] Task 5.2: Correct prompt Python module docstrings that name superseded\n  tools: the six `prompts/update_<d>.py` modules (rsk's is `update_risk.py`,\n  tsk's is `update_task.py`) — their module docstrings narrate the\n  `update_<d>` / `set_status_<d>` surface; the four ADR prompt modules\n  (`create_adr.py`, `create_adr_test.py`, `update_adr.py`,\n  `update_adr_test.py`) — their surface mentions of `set_status` stay true\n  (the tool still exists, now generic) but are made precise where they imply\n  the old ADR-only signature. No behavioral change to any prompt function —\n  depends on: Task 5.1 — status: not-started\n- [ ] Task 5.3: Update the ten prompt test files to assert the rewritten\n  narration: `tests/req/prompts/test_update_req.py`, `tests/tsk/prompts/\n  test_update_task.py`, `tests/qa/prompts/test_update_qa.py`, `tests/rsk/\n  prompts/test_update_risk.py`, `tests/prb/prompts/test_update_prb.py`,\n  `tests/gol/prompts/test_update_gol.py`, `tests/adr/prompts/\n  test_create_adr.py`, `tests/adr/prompts/test_create_adr_test.py`,\n  `tests/adr/prompts/test_update_adr.py`, `tests/adr/prompts/\n  test_update_adr_test.py` — assertions must confirm the generic call shapes\n  (and, for the six domain update prompts, the range-update passage) —\n  depends on: Tasks 5.1, 5.2 — status: not-started\n- [ ] Task 5.4: Phase-end quality gate — full gate (the prompt data files are\n  package data; `specmgr docs` regeneration covers Task 5.2's docstring\n  changes), then `git diff --exit-code -- docs/` zero drift; add a dated\n  entry to the Recent Updates section, update Current Status, flip the\n  phase's task lines to done in place — depends on: Task 5.3 — status: not-\n  started\n\n#### Phase 6: Cross-cutting documentation and release notes\n\n- [ ] Task 6.1: Update `AGENTS.md`: the seven per-domain bullets — remove\n  `update_<d>`/`set_status_<d>` from each tool enumeration and note that\n  whole-body/line-range updates go through the generic `update` tool and\n  status changes through the generic `set_status` tool (both in\n  `general/tools/`); the ADR bullet — remove `set_status` from its 12-wrapper\n  enumeration (11 remain); the `general/` bullet — add `update` (7-type;\n  optional `begin`/`end` range with the `N+1` sentinel) and `set_status`\n  (8-type; ADR-only `superseded_by`), and note the `raw` parameter on the\n  seven `get_<d>` tools; the \"Still genuinely missing / not yet done\" list —\n  add the convention note that future domains (e.g. `ac`) add one dispatch\n  entry to the two generic tools (plus a `raw` getter parameter) instead of\n  new `update_<d>`/`set_status_<d>` tools, citing the Phase-1 ADR id —\n  depends on: Phase 5 complete — status: not-started\n- [ ] Task 6.2: Update `CHANGELOG.md`'s `[Unreleased]` section: **Breaking** —\n  removed 14 MCP tools (`update_req`, `update_uc`, `update_tsk`,\n  `update_qa`, `update_prb`, `update_gol`, `update_rsk`, `set_status_req`,\n  `set_status_uc`, `set_status_tsk`, `set_status_qa`, `set_status_prb`,\n  `set_status_gol`, `set_status_rsk`) and ADR `set_status`'s signature\n  changes from `(id, status, superseded_by)` to `(id, type, status,\n  superseded_by)` with `type=\"adr\"` now required; **Added** — generic\n  `update(id, type, content, begin, end)` (7 types; optional 1-based\n  inclusive body-line range, `N+1` EOF sentinel, splice-then-validate-whole)\n  and generic `set_status(id, type, status, superseded_by)` (8 types);\n  optional `raw: bool = False` on the seven `get_<d>` tools (returns the\n  frontmatter-stripped body text verbatim — the text `begin`/`end` index\n  into); cite the Phase-1 ADR id — depends on: Phase 5 complete — status:\n  not-started\n- [ ] Task 6.3: Final regeneration: `uv run --frozen specmgr docs`, `uv run\n  --frozen specmgr mcp-docs`, `uv run --frozen specmgr adr-toc`, `uv run\n  --frozen specmgr schema` (models are untouched — expect no schema\n  changes); confirm `git diff --exit-code -- docs/` exits zero — depends on:\n  Task 6.1, Task 6.2 — status: not-started\n- [ ] Task 6.4: Phase-end quality gate — full gate; add a dated entry to the\n  Recent Updates section, update Current Status, flip the phase's task lines\n  to done in place — depends on: Task 6.3 — status: not-started\n\n#### Phase 7: Final cross-cutting verification\n\n- [ ] Task 7.1: Walk ACC-001…ACC-008 and confirm each with concrete evidence,\n  annotating the Acceptance Criteria section inline in the style of\n  feat-18-goal: live, un-mocked end-to-end in a temporary\n  `SPECMGR_DOCS_DIR` — for `req`, `rsk`, and `uc`: `create_<d>` →\n  `get_<d>(id, raw=True)` → `update(id, type, content, begin, end)` (one\n  middle-range replace verified byte-exact, one `N+1` append) → `get_<d>`\n  (content verified) → `set_status(id, type, status)` (domain-valid value\n  from the Design-Notes table) → `get_<d>` (status verified); for ADR:\n  `create_adr` → `set_status(id, type=\"adr\", status=\"superseded\",\n  superseded_by=…)` → status reads `\"superseded by …\"`; confirm\n  `asyncio.run(mcp.list_tools()/list_resources()/list_prompts())` on the\n  real `server.mcp` instance reports 71 tools / 25 resources / 19 prompts;\n  fresh-subprocess import check; full quality gate (ruff format/check, pylint\n  advisory, vulture, unittest, `specmgr docs`/`mcp-docs`/`adr-toc`/`schema`\n  zero drift); remove the temporary docs directory and confirm `git status`\n  shows no residue — depends on: Phases 1–6 complete — status: not-started\n- [ ] Task 7.2: Set this README's frontmatter `status: in-progress` →\n  `status: done`; final Recent Updates entry and Current Status summary —\n  depends on: Task 7.1 — status: not-started\n\n**Note:** If a task's scope changes mid-flight, edit its description in\nplace; rely on git history (`git log -p` on this file) to recover what was\noriginally planned, rather than keeping a second copy of the task around.\n\n## Progress\n\n### Current Status\n\n**As of 2026-08-26**: Planned. This README was drafted in the planning\nsession (all decisions in \"Decisions Made\" below are locked); all seven\nphases are not started. Execution is handed to the phase-orchestrator via\n`/implement-feature feat-0-consolidate-mutation-tools` (one phase-\nimplementer per phase, one Conventional Commit per accepted phase).\n\n### Blockers\n\nNone.\n\n### Recent Updates\n\n#### Update 2026-08-26 (planning session)\n\n- Completed: Feature planned end to end with the user. Design locked:\n  generic `update(id, type, content, begin, end)` for the seven whole-body\n  domains (line-range contract with the `N+1` EOF sentinel, splice-then-\n  validate-whole), generic `set_status(id, type, status, superseded_by)` for\n  all eight domains (ADR-only `superseded_by`), `get_<d>(raw=True)` body-text\n  read, outright deletion of the 15 superseded tools, per-domain prompts\n  kept with rewritten narration, and a short ADR (Phase 1).\n- Next: Phase 1 (ADR) via `/implement-feature feat-0-consolidate-mutation-\n  tools`.\n- Notes: Phase 4 is deliberately atomic (add generic `set_status` + delete\n  all eight old status tools) because ADR's existing tool already occupies\n  the `set_status` name. Target end state: 71 tools / 25 resources / 19\n  prompts (from 84/25/19).\n\n### Decisions Made\n\n- **2026-08-26**: Explicit `type` parameter on both generic tools rather\n  than bare-uuid resolution — per-domain v4 UUIDs are not *guaranteed*\n  unique, uuid-only would force an all-domains directory scan (parsing every\n  file) on the write path with cost growing per domain, and the calling\n  client always already knows the domain.\n- **2026-08-26**: ADR is excluded from `update` (its section-level MADR\n  contract — `update_frontmatter`/`update_section`/`option_*` — has no\n  whole-body replace by design) but included in `set_status` with the\n  `superseded_by` special case.\n- **2026-08-26**: The 15 superseded tools are deleted outright — no\n  deprecated wrapper release; the package is 0.x and the MCP tool list is\n  the only contract (breaking change recorded in `CHANGELOG.md`).\n- **2026-08-26**: The per-domain `update_*` prompts are kept (domain-\n  tailored interview guidance) and their narration text rewritten to the\n  generic tools — rather than consolidating seven near-duplicate prompts\n  into one generic prompt and losing domain-specific section names.\n- **2026-08-26**: The decision is recorded as a short ADR (Phase 1) rather\n  than README-only — it fixes a repo-wide convention future domains must\n  follow (per AGENTS.md's \"when in doubt, write the ADR\").\n- **2026-08-26**: `update` gains optional 1-based, inclusive `begin`/`end`\n  body-line coordinates with an `N+1` EOF sentinel (append/through-EOF); the\n  spliced result is always validated as a whole document before writing, and\n  unchanged regions stay byte-identical to disk (user request: smaller,\n  faster, safer targeted updates).\n- **2026-08-26**: Line numbers are served by `get_<d>(raw=True)` (shared\n  body-extraction helper with the splice) rather than re-introducing\n  `specmgr://<d>/{id}` resources — ADR ddfb1109's empirical finding that\n  agents invoke tools more reliably than parameterized resources, plus the\n  maintenance cost of seven new resource templates, decided it.\n\n### Related PRs / Commits\n\nNone yet (one Conventional Commit per accepted phase, created by the phase-\norchestrator with user confirmation).\n",
  "filePath": "/home/user/src/biz.dfch.SpecMgr/.specmgr/feat/feat-0-consolidate-mutation-tools/README.md"
}
```

**Output:**

```
Wrote file successfully.
```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 58.8s)

_Thinking:_

Now let's verify the final state:

1. git status should show only the new untracked feature directory (feat-18 has been reverted).
2. Sanity check of the README: verify that frontmatter parses correctly (a simple check), and that the structure is complete.

Let's run git status and do a simple structural check (sections present, task count, phase count).

Verifying the final state of the working tree and the README structure:

**Tool: bash**

**Input:**

```json
{
  "command": "git status --short; echo ===; grep -c \"^- \\[ \\] Task\" .specmgr/feat/feat-0-consolidate-mutation-tools/README.md; grep -n \"^#### Phase\\|^### \\|^## \" .specmgr/feat/feat-0-consolidate-mutation-tools/README.md; echo ===; uv run --frozen python -c \"\nimport frontmatter\np = frontmatter.load('.specmgr/feat/feat-0-consolidate-mutation-tools/README.md')\nprint(dict(p.metadata))\n\""
}
```

**Output:**

```
?? .specmgr/feat/feat-0-consolidate-mutation-tools/
===
35
11:## Plan
13:### Overview
43:### Requirements
128:### Acceptance Criteria
193:### Scope
230:### Dependencies
251:### Design Notes
393:### Related ADRs
414:### Task List
421:#### Phase 1: ADR
456:#### Phase 2: Generic `update` tool + `raw` read parameter
537:#### Phase 3: Retire the per-domain `update_*` tools
572:#### Phase 4: Generic `set_status` + retire the eight old status tools
635:#### Phase 5: Narration rewrite (prompts + instruction data)
684:#### Phase 6: Cross-cutting documentation and release notes
722:#### Phase 7: Final cross-cutting verification
748:## Progress
750:### Current Status
758:### Blockers
762:### Recent Updates
780:### Decisions Made
812:### Related PRs / Commits
===
{'created': datetime.date(2026, 8, 26), 'id': 'feat-0-consolidate-mutation-tools', 'status': 'planning', 'updated': datetime.date(2026, 8, 26), 'version': '1.0.0'}

```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 68.2s)

_Thinking:_

All confirmed:

- Working tree: only the new untracked feature directory (feat-18 has been completely reverted — no other changes).
- README: 35 tasks across 7 phases, all sections of the template are present, front matter parses correctly with the proper 5 fields.

Step 0 complete. Next is the handoff: the user runs `/implement-feature feat-0-consolidate-mutation-tools`.

Note: this file is untracked. Per the repo convention, feature folders are committed to git (AGENTS.md: "The .specmgr/ folder ... is committed to git like any other tracked path"). Commits are managed by the orchestrator per phase with user confirmation, and Step 0 was my responsibility — should I commit the README? The rule: "Never commit changes unless the user explicitly requests it." The user hasn't explicitly requested a commit. The orchestrator commits per phase. The README will presumably be included in the Phase 1 commit (or the user might commit it separately). Leave it uncommitted and mention it briefly.

Keep the reply concise: Step 0 complete, verified, handoff command, note on the uncommitted state.

Step 0 is complete.

**Created:** `.specmgr/feat/feat-0-consolidate-mutation-tools/README.md`

- Full plan: REQ-001…007, ACC-001…008, scope, dependencies, design notes (dispatch architecture, the precise `begin`/`end` range contract with the `N+1` sentinel, the raw/splice shared-helper invariant, the `set_status` name-collision constraint, per-domain status vocabularies, import-order analysis)
- **7 phases / 35 tasks**, each phase ending with its full quality-gate task + a dated **Recent Updates** entry
- All planning decisions logged in "Decisions Made" (incl. the raw-read-over-`/{id}`-resources decision per ADR ddfb1109)
- Frontmatter validated: `id: feat-0-consolidate-mutation-tools`, `status: planning`
- Working tree is clean apart from the new feature folder (an accidental `mdformat` pass on the existing feat-18 README was fully reverted)

The README is left **uncommitted** — the phase-orchestrator owns per-phase Conventional Commits (Phase 1's commit will pick it up, or you can commit it separately first).

**Hand-off:** run

```
/implement-feature feat-0-consolidate-mutation-tools
```

The phase-orchestrator will then drive Phases 1–7 — one fresh phase-implementer per phase, independent gate re-verification, one commit per phase with your confirmation, and any blocker or ambiguity surfaced to you directly.

---

## User

create a gh issue and use the overview of the feature as the description of the issue. Use the issue id of the issue that you created and rename the feat-0-consolidate... folder to use the new session id (instead of "0"). Update all locations that still reference the old name.

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 84.2s)

_Thinking:_

User's requests:

1. Create a GitHub issue, and use the feature overview as the issue description.
2. Rename the folder `feat-0-consolidate-mutation-tools` to `feat-NNN-consolidate-mutation-tools` using the new issue number.
3. Update all references to the old name.

Let's start by creating the GitHub issue first. I'll use `gh issue create`. For the body, I'll use the Overview section of the README.

First, let me check whether `gh` is available and what the repository is.

Next, the rename:

- Folder: `.specmgr/feat/feat-0-consolidate-mutation-tools` → `.specmgr/feat/feat-NNN-consolidate-mutation-tools`
- Front matter `id: feat-0-consolidate-mutation-tools` → new name
- Places within the README that reference the old name:
  - The `/implement-feature feat-0-consolidate-mutation-tools` line in Current Status
  - The "Next: Phase 1 (ADR) via `/implement-feature feat-0-consolidate-mutation-tools`" in Recent Updates
  - The title of "#### Update 2026-08-26 (planning session)"? No reference to the name there.
  - The Overview? Let me check — I don't think the Overview mentions the folder name. I'll verify with grep.
- Any other files that reference `feat-0-consolidate`? The previous message I sent to the user had it, but that's not a file. Let me grep the repo.

I'll run the following:

1. `gh auth status` / `gh repo view` to confirm remote.
2. Create the issue with a title and the overview body.
3. Get the issue number.
4. Rename the folder with `git mv`? The folder is untracked, so a regular `mv` is fine (git doesn't track untracked directories, so `git mv` won't work… actually, the files inside are untracked, so `mv` is correct).
5. Update the front matter + references with sed or the edit tool.
6. Verify with grep that no `feat-0` references remain (note: the `feat-0` pattern could match other things… the slug is unique: `feat-0-consolidate-mutation-tools`).

Title for the issue: something like "Consolidate update and set_status tools into generic type-dispatched tools". Description: the Overview section of the README.

Let me extract the overview text (lines 13–41 of the README, up to "### Requirements"). I'll build the body from that section.

Let's proceed step by step. First, check gh and the repo.

**Tool: bash**

**Input:**

```json
{
  "command": "gh auth status 2>&1 | head -5; gh repo view --json nameWithOwner -q .nameWithOwner 2>&1"
}
```

**Output:**

```
github.com
  ✓ Logged in to github.com account dfch (keyring)
  - Active account: true
  - Git operations protocol: https
  - Token: gho_************************************
dfch/biz.dfch.SpecMgr

```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 60.5s)

_Thinking:_

Authenticated. Next, create an issue. The body of the issue should be the Overview section of the README. Let me extract it precisely — from "### Overview" (line 13) to just before "### Requirements" (line 43). In other words, lines 15 through 41 (the body of the overview paragraph). To avoid transcription errors, I'll grab it with sed and write it out to a temp file.

Title: "Consolidate update and set_status tools into generic type-dispatched tools"

Authenticated as `dfch` on `dfch/biz.dfch.SpecMgr`. Creating the issue with the README's Overview as its description:

**Tool: bash**

**Input:**

```json
{
  "command": "sed -n '/^### Overview$/,/^### Requirements$/p' .specmgr/feat/feat-0-consolidate-mutation-tools/README.md | sed '1d;$d' > /tmp/opencode/issue-body.md && wc -l /tmp/opencode/issue-body.md && head -8 /tmp/opencode/issue-body.md"
}
```

**Output:**

```
29 /tmp/opencode/issue-body.md

Replace the 15 near-duplicate per-domain mutation MCP tools with two generic,
cross-cutting tools that live in `general/tools/`: `update(id, type, content,
begin, end)` for whole-body (and now line-range) document replacement across
the seven whole-body domains (`req`, `uc`, `tsk`, `qa`, `prb`, `gol`, `rsk`),
and `set_status(id, type, status, superseded_by)` for status changes across
all eight domains including `adr`. The per-domain tools
(`update_req`/`update_uc`/`update_tsk`/`update_qa`/`update_prb`/`update_gol`/

```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 58.3s)

_Thinking:_

The overview paragraph contains the text "**71 tools / 25 resources / 19 prompts** (currently 84/25/19: −15 +2)", which references the internal target state — that's fine as the issue description (it's part of the overview).

Alright, let's create the issue.

**Tool: bash**

**Input:**

```json
{
  "command": "gh issue create --title \"Consolidate update and set_status tools into generic type-dispatched tools\" --body-file /tmp/opencode/issue-body.md"
}
```

**Output:**

```
https://github.com/dfch/biz.dfch.SpecMgr/issues/22

```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 64.2s)

_Thinking:_

Issue #22 has been created: https://github.com/dfch/biz.dfch.SpecMgr/issues/22

Next, rename the folder `feat-0-consolidate-mutation-tools` → `feat-22-consolidate-mutation-tools` and update all references to the old name.

Steps:

1. `mv .specmgr/feat/feat-0-consolidate-mutation-tools .specmgr/feat/feat-22-consolidate-mutation-tools`
2. Update references within the README:
   - Front matter: `id: feat-0-consolidate-mutation-tools` → `id: feat-22-consolidate-mutation-tools`
   - Current Status: `/implement-feature feat-0-consolidate-mutation-tools` → new
   - Recent Updates Next line: `/implement-feature feat-0-consolidate-mutation-tools` → new
3. Grep the entire repo for `feat-0-consolidate` and catch anything else (AGENTS.md? other feature READMEs? .gitignore?).
4. Should I also update the `updated` date in the front matter? Today is 2026-08-26, same date — no change needed.

First, let me grep to confirm all references.

Issue #22 created. Now finding every reference to the old name, then renaming:

**Tool: bash**

**Input:**

```json
{
  "command": "grep -rn \"feat-0-consolidate\" . --include=\"*\" 2>/dev/null | grep -v \"^\\./\\.git/\" | grep -v \"feat-0-consolidate-mutation-tools/README.md:\" ; echo === in README:; grep -n \"feat-0-consolidate\" .specmgr/feat/feat-0-consolidate-mutation-tools/README.md"
}
```

**Output:**

```
=== in README:
3:id: feat-0-consolidate-mutation-tools
755:`/implement-feature feat-0-consolidate-mutation-tools` (one phase-
773:- Next: Phase 1 (ADR) via `/implement-feature feat-0-consolidate-mutation-

```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 101.8s)

_Thinking:_

There are only 3 references, all inside the README. No references elsewhere in the repository (AGENTS.md doesn't list feature folders per-feature — the "existing feature folders" paragraph only lists feat-9, feat-4, and feat-5).

So next:

1. Rename the folder with `mv`.
2. Update the 3 lines inside the README (since the oldString is unique, use the edit tool. Or `sed -i` against the new path would also work — 3 places, a simple string replacement of `feat-0-consolidate-mutation-tools` → `feat-22-consolidate-mutation-tools`. Note that line 773 has a line-wrapped split: "feat-0-consolidate-mutation-" + newline + "tools". A simple `sed` string replacement of `feat-0-consolidate-mutation-tools` won't match the wrapped one. Line 773: "via `/implement-feature feat-0-consolidate-mutation-`, and line 774 continues with `tools`." Let me check the exact text.

Lines 773–774:

```
- Next: Phase 1 (ADR) via `/implement-feature feat-0-consolidate-mutation-
  tools`.
```

So the replacement target for that line is `feat-0-consolidate-mutation-` → `feat-22-consolidate-mutation-`.

If I replace all occurrences of `feat-0-consolidate-mutation` with `feat-22-consolidate-mutation` (the prefix without the trailing `-tools`), I can handle all 3 cases including the wrapped one. Let me run `sed -i 's/feat-0-consolidate-mutation/feat-22-consolidate-mutation/g'` against the README, and then rename the folder.

Wait — first rename the folder, then run `sed` against the new path. Either order is fine. `mv` first, then `sed`.

Should I also update the frontmatter's `updated` date? Per convention: "`updated` is bumped on every substantive edit." This is a rename/ID change, which counts as a substantive edit, but the date is the same (2026-08-26), so no visible change is needed.

Also: the "planning session" Recent Updates entry and Current Status mention the id — the `sed` replacement handles those.

After that, verify: grep for `feat-0-consolidate` (should return nothing), and confirm the new name is present.

Only 3 references, all inside the README. Renaming the folder and updating all occurrences (including the line-wrapped one):

**Tool: bash**

**Input:**

```json
{
  "command": "mv .specmgr/feat/feat-0-consolidate-mutation-tools .specmgr/feat/feat-22-consolidate-mutation-tools && sed -i 's/feat-0-consolidate-mutation/feat-22-consolidate-mutation/g' .specmgr/feat/feat-22-consolidate-mutation-tools/README.md && echo \"--- remaining old refs (want none):\" && grep -rn \"feat-0-consolidate\" . 2>/dev/null | grep -v \"^\\./\\.git/\" | wc -l && echo \"--- new refs:\" && grep -n \"feat-22-consolidate\" .specmgr/feat/feat-22-consolidate-mutation-tools/README.md"
}
```

**Output:**

```
--- remaining old refs (want none):
0
--- new refs:
3:id: feat-22-consolidate-mutation-tools
755:`/implement-feature feat-22-consolidate-mutation-tools` (one phase-
773:- Next: Phase 1 (ADR) via `/implement-feature feat-22-consolidate-mutation-

```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 60.6s)

_Thinking:_

Rename and update complete. Final check: verify that the frontmatter still parses correctly, and that the feature ID convention matches the folder name (the ADR states that the `id` in the frontmatter is the folder name itself — and indeed that's how it is now).

Also, let me confirm that the issue body matches the overview, and check the final git status.

Final verification — frontmatter parses and matches the folder name, issue looks right:

**Tool: bash**

**Input:**

```json
{
  "command": "uv run --frozen python -c \"\nimport frontmatter\np = frontmatter.load('.specmgr/feat/feat-22-consolidate-mutation-tools/README.md')\nprint(p.metadata['id'], '|', p.metadata['status'])\n\" && git status --short && gh issue view 22 --json title,url -q '\"\\(.title) — \\(.url)\"'"
}
```

**Output:**

```
feat-22-consolidate-mutation-tools | planning
?? .specmgr/feat/feat-22-consolidate-mutation-tools/
Consolidate update and set_status tools into generic type-dispatched tools — https://github.com/dfch/biz.dfch.SpecMgr/issues/22

```

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 62.1s)

_Thinking:_

All done:

1. Created Issue #22 at https://github.com/dfch/biz.dfch.SpecMgr/issues/22, and the Overview from the README is the body.
2. Renamed the folder to `feat-22-consolidate-mutation-tools`.
3. Updated all references (3 places: frontmatter id, Current Status, Recent Updates) — 0 old references remain.
4. The frontmatter id matches the folder name (as per the ADR e369ee2e convention).

The handoff command has been changed accordingly. Keep the reply concise.

Done.

- **Issue:** https://github.com/dfch/biz.dfch.SpecMgr/issues/22 — body is the README's Overview section verbatim.
- **Folder renamed:** `.specmgr/feat/feat-22-consolidate-mutation-tools/` (frontmatter `id` updated to match, per the `feat-NNN-slug` convention — the `NNN` infix now carries issue #22).
- **References:** all 3 occurrences in the README updated, zero old-name references remain anywhere in the repo.

Hand-off is now:

```
/implement-feature feat-22-consolidate-mutation-tools
```

---

## User

---

## Assistant (Build · qwen3.8-27b-bf16-896k · 0.1s)

**Tool: bash**

**Input:**

```json
{
  "command": "git status"
}
```

**Output:**

```
On branch dev
Your branch is up to date with 'origin/dev'.

nothing to commit, working tree clean

```

---
