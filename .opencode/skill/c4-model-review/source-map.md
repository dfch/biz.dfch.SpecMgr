# Source map

Every adapted passage of this skill, mapped to its source file at the
pinned commit. A passage marked "ideas only" copies no text and therefore
carries no attribution line — the notice and this map stay consistent:
adapted text exists in exactly the three files `NOTICE.md` lists.

Sources:

- `jrjsmrtn/c4-skills` @ `e86d8a91d3ed793cdf6c035f01d19f1b18cc8b6b`
  (MIT, "Copyright (c) 2026 Georges Martin"); source path
  `skills/c4-review/SKILL.md` (single-file skill).

## `SKILL.md` — ideas only

| Passage | Source | Notes |
|---|---|---|
| The trigger description + the intro's read-only hook | — | Ideas only: the single-task review framing ("reviewing an existing C4 model ... for quality", "This skill is read-only: it reports findings and never edits the model"), the five trigger phrases, and the routing to the `structurizr-dsl-authoring` / `structurizr-validate-loop` skills are this repo's (REQ-005/REQ-007); no source text |
| "The workflow" (read → MCP check → walk checklists → report) | upstream "Workflow" Phases 1–2 (structure) | Ideas only: the phase structure is the upstream's; every step is rewritten — the Docker-CLI `validate`/`inspect` invocations are replaced by the MCP tools (the locked removals), "if validation fails, fix syntax errors first" is replaced by the read-only first-finding rule, and Phase 3–8 are replaced by the three reference checklists; the efficiency note ("read it once, completely", "call each tool once; do not re-run a tool over text that has not changed") is this repo's (the proof data showed baseline trials burning the full 1200 s budget on repeated reads/exports) |
| "The report format" (context line, one bullet per finding, Error/Warning/Suggestion, closing line, name-everything rule, no-padding rule, no-own-opinion rule, no-view-element-listing rule) | upstream "Output Format" | Ideas only: the Error/Warning/Suggestion categorization and the "positive observations" idea are the upstream's; the bullet shape, the name-everything rule, the no-padding rule and the no-own-opinion rule ("judge this model, not a different one") are this repo's (REQ-005's report deliverable; the proof data showed baselines failing their own reviews by padding the list with generic advice and design opinions on clean elements); the no-view-element-listing rule ("name the view and give the element count — do not list the elements") is this repo's iteration-2 fix (iteration-1 skill trials reported the crowded view correctly but enumerated the pulled-in elements in the finding line, naming clean elements) |
| "The MCP limits" | the spike's Finding 3 (the MCP's surface) + upstream Phase 1/2 (the refused directives) | Ideas only: the no-image-rendering rule and the single-file rule are this repo's (REQ-006 — the limits this skill depends on); the `!include`/`!docs`/`!adrs` refusal and the "documentation/decisions findings are expected under the MCP limits" note are the pinned MCP's observed behaviour |
| "When the MCP is absent" | — | Ideas only: REQ-011 (the review can still read the DSL text and walk the checklists — model structure, not tool output; the MCP-based checking is not; never described as validated/parse-checked/export-checked) |

No passage in `SKILL.md` copies text; it has no attribution line in
`NOTICE.md`.

## `references/element-checklist.md`

| Passage | Source | Adaptation |
|---|---|---|
| "People / actors" checklist (4 items) | upstream "Phase 3" "People/Actors" | near-verbatim (item wording kept; the review categorization added) |
| "Software systems" checklist (5 items) | upstream "Phase 3" "Software Systems" | adapted: the "tagged External" item gains the third-party-must-be-top-level + Warning phrasing (the pinned DSL's observed shape, the Phase 130 precedent) and the do-not-flag-a-tagged-element rule (the pinned DSL has no `externalSystem` keyword — a tagged top-level `element` is the sanctioned shape; the proof data showed baselines flagging correctly tagged elements for "not being a softwareSystem"); the other items near-verbatim |
| "Containers" checklist (6 items) | upstream "Phase 3" "Containers" | adapted: the "No libraries, modules, or packages modeled as containers" item gains the code-level explanation and the Error categorization; the "Technology Soup" definition is folded into the description item (its own anti-pattern section is dropped here — no Elixir examples) |
| "Components (if present)" checklist (4 items) | upstream "Phase 3" "Components" | adapted: the "Code Structure Mirror" and "Stale Component Diagram" anti-pattern definitions are folded in |
| "Completeness" checklist (5 items) | upstream "Phase 7: Completeness Check" | adapted: the "No orphaned elements (elements with no relationships)" item is kept near-verbatim and gains the MCP `inspect` disconnected/noview facts (observed) + the Warning categorization; the "users/personas", "external integrations" and "Relationships cover all known communication paths" items are replaced by the description-contradiction-only rule (a read-only review has no external ground truth for "known paths" — the proof data showed baselines inventing missing edges on clean elements); the "Missing Middle" definition is folded into the views item; the deployment-related completeness items are dropped |
| "Anti-patterns worth flagging" (Docker Confusion, Technology Soup) | upstream "Common Anti-Patterns" | adapted: the two model-level anti-patterns kept with their definitions near-verbatim; the review framing added |

## `references/relationship-checklist.md`

| Passage | Source | Adaptation |
|---|---|---|
| "Labels" checklist (3 items) | upstream "Phase 4" "Labels" | near-verbatim; the vague-label item gains the Warning categorization and the name-the-elements reporting rule |
| The vague-label table (Uses / Connects to / Interacts with / Communicates with) | upstream "Phase 4" "Suggest specific alternatives" table | near-verbatim (no change) |
| "Technology" checklist (3 items) | upstream "Phase 4" "Technology" | near-verbatim (no change) |
| "Direction" checklist (3 items) | upstream "Phase 4" "Direction" | near-verbatim (no change) |

## `references/view-checklist.md`

| Passage | Source | Adaptation |
|---|---|---|
| "Existence and scope" checklist (5 items) | upstream "Phase 5: View Review" (system context / container / component / dynamic / deployment) | adapted: the per-kind criteria kept, the `include *` advice (upstream says a context view "uses `include *` or explicitly includes all relevant elements") is dropped — the size criteria below contradict it for large models (this repo's spike Finding 8) |
| "Keys and size" checklist (3 items) | this repo's (the spike's Finding 8 + the pinned CLI's observed `views.view.key` finding) + upstream "Phase 5" structure | Ideas only + observed: the explicit-key rule and the about-20-element bound are the `c4-view-design` skill's locked rules (REQ-004) restated as review criteria; the `Container-001`/`views.view.key` facts are the pinned CLI's observed output (verified at Task 150.100); the split is delegated to the `c4-view-design` skill; the "do not list the elements themselves" wording is this repo's iteration-2 fix (the SKILL.md report-format counterpart) |
| "Content" checklist (2 items) | upstream "Phase 5" (per-kind content criteria) | adapted: the "no mixed abstraction levels" and "everything it shows is labelled" ideas, restated |

## Dropped upstream content (no local passage)

- The upstream frontmatter's `metadata`/`license` fields (this skill's
  frontmatter is exactly `name` + `description`).
- "When to Use" and "Required Inputs" (the trigger surface is the
  frontmatter `description`; the input is the workspace file the user
  names).
- "Phase 1: Syntax Validation" and "Phase 2: Workspace Inspection" in their
  Docker-CLI form (`$RUNTIME`/podman/container/`wslc`, the pinned dated
  image `structurizr/structurizr:2026.09.19`, the mount-the-project-root
  advice, the "fix syntax errors first" instruction) — the locked removals:
  replaced by the MCP `parse`/`validate`/`inspect` workflow and the
  read-only first-finding rule.
- "Phase 6: Style Review" (shape Person / shape Cylinder / colours /
  colour blindness) — visual criteria the MCP cannot verify (no image
  rendering; the review is over model structure, never a rendered picture),
  and the styles mechanics belong to the `structurizr-dsl-authoring` skill.
- "Phase 8: Structural Issues" — the `!adrs`/`!docs` items (the MCP refuses
  them — the locked removals), `!identifiers hierarchical` and identifier
  naming (the `structurizr-dsl-authoring` skill's task), tags/groups
  organization (the element checklists cover tags where they matter).
- "Common Anti-Patterns": "The 'Everything Uses Everything' Model" (folded
  into the relationship vague-label item), "The 'Missing Middle'" (folded
  into the completeness item), "The 'Stale Component Diagram'" (folded into
  the components item), "The 'Technology Soup'" (folded into the containers
  item), "The 'Docker Confusion'" (kept in the element anti-patterns), and
  the Elixir-specific "The 'GenServer Container'", "The 'Supervision Tree
  Diagram'" and "The 'Umbrella = Microservices' Model" (the locked removals).
- The entire "Erlang/Elixir/OTP Review Checklist" section (the locked
  removals).
- "Validation" (the review-completion criteria in the upstream's
  fix-forward sense — the "fix every error" half is the read-only
  skill's antithesis); the completion rule is restated in "The report
  format".
- "Related Skills" (points at the upstream's own `c4-model`/
  `structurizr-dsl`/`c4-deployment` skills; this skill routes to this repo's
  own skills in `SKILL.md` instead).
