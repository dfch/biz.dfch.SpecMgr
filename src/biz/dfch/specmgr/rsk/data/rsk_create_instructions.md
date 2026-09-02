You are drafting a new Risk (RSK) document about: $topic

Follow this structure and tool sequence exactly. Do not write raw
markdown yourself beyond the body content you pass to `create_rsk` --
every write to disk goes through the specmgr MCP tools listed below.
There is no frontmatter for you to draft: `create_rsk` builds
id/type/status/created/updated/version automatically.

Make a todo list and use the question tool.

## 0. Check for an existing risk on this topic first
Call the `list_rsk` tool before creating anything. If a risk with a
similar title or scenario already exists, tell the user about it and
ask whether they want to revise that one (via the `update_risk` prompt)
instead of creating a duplicate. Only proceed to step 1 if this is
genuinely a new risk.

## 1. Structure recap (body markdown only, no frontmatter block)
- `# {title}` -- H1, mandatory, free-form.
- `<!-- optional leading comment -->` -- optional HTML comment right
  after the H1, giving context for the risk as a whole.
- `## Cause` -- mandatory prose: why the risk exists (the root
  condition).
- `## Trigger` -- mandatory prose: what sets the risk event in motion.
- `## Consequence` -- mandatory prose: what happens if the risk event
  occurs.
- `## Scope` -- mandatory bullet list of affected systems/components;
  at least one item.
- `## Initial Assessment` -- mandatory 5x5 assessment BEFORE
  mitigation: exactly two H3 headings, the value in the heading
  itself, `### Probability {1..5}` first, then `### Impact {1..5}`.
  A missing value, an out-of-range value, or a swapped order fails
  validation.
- `## Strategy` -- mandatory single-line TARA word: exactly one of
  transfer, accept, reduce, avoid (lowercase).
- `## Mitigation` -- mandatory prose: the treatment measures bridging
  the two assessments (`none` if the strategy is accept).
- `## Residual Assessment` -- mandatory 5x5 assessment AFTER
  mitigation, same shape as the initial one.
- `## Owner` -- optional single-line value: the responsible
  person/role.
- `## Tags` -- optional bullet list of free-form labels.
- `## More Information` -- optional free-form supplementary text.

## 2. Gather information before calling any tool
Elicit (asking the user if not already given): the cause, trigger and
consequence of the risk, the affected systems, the initial and
residual 5x5 coordinates, and the chosen TARA strategy with its
mitigation measures, and optionally owner, tags, and more information.

## 3. Use the template/example/schema and the domain knowledge as references
Fetch `specmgr://rsk/template` or `specmgr://rsk/example` as a
starting point/style reference, then check `specmgr://rsk/schema`
(the generated JSON Schema) to confirm field names and constraints
before drafting the body. Do not invent field names or section
headings that are not present there. For what TARA means and when to
pick each of the four strategies, read `specmgr://rsk/tara`; for what
'high risk' and 'low risk' mean (the 5x5 zone table and the product
thresholds), read `specmgr://rsk/risk-matrix`.

## 4. Tool call sequence
1. Draft the body-only markdown per the structure above.
2. Call `create_rsk(content)` -- `content` is body markdown only; the
   entire frontmatter is built automatically. A structural or field
   validation failure raises uncaught and nothing is written.
3. Optionally call `validate_rsk(content, full=False)` first if you
   want to dry-run the body without writing anything -- `create_rsk`
   already performs the same validation internally, so this step is
   never required, only a convenience.

## 5. Later revisions
Any later change to this risk should go through the `update_risk`
prompt (or directly through the generic `update(id, type="rsk", content)`,
`set_status(id, type="rsk", status)`, and
`set_classification(id, type="rsk", classification)` tools), not by
re-running this prompt.
