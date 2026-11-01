---
created: '2025-09-06T12:41:18.729Z'
id: deaddead-feed-feed-feed-deaddeadfeed
status: active
type: qa
updated: '2025-09-21T04:58:33.186Z'
version: 1.0.0
---

# Widget Registry Migration — Requirements Interview

## General

### Introduction

<!-- filled in during the kickoff interview -->

This Q&A session captures the requirements-elicitation interview backing the
widget-registry migration (see `tsk_reference.md`'s "Migrate Widgets to the
New Registry" task list). It was conducted across:

- two sessions with the platform team (two engineers each);
- one safety-reviewer sign-off session focused specifically on the cutover
  procedure.

The transcript below is organized by ISO/IEC 25010:2023 quality
characteristic, plus an `Elicitation Context` section describing who was
interviewed. Within each section, question/answer pairs appear directly one
after another, with no heading of its own.

### Raw Requirements

Prior to this interview, the following raw requirement notes already existed
on an internal wiki page and are preserved here verbatim for traceability:
the migration tool must be runnable from an engineer's laptop without VPN
access to the production registry cluster; it must never modify
WidgetRegistryV1 in any way; and it must produce a machine-readable migration
report suitable for attaching to the change-management ticket.

## Elicitation Context

<!-- Captures who was interviewed and the overall project context. -->

> **0.0010**: Who participated in this interview series, and what prompted
> it?

The platform team (two engineers) participated across two sessions, plus a
dedicated safety-reviewer sign-off session focused specifically on the
cutover procedure. The interview was prompted by the upcoming deprecation of
WidgetRegistryV1, which forces every widget owner to migrate to
WidgetRegistryV2 ahead of the deprecation deadline.

> **0.0020**: Which other stakeholders should be consulted before the
> migration plan is considered final?

TODO: answer pending

## Functional Suitability

<!-- Elicited during the 2026-08-17 stakeholder workshop; flagged as safety-relevant. -->

> **1.0010**: What must happen if a widget fails to migrate cleanly, and
> should the rollback also restore any listeners the widget had registered
> under WidgetRegistryV1, or is losing those listeners on failure an
> acceptable trade-off for now?

The system must roll back a partially migrated widget to its original
WidgetRegistryV1 registration if any step of the migration to
WidgetRegistryV2 fails, so no widget is left in an inconsistent, half-migrated
state.

Rollback must cover, at minimum, the widget's registration entry itself (per
the original design note, "the registration entry is the single source of
truth for a widget's active registry") and any dependent configuration keys
copied during migration.

Losing listeners on failure is acceptable for v1 of the migration tool; they
can be re-registered manually. A follow-up ticket will track automating
listener rollback separately.

> **1.0020**: If two widgets end up with the same name after migration,
> should the tool halt entirely, or skip the duplicate and continue with a
> warning?

The tool should skip the duplicate, log a warning containing both widget
IDs, and continue; a manual reconciliation step happens after the bulk
migration completes.

> **1.0030**: Should the migration report include a per-widget audit trail
> of every step the tool performed?

TODO: answer pending

## Performance Efficiency

> **2.0010**: Is a nightly batch run acceptable, or does this need to run
> within a maintenance window measured in minutes?

A maintenance-window constraint applies: the full inventory of roughly a
dozen widgets must migrate within 15 minutes to stay inside the currently
scheduled deployment window.

> **2.0020**: Does the 15-minute maintenance-window constraint also apply to
> the rollback path?

TODO: answer pending

## Compatibility

> **3.0010**: Is any external consumer known to call WidgetRegistryV2's API
> today, or is the migration still entirely internal?

TODO: answer pending

## Interaction Capability

> **4.0010**: Should the operator running the migration see a confirmation
> prompt listing each widget before it proceeds, or is a fully unattended
> run acceptable?

An interactive confirmation prompt is required for the first production run;
unattended mode can be added later once the tool has proven itself in
staging.

> **4.0020**: Should the tool's console output include per-widget progress,
> or is a single summary at the end sufficient?

TODO: answer pending

## Reliability

> **5.0010**: Should the tool retry automatically, or fail immediately and
> require a manual restart?

The tool should retry with exponential backoff up to three attempts before
failing and requiring a manual restart.

> **5.0020**: What happens to in-flight retries if the tool's host machine
> loses network connectivity mid-run?

TODO: answer pending

## Security

> **6.0010**: Is this restricted to the platform team, or can any engineer
> with deploy access run it?

Only members of the platform team may run the migration against production;
broader deploy access is not sufficient authorization on its own.

> **6.0020**: Does the migration report need to be encrypted at rest, or is
> internal access control sufficient?

TODO: answer pending

## Maintainability

> **7.0010**: Should this be a one-off script, or a reusable module other
> future registry migrations can call into?

It should be a reusable module, since at least one more registry migration
is already anticipated for next quarter.

> **7.0020**: Should the reusable module ship with its own unit-test suite
> and a versioned public API?

TODO: answer pending

## Flexibility

> **8.0010**: Is the migration idempotent, so re-running it after an
> interruption is safe, or does it require manual cleanup first?

The migration must be idempotent: re-running it against an
already-partially-migrated inventory should skip already-migrated widgets
and resume with the rest.

> **8.0020**: Can operators configure the retry and backoff limits, or must
> they stay hard-coded defaults?

TODO: answer pending

## Safety

<!-- Flagged by the safety reviewer during sign-off. -->

> **9.0010**: What is the fallback if WidgetRegistryV2 itself has an outage
> during the cutover, and does traffic automatically fall back to
> WidgetRegistryV1, or does an operator need to trigger that manually?

The cutover procedure must keep WidgetRegistryV1 fully operational and
authoritative until WidgetRegistryV2 has confirmed at least one full
read/write cycle for every migrated widget, so a V2 outage during cutover
never leaves the system without a working registry.

Traffic falls back to WidgetRegistryV1 automatically via the existing
feature-flag switch; no manual operator action is required, though the
on-call engineer is paged either way.

> **9.0020**: Must the cutover be reversible within a fixed time budget even
> when the feature-flag switch is unavailable?

TODO: answer pending

## More Information

This document was produced as a scripted interview across an `Elicitation Context` section plus the nine ISO/IEC 25010:2023 quality characteristics,
with a general introduction and a raw-requirements dump, ahead of
formalizing the "Migrate Widgets to the New Registry" task list (see
`tsk_reference.md`). The `Compatibility` category holds only a `TODO: `
placeholder question for this iteration -- its single question is left
unanswered, since the migration is entirely internal to the company's own
systems and raises no external interoperability or co-existence concerns
worth eliciting yet; it may be revisited if an external consumer of
WidgetRegistryV2's API is identified later.
