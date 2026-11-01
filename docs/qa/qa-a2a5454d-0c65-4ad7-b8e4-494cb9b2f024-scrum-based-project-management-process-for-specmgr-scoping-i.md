---
classification: null
created: '2026-10-07T20:51:12.948+02:00'
id: a2a5454d-0c65-4ad7-b8e4-494cb9b2f024
status: draft
type: qa
updated: '2026-10-08T21:40:54.613+02:00'
version: 1.0.0
---

# Scrum-Based Project Management Process for specmgr — Scoping Interview

## General

### Introduction

This is round 1 of a non-interactive, single-respondent scoping interview for
a Scrum-based project-management process layered on top of specmgr. The goal
is to have an agent available for every Scrum accountability/role, while
guaranteeing that every one of those roles remains fully executable by an
actual human alone — nothing in the process may require AI-agent
participation. All questions below are open for a first answer pass in one
sitting; there was no live interview session.

### Raw Requirements

Prior to this interview, the following request existed verbatim: "We want
to implement a project management process, that is based on scrum. The
aim would be, to have agents for all the scrum roles and also the skills and
commands for it. but it must be possible that all the roles are filled by
actual humans also. so nothing that only AI agents could do."

## Elicitation Context

<!-- Scoping/meta questions establishing the shape of this effort before any ceremony/role detail is designed. -->

> **0.0010**: Should this Scrum layer be built purely from *existing*
> specmgr domains plus new `.opencode` agents/skills/commands (no new
> document schema at all), or should it introduce one or more brand-new
> specmgr document types?
>
> - Option A (reuse-only): Product Goal -> `gol`; Product Backlog Item ->
>   `req`/`uc`; Sprint Backlog -> `tsk` (using the existing Phase/Task
>   numbering scheme); Definition-of-Done verification -> `vcr`;
>   impediments/risks -> `rsk`; retrospective outcomes -> `dec`; refinement
>   interviews -> `qa`. Scrum ceremonies and roles become pure orchestration
>   (agents/skills/commands) with no new persisted schema.
> - Option B (new domain(s)): same reuse as A, but add a dedicated `sprint`
>   (and/or `backlog`) domain to represent sprint boundaries (start/end
>   dates, sprint goal, committed items, burndown) as first-class,
>   queryable documents instead of inferring them from `tsk`/`feat`
>   metadata.
> - Option C (hybrid/staged): start with Option A to validate the workflow
>   end to end, and only add a dedicated schema later once a concrete gap is
>   found in practice.

!!! I want to start with option c. But what about the estimates of how long a certain task will take. This is part of scrum. How would that be implemented and how would an agent estimate how "long" it would take him?

> **0.0015**: Follow-up on estimation: Scrum traditionally sizes Product
> Backlog Items with *relative* effort (story points on a Fibonacci-like
> scale, or T-shirt sizes) rather than absolute hours/days, precisely
> because relative sizing is faster to agree on and more stable across
> different people (or agents) than wall-clock-time guesses. Proposed
> approach for an agent "estimating how long it would take": an
> agent-Developer sizes a PBI the same way a human would — by relative
> comparison against already-completed, similarly-scoped past items (its
> own prior `tsk` task breakdowns) and against the PBI's likely number of
> Phase/Task entries once decomposed via the `feat-numbering` scheme — never
> by reasoning about literal wall-clock duration. Given this:
>
> - Do you want relative story points (e.g. Fibonacci 1/2/3/5/8/13), a
>   simpler T-shirt scale (XS/S/M/L/XL), or literal time-boxed estimates
>   (hours/days) despite Scrum convention favoring the former?
> - Should the estimate live as a new field on the Product Backlog Item
>   (`req`/`uc`) itself, on its `tsk` Sprint Backlog breakdown, or both
>   (PBI-level estimate at Planning time, refined per-task once broken
>   down)?
> - Should a human-filled estimate and an agent-filled estimate be
>   structurally indistinguishable in the document (so neither occupant's
>   estimate is treated as more or less authoritative), or should the
>   occupant (human/agent) be recorded alongside the estimate?

!!! - I want a literal time-boxed estimates for now. 
    - both
    - it should be distinguishable and both a human and an agent should be able to entre estimates. but only one is needed each time.

> **0.0020**: Which Scrum accountabilities/roles should get an agent (with
> an equally valid human-only path for each)?
>
> - Option A (Scrum Guide 2020 minimal set): Product Owner, Scrum Master,
>   Developers (the Dev Team as one collective role).
> - Option B (A + Stakeholders): adds a Stakeholder role/agent for
>   review-meeting feedback capture.
> - Option C (A + per-developer agents): one agent instance per individual
>   Developer rather than a single collective "Developers" role, enabling
>   parallel work similar to the existing `phase-implementer` pattern.
> - Option D (A + a Quality/Testing-focused role): not an official Scrum
>   accountability, but common in practice and aligned with the existing
>   `vcr` (Verification Case Record) domain.

!!! I think we start with option c and d both.

> **0.0025**: Follow-up on roles: with Option C (per-developer agents) and
> Option D (a Quality/Testing role) both in scope:
>
> - Should the Quality/Testing role *own* `vcr` (Verification Case Record)
>   creation/maintenance exclusively, or can any Developer also author/
>   update a `vcr`, with the Quality role only required to *approve* (sign
>   off on) it before a PBI counts as Done?
> - For per-developer agents: does each need a stable identity across
>   sprints (e.g. a named agent instance tied to a "developer slot" on the
>   Sprint Backlog, so handover/accountability history is traceable), or is
>   a fresh, anonymous agent instance per sprint/task acceptable?

!!! all can author one but the quality role has to approve it

> **0.0027**: Follow-up on the second half of 0.0025, which wasn't
> answered yet — per-developer agent identity: does each per-developer
> agent need a *stable* identity across sprints (e.g. a named agent
> instance tied to a "developer slot" on the Sprint Backlog, so
> handover/accountability history stays traceable), or is a fresh,
> anonymous agent instance per sprint/task acceptable? This also feeds
> 8.0035's per-task ownership answer: a stable identity gives ownership
> something durable to point at across sprints, while an anonymous
> instance only has meaning within a single sprint.

!!! what are the pros and cons on that?

> **0.0028**: Pros/cons of stable vs. anonymous per-developer agent
> identity:
>
> - **Stable identity** (a named agent instance tied to a "developer
>   slot"): lets the agent build up its own history of prior `tsk`
>   breakdowns to size new PBIs by comparison (the exact mechanism
>   0.0015 proposed), gives 8.0035's per-task ownership something
>   durable to point at across sprints (not just "an agent did this"),
>   and supports a real handover audit trail (5.0010). Cost: needs a
>   slot/registry concept to exist somewhere, and raises the question of
>   what happens to that identity's history when a human permanently
>   replaces the agent in that slot.
> - **Fresh, anonymous instance per sprint/task**: zero extra
>   infrastructure, maximum interchangeability (reinforces 0.0030's
>   "swappable anytime" guarantee most directly), simplest to build
>   first. Cost: no historical basis for 0.0015's own
>   compare-against-prior-work estimation approach, and 8.0035's
>   per-task ownership degrades to "which agent happened to run this
>   sprint" rather than real accountability continuity.
>
> Since the anonymous option undercuts two things you already decided
> (0.0015's estimation method, 8.0035's ownership tracking), I'd lean
> toward stable identity — but it's your call. Which do you want?

TODO: answer pending

> **0.0029**: New topic this round: you raised adding an **Architect**
> role for the Scrum team. HERMES independently lists "IT Architect" as
> its own execution-level role, distinct from a generic developer —
> responsible for technical/solution design and consistency, not
> day-to-day implementation, which lines up well with specmgr's existing
> `adr` (Architecture Decision Record) tooling. Concretely:
>
> - Is Architect a distinct accountability with its own agent (like
>   Quality/Testing was added via 0.0020 Option D), or a specialization
>   *within* "Developers" rather than a separate role?
> - What does it own — sole authorship of ADRs for this effort, or just
>   required *approval* before a PBI touching cross-cutting architecture
>   can be called Done (mirroring Quality's `vcr`-approval gate from
>   0.0025)?
> - Per HERMES's own convention (and mirroring the Quality/Testing
>   independence point raised in this round's 6.0018 below), should
>   Architect stay independent — not also acting as the Developer who
>   implements the same item it designed/approved — or can one
>   person/agent hold both?

TODO: answer pending

> **0.0030**: What exactly must "fillable by an actual human" guarantee,
> precisely?
>
> - Option A (no agent-exclusive state): every action an agent performs
>   (e.g. "Scrum Master facilitates a retro") must be expressible as a human
>   directly calling the same specmgr MCP tools / editing the same markdown
>   files, with no hidden state an agent uniquely owns.
> - Option B (A + no mandatory agent step): additionally, no ceremony or
>   artifact transition may ever *require* an agent to run — a human must be
>   able to complete every step of the process (planning, review, retro,
>   backlog refinement, standups) start to finish using only the plain MCP
>   tools/CLI, with agents being pure convenience on top.
> - Option C (A + B + mid-process swap): additionally, the occupant of a
>   role (human or agent) must be swappable sprint-to-sprint, or even
>   mid-sprint, without migrating data or changing the artifact schema.

!!! I want option b and c

> **0.0040**: Confirming scope for this first round: only this QA document
> is being created right now (no `.specmgr/feat/` folder yet for this
> effort) — correct, and should a feature folder be opened once these
> answers settle, or kept informal for longer?

!!! keep informal for at least the next refinement round.

## Functional Suitability

<!-- Ceremony/artifact mapping: what each Scrum event and artifact concretely maps onto. -->

> **1.0010**: Which of the standard Scrum events should be modeled
> explicitly, each as its own skill/command (mirroring the existing
> `review-feature`/`refine-feature` pattern)? Sprint Planning, Daily Scrum,
> Sprint Review, Sprint Retrospective, and Backlog Refinement (not an
> official Scrum event, but near-universal practice) — all five, a subset,
> or others (e.g. Release Planning)?

!!! all of the above.

> **1.0020**: For Sprint Planning specifically: should "committing" a set
> of Product Backlog Items to a sprint be a new frontmatter/body concept
> added to `tsk` (e.g. a `sprint` field), reuse the existing `feat`
> Phase/Task numbering scheme as a sprint's scope boundary, or something
> else entirely?

!!! this stays open for the moment. I think we should first define the process before we go into that kind of detail. But we don't want to reinvent the wheel. How do others do this? For instance Jira?

> **1.0025**: Follow-up / research note on common tooling (your Jira
> question): most Scrum tools (Jira, Azure DevOps, Linear) model this with
> three concepts: (1) an **Epic** grouping related backlog items, (2) a
> **Sprint** as a time-boxed field/attribute attached directly to an issue
> (not a separate hierarchy level), and (3) a **Board** that is just a
> filtered/grouped *view* over issues, not its own stored artifact. Mapped
> onto specmgr's existing domains:
>
> - Option A: treat `feat` (folder-per-feature, already has Phase/Task
>   numbering) as the Epic-equivalent, and add a lightweight `sprint`
>   attribute directly to `req`/`uc` (and/or `tsk`) frontmatter — closest to
>   Jira's own model, no new domain needed yet (consistent with your Option
>   C "reuse-first" choice on 0.0010).
> - Option B: skip Epics entirely for now (most PBIs stand alone) and only
>   add the `sprint` attribute, deferring any Epic-equivalent grouping to a
>   later round.
> - Option C: don't add any new field yet — represent "this sprint's scope"
>   purely as a filtered view (e.g. a generated report/command output) over
>   existing `classification`/status fields, with nothing new persisted at
>   all.
>
> Which of these (if any) fits best, or would you like a dedicated
> follow-up round specifically to design this once more of the ceremony
> detail (refinement, prioritization, Definition of Done — see
> 1.0065/1.0075/1.0085 below) is settled?

!!! It will need a extra round of refinement. But for the moment certainly rather option a.

> **1.0030**: For the Daily Scrum: is a literal daily synchronous ceremony
> even wanted here (this is an agent/CLI-first workflow, not a live
> meeting), or should it become an on-demand "status/impediments summary"
> command any role can run at any time — closer to a standup-report
> generator than a real-time meeting?

!!! your suggestions for a more on-demand command sounds ok

> **1.0040**: For Sprint Review: should the outcome (what's accepted, what's
> deferred, stakeholder feedback) be captured as a `dec` (Decision)
> document, a `vcr` (Verification Case Record) per backlog item, or a new
> dedicated artifact?

!!! I think the current artifacts will be ok. But we should reconsider this later

> **1.0050**: For Sprint Retrospective: should outcomes (process
> improvements, action items) be captured as `dec` documents, a new `tsk`
> task list of improvement actions, or something else?

!!! same answer as the one before

> **1.0055**: Follow-up on 1.0040/1.0050 ("the current artifacts will be
> ok"), to pin down which artifact concretely: for **Sprint Review**, is
> the outcome (accepted/deferred items, stakeholder feedback) one `dec`
> document per sprint, or an update to each accepted PBI's own `vcr`? For
> **Sprint Retrospective**, is it one `dec` document per retro
> (process-improvement decisions), or something else? Defaulting to "one
> `dec` per ceremony per sprint" unless you say otherwise.

!!! your default is ok

> **1.0060**: For Backlog Refinement: is this simply the existing
> `qa`-driven requirements-elicitation interview flow (already supported via
> `create_qa`/the `refine` prompt) applied per Product Backlog Item, or do
> you want a dedicated refinement ceremony/skill distinct from that?

!!! I need to know more about the backlog refinement ceremony to be able to answer this.

> **1.0065**: Backlog Refinement, explained: it's the ongoing activity
> (not time-boxed as strictly as Planning/Review/Retro) where the Product
> Owner and Developers jointly prepare upcoming Product Backlog Items so
> they're ready to be pulled into a future sprint. In practice it typically
> covers: (1) clarifying/adding acceptance criteria, (2) splitting an item
> that's too large into smaller ones, (3) estimating size (see 0.0015), and
> (4) re-ordering/re-prioritizing based on new information. None of this
> requires a live meeting — it can happen asynchronously, one item at a
> time. Given that:
>
> - Does the existing `qa`-driven elicitation flow (`create_qa`/`refine`
>   prompt) already cover step (1) well enough, with 1.0025's `sprint` field
>   and 0.0015's estimate covering (3)/(4), making a *dedicated* Refinement
>   ceremony mostly "run `refine` + fill in the new fields" rather than new
>   tooling?
> - Or do you want a single combined refinement command that walks all four
>   steps (acceptance criteria, splitting, estimating, prioritizing) in one
>   guided pass per PBI, distinct from the existing generic `qa` refinement
>   flow?

!!! an single combined refinement command

> **1.0070**: Should the Product Backlog itself be a literal ordered list
> somewhere (a document, or a view derived from `list_req`/`list_uc`), or
> stay purely implicit — "all `req`/`uc` documents not yet assigned to a
> sprint", with ordering left to priority/classification fields?

!!! how will the priorisation/classification take place? I need to know more to be able to answer this question.

> **1.0075**: Prioritization/classification options, since you need this to
> answer the ordering question:
>
> - Option A (ordinal rank): a single numeric `priority` field (1 =
>   highest) on each `req`/`uc`, directly orderable — simplest, but requires
>   renumbering neighbors when inserting.
> - Option B (MoSCoW): reuse the existing free-text `classification`
>   frontmatter field with a closed `Must`/`Should`/`Could`/`Won't`
>   vocabulary — coarse-grained, no renumbering needed, but ties within a
>   bucket are unordered.
> - Option C (value-based, e.g. WSJF/cost-of-delay): a heavier scoring
>   model (business value, urgency, risk reduction, effort) producing a
>   derived rank — most "correct" Scrum/Lean practice, but needs several new
>   fields and is harder to maintain by hand (works against the
>   "human-fillable" goal if too heavy).
>
> Which fits your intended level of rigor, and should it live on `req`/`uc`
> directly, or only apply as a transient ordering at Backlog-Refinement/
> Planning time rather than a persisted field?

!!! Option C living on 'reg'/'uc' directly

> **1.0077**: Follow-up reconciling WSJF (1.0075's Option C) with the
> literal time-boxed estimate from 0.0015: WSJF conventionally computes
> `(business value + time criticality + risk reduction) / job size`, where
> `job size` is a *relative* effort unit, not absolute hours/days — using
> literal hours directly as the denominator skews the ranking toward
> small/quick items regardless of value. Given that:
>
> - Should `job size` in the WSJF formula reuse the literal time estimate
>   from 0.0015 directly (accepting that skew), or do you want a separate,
>   purely relative sizing field used only for WSJF math, with the literal
>   time estimate staying for scheduling/burndown?
> - What scale should `business value`/`time criticality`/`risk reduction`
>   each use (e.g. 1-10, Fibonacci-like 1/2/3/5/8/13, or something else),
>   and should the derived WSJF score be stored as a field or always
>   recomputed on demand?

!!! I don't understand the skew. Can you explain?

> **1.0078**: Worked example of the WSJF skew: PBI A has business value
> 8 and an estimate of 1 hour. PBI B also has business value 8, but an
> estimate of 40 hours. Dividing value by literal hours gives A a score
> of 8/1 = 8 and B a score of 8/40 = 0.2 — A ranks 40x higher purely
> because it's quick, even though both deliver *identical* value. Now
> say PBI A is a trivial typo fix and PBI B is the single most valuable
> feature in the whole backlog, which simply happens to take longer:
> literal-hours WSJF would still rank the typo fix far above the major
> feature. That's the "skew" — the denominator rewards speed over value,
> independent of how valuable the slower item actually is. Relative
> story points are less prone to this because they're meant to track
> *relative* effort rather than punish-by-literal-duration, but they're
> also coarser (e.g. a 1-hour and a 3-hour task might both round to the
> same Fibonacci bucket). Given this: do you still want `job size` =
> literal hours (accepting the skew, perhaps with a sanity-check cap), or
> would you rather add a separate, purely relative sizing field used
> only for the WSJF math?

TODO: answer pending

> **1.0080**: What signals "Done" for a Product Backlog Item — only a
> passing `vcr` (Verification Case Record), a status transition on the
> `req`/`uc` document itself, or both together?

!!! what does our process say for definition of done?

> **1.0085**: Definition of Done doesn't exist yet in our process — it's a
> team-defined artifact in Scrum, not something the framework prescribes,
> so this process needs to state an initial default rather than discover
> one. Proposed default Definition of Done for a Product Backlog Item here:
> (1) its `vcr` (Verification Case Record) shows `Coverage: full` against
> every `## Acceptance Criteria` entry, and (2) the `req`/`uc` document's
> own `status` has transitioned to `accepted` (or equivalent). Is this an
> acceptable starting Definition of Done, should it be weaker for v1 (e.g.
> status transition alone, `vcr` added later), or do you already have
> specific criteria in mind (e.g. code merged, docs updated, tests passing)
> that should be enumerated explicitly here?

!!! I think 1 and 2 is good. The tests should certainly be run and it can be another indicator for definition of done how many % passed. (like there can be no critial bugs, only 5 major ones and 20 trivial ones or something like that). Add a bug or error severity level.

> **1.0087**: Follow-up on the bug/defect severity addition to Definition
> of Done (1.0085): specmgr has no existing artifact for tracking
> individual defects/bugs today. Where should they live?
>
> - Option A: as `rsk` (Risk) entries, reusing the existing 5x5
>   probability/impact assessment, with severity derived from the `rsk`
>   zone/level rather than a new field.
> - Option B: as a new lightweight field set directly on the `vcr`
>   (Verification Case Record) each defect was found against (a defect
>   list with a closed severity vocabulary).
> - Option C: a brand-new `defect`/`bug` domain, structurally distinct from
>   `rsk` (a risk is a *potential* future problem; a defect is a
>   *confirmed* one already found), with its own severity field.
>
> And concretely: what are the severity levels (e.g.
> `critical`/`major`/`minor`/`trivial`) and the actual pass thresholds for
> Definition of Done — should your example (0 critical, <=5 major, <=20
> trivial) be the literal v1 default, or do you want different numbers?

!!! I'm not sure on that. How does scrum do it, if they don't handle bugs?

> **1.0088**: How Scrum itself actually handles bugs: it doesn't define
> them as a separate concept at all. In the official Scrum Guide, a bug
> is just another Product Backlog Item like any feature request — it
> goes into the Product Backlog, gets sized the same way (story
> points/estimate), gets prioritized by the Product Owner against every
> other item (sometimes high, sometimes low), and is "Done" when it
> meets the same Definition of Done as everything else. There is no
> built-in defect artifact, severity scale, or workflow in Scrum —
> teams that want one invent it themselves, exactly what you're doing
> here. Given that, a fourth option worth considering alongside
> 1.0087's A/B/C:
>
> - Option D: bugs are just regular `req`/`uc` Product Backlog Items,
>   with severity captured via the existing `classification`/priority
>   fields instead of a dedicated mechanism — no new tracking concept at
>   all, closest to how Scrum itself treats them.
>
> Does Option D fit better than inventing a dedicated
> severity/defect mechanism, or do you still want one of A/B/C from
> 1.0087 (and if so, which, plus the concrete severity levels/thresholds
> that question also asked for)?

TODO: answer pending

## Performance Efficiency

> **2.0010**: Is there a desired sprint length/cadence this process should
> assume or enforce (e.g. always 2 weeks), or should cadence stay a free
> configuration choice left entirely to the team using it, not encoded
> anywhere in specmgr?

!!! there should be a standard that can be changed easily

> **2.0015**: Follow-up on cadence ("a standard that can be changed
> easily"): what should the actual default be — 1 week, 2 weeks, or
> something else — and where should it live so it stays easy to change (a
> field in the `sop` process document from 7.0015, a value on the
> `sprint`/GitHub-Project side from 5.0027, or a plain config value
> alongside the other `SPECMGR_*_DIR` env vars)?

!!! SOP for now

> **2.0017**: Just the number itself now that the "where" is settled
> (the `sop` document): what should the actual default cadence be — 1
> week, 2 weeks (the most common real-world default), 3 weeks, or 4
> weeks (the Scrum Guide's own stated maximum)?

TODO: answer pending

> **2.0020**: Do you want any velocity/throughput tracking (e.g. items
> completed per sprint) as part of this, or is that explicitly out of scope
> for the first iteration?

!!! yes, burn down etc should also be part of this

> **2.0025**: For burndown/velocity tracking: should it track count of
> Product Backlog Items completed, their estimated size (story points/
> T-shirt size from 0.0015), or both? And do you want a burnup chart
> (showing scope growth alongside completion) in addition to burndown,
> given Scrum backlogs commonly grow mid-sprint?

It certainly must show scope growth as well!

## Compatibility

> **3.0010**: Should this process integrate with the existing GitHub
> issue-numbering convention used by `feat-NNN-slug` (i.e. a sprint maps
> loosely onto one or more GitHub milestones/issues), or should it stay
> entirely GitHub-agnostic?

!!! yes, integrate

> **3.0015**: Concretely, how should the GitHub integration map? Suggested
> default: a GitHub Milestone represents one Sprint (its due date = sprint
> end), and each Product Backlog Item (`req`/`uc`) pulled into that sprint
> links to one GitHub Issue (mirroring how `feat-NNN-slug` already embeds
> its GitHub issue number). Does that match what you had in mind, or did
> you picture GitHub Projects (boards) as the primary integration point
> instead (with Milestones unused)?

!!! I had GitHub Projects in mind

> **3.0017**: Follow-up on GitHub Projects as the integration point: since
> a Project (board) is a cross-repo, configurable *view*, not a time-boxed
> container the way a Milestone is, how should a Sprint map onto it
> concretely?
>
> - Option A: one GitHub Project *per sprint* (created/archived each
>   sprint boundary), with every committed PBI's Issue added to it.
> - Option B: one long-lived GitHub Project for the whole backlog, with a
>   custom "Sprint" field/column on it (mirroring the `sprint` attribute
>   from 1.0025) used to filter the current sprint's view.
> - Option C: one Project per team (ties into the multi-team question,
>   8.0025/8.0027), each with its own "Sprint" field.
>
> Separately: does every PBI (`req`/`uc`) still get its own linked GitHub
> Issue (as originally suggested), with the Project just being the
> sprint-level view over those issues, or did you picture something
> different?

!!! I don't know GIthub enough. Can you advise? Is the github milestone comparable to sprint? should it be used instead of project?

> **3.0018**: Milestone vs. Project, explained: a GitHub **Milestone** is
> a built-in, time-boxed container — it has a due date, a target list of
> issues, and automatic open/closed-issue progress tracking. Functionally
> it *is* GitHub's own native equivalent of a Sprint. A GitHub **Project**
> (the newer Projects v2 boards) is a persistent, cross-repository,
> fully customizable table/board/roadmap with custom fields, filters, and
> multiple views — closer to a queryable workspace than a time box; it
> has no built-in "this is a 2-week period" concept the way a Milestone
> does.
>
> Recommendation: use a **Milestone** to represent each Sprint (gets you
> the due date and native progress tracking for free, no custom fields
> needed), and use a **Project** as the longer-lived, cross-sprint view
> on top of it (backlog grooming board, multi-sprint roadmap, or
> multi-team board) — the two aren't mutually exclusive, and this is how
> most real teams combine them. Does that resolve your original 3.0015
> question in favor of using both (Milestone = Sprint, Project =
> backlog/roadmap view), or did you specifically want Projects used for
> something a Milestone structurally can't do (e.g. a single board
> spanning multiple repos)?

TODO: answer pending

> **3.0020**: Should the new Scrum role-agents/skills/commands follow the
> exact same `.opencode/agent` + `.opencode/command` + `.opencode/skill`
> pattern already used for `phase-orchestrator`/`phase-implementer`/
> `feat-reviewer`/etc. (so they compose with those — e.g. a "Developer" role
> agent could itself invoke `phase-implementer`), or should they be
> deliberately independent/isolated from the feature-implementation
> tooling?

!!! they should folow the exact same pattern.

## Interaction Capability

> **4.0010**: Should each ceremony get its own slash command (e.g.
> `/sprint-plan`, `/standup`, `/retro`, `/review`), the way
> `/refine-feature`/`/review-feature`/`/implement-feature` already work —
> one command per ceremony rather than one per role?

!!! I'm no sure. What do you suggest?

> **4.0015**: Suggestion: one slash command per ceremony (e.g.
> `/sprint-plan`, `/standup`, `/review`, `/retro`, `/refine-backlog-item`)
> rather than per role, mirroring the existing `/refine-feature`/
> `/review-feature`/`/implement-feature` precedent — a ceremony naturally
> involves multiple roles at once (e.g. Planning needs both PO and
> Developers), so a per-role command would need awkward sub-dispatch
> anyway, while a per-ceremony command can internally invoke whichever
> role-agent(s) are relevant. Do you want to go with that, or did you have
> a reason to prefer per-role commands instead?

!!! yes I want to go with that

> **4.0020**: When a role is "played" by an agent, should it always ask
> clarifying questions interactively via the `question` tool (as the
> existing narrated prompts do), always run fully non-interactively like
> this QA round, or should that differ per ceremony?

!!! differ per ceremony

> **4.0025**: Given "differs per ceremony" — proposed default split:
> **Sprint Planning** and **Sprint Review** interactive (via the `question`
> tool), since they inherently involve negotiating with a human Product
> Owner/stakeholders; **Daily Scrum/standup** non-interactive (an on-demand
> generated summary, per 1.0030); **Backlog Refinement**'s first pass
> non-interactive (a draft a human then edits, like this QA round) with
> interactive follow-up only when genuinely ambiguous; **Sprint
> Retrospective** interactive (facilitating a retro by asking questions is
> the whole point of the ceremony). Does this split match your intent, or
> would you flip any of these?

!!! let's start with that. TODO: Also check the Hermes 2022 projectmanagement method https://www.hermes.admin.ch/. Is there anything in there, that we should integrate in our process as well that makes sense with our scrum adaptation?

> **4.0027**: Noting your Hermes 2022 research TODO so it doesn't get
> lost: do you want that research done *before* the process design is
> finalized (a blocking step in a round 4), done in parallel while the
> rest of the process is drafted (integrating any findings later, possibly
> as a schema/process revision), or deferred entirely to after a v1 of the
> Scrum process ships?

!!! do the research before you draft the questions for round 4.

> **4.0030**: Do you want any notification/reporting output (e.g. a
> generated Markdown summary posted somewhere after each ceremony), or is
> the artifact update itself (the `tsk`/`dec`/`vcr`/etc. document) a
> sufficient record of the ceremony?

!!! no sure. what do you suggest?

> **4.0035**: Suggestion: for v1, don't add a separate notification/
> reporting channel — let the artifact update itself (the `tsk`/`dec`/
> `vcr`/etc. document, plus the standup command's own on-demand console
> output from 1.0030) be the complete record, since specmgr has no existing
> notification mechanism (email/chat webhook) to build on, and adding one
> would be a sizable integration unrelated to the Scrum process itself. A
> dedicated "ceremony summary" artifact/integration could be revisited
> later if the plain document trail proves insufficient in practice.
> Agreed, or do you already have a specific channel in mind (e.g. posting
> to GitHub as an issue/milestone comment, consistent with the GitHub
> integration from 3.0010/3.0015)?

!!! still not sure on that one

> **4.0037**: Since 4.0030/4.0035 were both answered "not sure": absent a
> stronger preference, the plan is to go with the suggested v1 default —
> no dedicated notification/reporting channel, with artifact updates (plus
> the standup command's own console output) as the complete record.
> Confirm that default is fine for v1, or is there something specific
> (e.g. a GitHub issue/Project comment posted automatically after each
> ceremony) you'd want reconsidered now rather than later?

!!! what do you suggest?

> **4.0038**: Making this a plain yes/no: the proposal is — build no
> notification channel at all for v1. When a ceremony happens, the only
> record is the artifact itself (the `tsk`/`dec`/`vcr` document that
> ceremony updates), plus, for the Daily Scrum, the on-demand standup
> command's console output (1.0030). Nothing gets posted anywhere
> automatically. Yes, go with that for v1, or no — you want something
> posted somewhere, and if so, where (e.g. a GitHub issue/Project
> comment)?

TODO: answer pending

## Reliability

> **5.0010**: If an agent fills a role for one sprint and a human takes
> over the same role the next sprint (or vice versa), what must be
> preserved across that handover — just the artifacts (trivially true,
> since they are plain documents), or also some role-specific "memory"/
> context the next occupant needs?

!!! cannot answer this at this state yet

> **5.0020**: What happens if a ceremony is skipped entirely for a sprint
> (e.g. no retro happened) — should the tooling detect/flag that, or is
> enforcement entirely a human/process concern outside specmgr's scope?

!!! tooling should flag it

> **5.0025**: Given no `sprint` schema exists yet (0.0010 Option C:
> staged), how should "ceremony skipped" even be detected for now?
> Suggested v1 approach: a "health check" command (similar to the existing
> `review-feature` precedent) that inspects whether the expected artifacts
> exist for the current sprint window (e.g. a `dec`/`vcr` update during
> Review, a retro `dec` during Retro) and reports gaps — on-demand only, not
> an automatic/background check. Acceptable for now, or do you want this to
> actively block something (e.g. refuse to start the next Sprint Planning
> until the previous sprint's Retro is recorded)?

!!! why can't we mache a schema?

> **5.0027**: Follow-up on reopening the schema question — this directly
> revisits 0.0010's Option C ("stay reuse-only until a concrete gap
> appears"); the skipped-ceremony/health-check need from 5.0020 is exactly
> that gap surfacing already, in round 2 rather than later. Given that, do
> you want to:
>
> - Option A: introduce a dedicated `sprint` domain/schema now (reversing
>   0.0010's staged choice) — a first-class, queryable document per sprint
>   (start/end dates, sprint goal, committed items, ceremony-completion
>   flags) the health-check command (5.0025) can inspect directly, instead
>   of inferring a sprint window from scattered `tsk`/`dec`/`vcr`
>   documents?
> - Option B: keep the staged, reuse-only approach, but still get a
>   concrete "sprint window" to health-check against from the `sprint`
>   field on `req`/`uc` (1.0025's Option A) plus its GitHub Project/board
>   dates (3.0017) — i.e. "a sprint is everything sharing this sprint
>   value, bounded by its Project's start/end" — with no new domain yet.
> - Option C: introduce the `sprint` domain now, but scoped minimally
>   (just enough fields for health-check/reporting), deferring any richer
>   sprint-schema design (burndown data model, per-team scoping) to a
>   later round.
>
> This decision also affects how multi-team (8.0020/8.0027), burndown/
> burnup (2.0025), and the GitHub Projects mapping (3.0017) get designed,
> so it's worth settling before those.

!!! option a

## Security

> **6.0010**: Should any role carry real authority constraints (e.g. only
> the Product Owner may reorder the backlog or mark an item "Done", only
> the Scrum Master may change sprint cadence), enforced somehow in tooling,
> or is authority purely a social/organizational convention this process
> doesn't technically enforce — mirroring how specmgr today has no
> per-user permission model at all?

!!! make a suggestion for the authority constraints

> **6.0015**: Suggested authority matrix (conventions only for now, since
> specmgr has no permission/auth model — see 6.0025 for enforcement
> mechanics):
>
> - **Product Owner**: sole authority to reorder/re-prioritize the Product
>   Backlog and to accept a PBI as "Done" at Sprint Review.
> - **Scrum Master**: sole authority to change sprint cadence/length and to
>   declare a sprint cancelled early.
> - **Developers**: sole authority over technical task breakdown and effort
>   estimates within a committed sprint (the "how").
> - Nobody unilaterally changes a sprint's committed scope mid-sprint
>   without the whole Scrum Team (PO + SM + Developers) agreeing — mirrors
>   the Scrum Guide's own rule that only Developers can change scope *in
>   consultation with* the PO.
>
> Does this match your expectations, or would you adjust any of these
> assignments?

!!! Do we not have further roles?

> **6.0017**: Follow-up on "do we not have further roles?": the suggested
> authority matrix (6.0015) only covered Product Owner/Scrum
> Master/Developers — it's missing the Quality/Testing role added at
> 0.0020. Proposed addition: **Quality/Testing**: sole authority to
> approve (sign off on) a `vcr` before a PBI counts as Done, regardless of
> who authored it (ties into 0.0025's "any Developer can author, Quality
> approves" answer). Is Product Owner / Scrum Master / Developers /
> Quality-Testing now the complete role list for authority purposes, or
> are there other roles/accountabilities you had in mind (e.g.
> Stakeholders from 0.0020's Option B, which wasn't picked but could still
> need an authority line for review feedback)?

!!! Do scrum teams have any other roles? to development teams have specifications like tester? give me a suggested list for more roles

> **6.0018**: Suggested additional roles, drawing on both common Scrum
> practice and the HERMES research (4.0027):
>
> - **Architect** (new this round, see 0.0029) — technical/design
>   authority; a natural fit given specmgr's existing `adr` tooling.
> - **Sponsor/Executive** (HERMES's "Project Sponsor" — a steering-level
>   role sitting *above* the Scrum Team, distinct from Product Owner):
>   owns budget/strategic objectives and the "why does this exist" case,
>   while the Product Owner stays the operational "what" authority.
>   HERMES makes this role mandatory and explicitly forbids it from being
>   held by the same person as the team-level manager equivalent.
> - **Stakeholder** (0.0020's Option B, not picked as a full agent role)
>   — still worth a light authority line even without a dedicated agent:
>   gives feedback at Sprint Review, has no decision authority.
> - **Tester**: HERMES lists Tester as its own execution role, separate
>   from a generic Developer — worth asking whether this should be
>   folded into the Quality/Testing role you already have (0.0020 Option
>   D) or kept conceptually distinct (Quality approves/signs off;
>   Tester actually writes/runs tests).
>
> Do you want any/all of these added, and if Sponsor is added: should it
> have override authority over Scrum Master's sole authority to cancel a
> sprint (6.0015), given HERMES treats the Sponsor as the ultimate
> steering authority?

TODO: answer pending

> **6.0020**: Is there any reason an agent playing a role should ever be
> restricted from an action a human in that same role could take (e.g. an
> agent Product Owner must not unilaterally close a sprint without human
> sign-off)? If yes, where should that restriction live — in the agent's
> own prompt/instructions, or enforced at the MCP tool layer?

!!! yes, there need to be those restrictions. what are the pros and cons for prompt vs mcp tool? where will it be acknowledged better?

> **6.0025**: Pros/cons of where to enforce agent-only restrictions:
>
> - **Prompt-level** (the agent's own `.opencode/agent/*.md` instructions,
>   like `doc-repairer`'s "never commits"): easy to write and iterate, keeps
>   the MCP server itself role-agnostic (consistent with specmgr having no
>   auth model at all today) — but it is advisory only: a badly-prompted or
>   sufficiently capable agent run could still ignore it, and it does
>   nothing for a human operator calling the same MCP tools directly (a
>   human was never going to be stopped by an agent's own prompt anyway).
> - **MCP-tool-level** (e.g. a precondition on `set_status`/`update` that
>   refuses certain transitions unless a flag confirms human sign-off):
>   actually enforced regardless of who's calling, and applies equally to
>   agents and humans (consistent with the "nothing agent-exclusive" goal)
>   — but is a real code change to shared generic tools used by every
>   domain, and risks over-engineering a permission system specmgr
>   deliberately doesn't have yet.
>
> Suggested v1 approach: start prompt-level only (fast, matches the current
> architecture, zero risk to shared tools), and revisit MCP-tool-level
> enforcement later only if prompt-level restrictions prove to be routinely
> ignored or insufficient in practice. Agreed, or do you want tool-level
> enforcement from the start for the specific "unsupervised decisions" list
> from Safety (9.0010/9.0015)?

!!! i want the safer version

> **6.0027**: Follow-up on choosing MCP-tool-level enforcement ("the safer
> version"): this is a real mechanism to design, not just a preference.
> Concretely:
>
> - Should it be scoped to exactly the 5 actions in the 9.0015 checklist
>   (sprint-scope commit, mid-sprint scope change, Definition-of-Done
>   acceptance, sprint cancellation, backlog reordering that bumps a
>   committed item), or broader?
> - What should the actual enforcement mechanism look like — a new
>   required confirmation parameter/flag on the relevant generic tool call
>   (`set_status`, `update`) that must be explicitly supplied by a human
>   session, a separate "human sign-off" tool that must succeed before the
>   status-changing tool will, or something else?
> - Since this touches shared generic tools used by every domain, not just
>   Scrum artifacts, do you want this designed/reviewed as its own ADR
>   before implementation, consistent with how other cross-cutting
>   mechanism changes in this codebase are usually decided?

!!! reading your answer I think that maybe the option promt-level would be better. what do you think? 

> **6.0028**: My actual recommendation, rather than just restating the
> tradeoffs: a **hybrid**, not purely one or the other — prompt-level for
> every ordinary role behavior, but MCP-tool-level specifically (and
> only) for the 5 Safety-critical actions in the 9.0015 checklist, since
> those are exactly the ones you already said must never happen
> unsupervised regardless of role (9.0010). That keeps the tool-layer
> change small and bounded (5 specific transitions, not a general
> permission system) while still giving real, unbypassable teeth to the
> one list you explicitly flagged as non-negotiable — prompt-level alone
> is advisory only and wouldn't actually guarantee that list holds. Does
> this hybrid split work for you, or do you want to stay fully
> prompt-level for now (as 6.0025 originally suggested) and revisit
> tool-level only if it's later ignored in practice?

TODO: answer pending

## Maintainability

> **7.0010**: Should the Scrum process definition itself (ceremonies, role
> responsibilities, artifact mapping) be documented as its own specmgr
> artifact — e.g. one or more `sop` (Standard Operating Procedure)
> documents, which already model RASCI responsibility assignment — or
> purely as `.opencode` agent/skill/command instructions with no
> corresponding specmgr document?

!!! what are the pros and cons for that?

> **7.0015**: Pros/cons of documenting the process as an `sop` artifact vs.
> agent/skill/command instructions only:
>
> - **As an `sop` document**: becomes a real, versioned, queryable specmgr
>   artifact (listable via `list_sop`, referenceable from other documents
>   via the cross-reference tag vocabulary, carries its own RASCI
>   `## Roles and Responsibilities`) — directly reinforces the
>   "human-fillable" goal, since a human with zero agent access can read
>   the exact same process definition a human would otherwise only get by
>   reading agent prompts. Cost: another document to keep in sync if the
>   process evolves, and the existing `sop` schema's approval/effectivity
>   lifecycle may be heavier than needed for an internal process doc.
> - **Agent/skill/command instructions only**: zero extra artifact to
>   maintain, changes ship in the same place as the behavior they describe
>   — but then the canonical process description only exists embedded in
>   `.opencode/` files, which a human who wants to run the process
>   *without* any agent would have to go dig through instead of reading one
>   clear document.
>
> Suggested approach: one `sop` document as the single human-readable
> source of truth for the process (ceremonies, roles, artifact mapping,
> Definition of Done, authority matrix from 6.0015), with every agent/
> skill/command simply pointing back to it (mirroring how `sop`'s own
> prompts already read the cross-cutting `specmgr://rasci` resource first).
> Agreed?

!!! agreed

## Flexibility

<!-- The core "every role must be human-fillable" ask, plus scaling questions. -->

> **8.0010**: Should a single person be allowed to occupy more than one
> role at once (common in small teams, e.g. one person as both Product
> Owner and Scrum Master), and should the tooling have any opinion on that,
> or must it stay entirely agnostic?

!!! first design the process then ask me this again

> **8.0020**: Should this process support multiple concurrent teams/
> backlogs (several Scrum Masters, several Developer groups, one shared
> Product Owner) from day one, or is a single-team design sufficient for
> the first iteration, with multi-team support deferred?

!!! we will need multi-team

> **8.0025**: Since multi-team support is needed: should teams share a
> single Product Backlog with one Product Owner prioritizing across all
> teams (Nexus/Scrum@Scale-style), or does each team get its own fully
> independent backlog and Product Owner? And should teams be distinguished
> in specmgr via a `classification`/tag field on shared documents (one
> shared `req`/`uc`/`gol` pool, filtered by team), or via fully separate
> directories/base-directory configuration per team (mirroring how
> `SPECMGR_*_DIR` env vars already let each domain's base directory be
> overridden)?

!!! not sure yet

> **8.0027**: Follow-up on multi-team shape — flagging this as one of the
> more structurally important open points, since 8.0020 already confirmed
> multi-team is needed from day one, and the backlog/sprint design (and
> the GitHub Projects mapping from 3.0017) depends on which shape is
> picked:
>
> - Option A (shared backlog, shared PO): one Product Backlog, one Product
>   Owner prioritizing across all teams (Nexus/Scrum@Scale-style); teams
>   distinguished via a `classification`/tag field on the shared
>   `req`/`uc`/`gol` pool.
> - Option B (per-team backlog, per-team PO): each team has its own fully
>   independent backlog and Product Owner; teams distinguished via
>   separate base directories (`SPECMGR_*_DIR`-style overrides) rather
>   than a tag.
> - Option C (hybrid): a shared Product Goal (`gol`) and `feat`-level
>   grouping, but independent per-team backlogs/Product Owners underneath
>   it.
>
> Which fits your organization best, or is it genuinely too early to say,
> and you'd rather explicitly defer this (like 8.0010) to right before
> implementation?

!!! keep this open for now

> **8.0028**: Scrum of Scrums (SoS) research, per your request — and it
> turns out the real gap in 8.0025/8.0027 wasn't *who owns the backlog*,
> it was *how do independent teams actually coordinate day to day*,
> which is a separate, orthogonal question:
>
> - **SoS mechanics**: each team's daily scrum ends by naming one
>   **ambassador** (a Developer, Scrum Master, or sometimes a manager)
>   who attends a periodic cross-team sync. Ambassadors report
>   completions/next-steps/impediments on behalf of their team, focused
>   specifically on *between*-team coordination (interfaces, dependency
>   boundaries). Crucially, the SoS tracks its own backlog of cross-team
>   **R**isks, **I**mpediments, **D**ependencies, **A**ssumptions
>   (RIDAs) — which maps directly onto specmgr's existing `rsk` domain,
>   no new schema needed for this part.
> - Two well-known scaling frameworks build on exactly this: **Nexus**
>   (shared backlog + shared PO + a dedicated Integration Team — the
>   closest precedent for your 8.0025 Option A) and **Scrum@Scale**
>   (independent per-team backlogs/POs + a rotating SoS-Master ambassador
>   plus an "Executive MetaScrum"/Chief-PO layer for strategic alignment
>   — the closest precedent for Option B).
>
> Proposal: regardless of which backlog-ownership option (A/B/C) you
> eventually pick for 8.0025, add the coordination mechanism now as its
> own piece — an ambassador-based `/scrum-of-scrums` ceremony/command,
> with cross-team RIDAs tracked as `rsk` entries. Does having a concrete
> answer for *coordination* make it easier to decide the
> backlog-*ownership* question (8.0025) now, or do you still want that
> part deferred?

TODO: answer pending

> **8.0030**: Can the "Developers" role be partially human and partially
> agent within the very same sprint (e.g. two human developers plus one
> `phase-implementer`-style agent working the same Sprint Backlog), or
> should role occupancy be all-human or all-agent for a given sprint?

!!! it can be mixed

> **8.0035**: Given Developers can be a mixed human/agent set within one
> sprint: should the Sprint Backlog (`tsk`) record *who* (which named
> human, or which agent instance) owns each task line, so handover/
> accountability stays traceable (ties into the deferred Reliability
> question 5.0010), or is per-task ownership out of scope for now, with the
> Sprint Backlog staying occupant-agnostic (just "done"/"not done")?

!!! per-task ownership is good

## Safety

> **9.0010**: Is there any Scrum decision this process must never let an
> agent make unsupervised — e.g. agreeing to a scope change mid-sprint,
> declaring the Definition of Done satisfied, or cancelling a sprint — i.e.
> an explicit list of actions that always require human confirmation
> regardless of who nominally holds the role?

!!! yes

> **9.0015**: Proposed concrete list of actions that always require
> explicit human confirmation, regardless of who nominally holds the role —
> please confirm, trim, or extend:
>
> 1. Committing a sprint's scope at Sprint Planning (what gets pulled in).
> 2. Agreeing to any mid-sprint scope change.
> 3. Declaring a Product Backlog Item's Definition of Done satisfied /
>    accepting it at Sprint Review.
> 4. Cancelling a sprint early.
> 5. Re-prioritizing/reordering the Product Backlog in a way that bumps an
>    already-committed item out of the current sprint.
>
> Is this the right list, and should it live as a literal checklist inside
> the `sop` process document from 7.0015 (so it's independently
> auditable), or purely as shared guardrail text repeated across the
> relevant agent prompts?

!!! yes, this is a good start. there will be more points to it. yes as a ckecklist inside sop

## More Information

The nine section headings above (`Functional Suitability` through `Safety`)
are the fixed ISO/IEC 25010:2023 quality characteristics the `qa` document
schema requires; they are repurposed here as a best-fit bucketing scheme for
a process-design interview rather than a literal software-quality
assessment. Questions were placed under whichever characteristic they most
resembled (e.g. role/ceremony mechanics under `Functional Suitability`,
human/agent interchangeability under `Flexibility`, ceremony communication
under `Interaction Capability`). `Elicitation Context` additionally carries
the structural scoping questions (new schema vs. reuse, which roles are in
scope, what "human-fillable" must guarantee) that determine how every later
answer should be interpreted.

Round 2 added in-between follow-up numbers (e.g. `0.0015`, `1.0025`) directly
after the specific round-1 answer each one responds to — per the `qa` v2
schema's own documented convention, gaps and in-between numbers are a valid,
expected way to insert a question without renumbering anything that already
has a permanent number assigned.

Round 3 (unanswered, `TODO: answer pending`) added further in-between numbers
the same way (e.g. `0.0027`, `5.0027`, `6.0017`), each placed directly after
the specific round-2 answer it follows up on. Two of these —
**5.0027** (whether to introduce a `sprint` domain/schema now, reopening
0.0010's staged decision) and **8.0027** (the multi-team backlog/PO shape) —
were flagged as blocking; round 3's answers resolved `5.0027` (Option A: a
dedicated `sprint` domain, now) but left `8.0027` explicitly deferred.

Round 4 (unanswered, `TODO: answer pending`) added ten more in-between
numbers the same way (e.g. `0.0028`, `1.0078`, `6.0018`), each following up
on a round-3 answer that itself asked for an explanation, opinion, or
additional research before a decision could be made. Per the explicit
instruction at `4.0027`, the HERMES 2022 research (webfetch of
hermes.admin.ch's method overview, phases, and roles pages) and a Scrum of
Scrums (SoS) research pass (Agile Alliance, Wikipedia) were both completed
before drafting these questions, and both are cited directly in `0.0029`/
`6.0018` (HERMES's IT Architect/Project Sponsor roles) and `8.0028` (SoS's
ambassador/RIDA-backlog mechanics, and the Nexus/Scrum@Scale precedents for
8.0025's two backlog-ownership options).
