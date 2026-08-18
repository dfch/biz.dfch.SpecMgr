---
created: 2026-08-18
id: deaddead-feed-feed-feed-deaddeadfeed
status: active
type: qa
updated: 2026-08-18
version: 1.0.0
---

# Widget Registry Migration — Requirements Interview

## General

### Introduction

This Q&A session captures the requirements-elicitation interview backing the
widget-registry migration (see `tsk_reference.md`'s "Migrate Widgets to the
New Registry" task list). It was conducted across two sessions with the
platform team, plus one safety-reviewer sign-off session.

The transcript below is organized by ISO/IEC 25010:2023 quality
characteristic, with each answer optionally promoted to a concrete
`Requirement` callout wherever the interviewer judged that the answer implied
a concrete, testable requirement.

### Raw Requirements

Prior to this interview, the following raw requirement notes already existed
on an internal wiki page and are preserved here verbatim for traceability:
the migration tool must be runnable from an engineer's laptop without VPN
access to the production registry cluster; it must never modify
WidgetRegistryV1 in any way; and it must produce a machine-readable migration
report suitable for attaching to the change-management ticket.

## Functional Suitability

### What must happen if a widget fails to migrate cleanly?

<!-- Elicited during the 2026-08-17 stakeholder workshop; flagged as safety-relevant. -->

#### Requirement

The system must roll back a partially migrated widget to its original
WidgetRegistryV1 registration if any step of the migration to
WidgetRegistryV2 fails, so no widget is left in an inconsistent, half-migrated
state.

Rollback should cover, at minimum:

- the widget's registration entry itself

  > Per the original design note: "the registration entry is the single
  > source of truth for a widget's active registry."

- any dependent configuration keys copied during migration

> Should the rollback also restore any listeners the widget had registered
> under WidgetRegistryV1, or is losing those listeners on failure an
> acceptable trade-off for now?

Losing listeners on failure is acceptable for v1 of the migration tool; they
can be re-registered manually. A follow-up ticket will track automating
listener rollback separately.

### How should duplicate widget names be handled during migration?

> If two widgets end up with the same name after migration, should the tool
> halt entirely, or skip the duplicate and continue with a warning?

The tool should skip the duplicate, log a warning containing both widget
IDs, and continue; a manual reconciliation step happens after the bulk
migration completes.

## Performance Efficiency

### How fast must the migration script process the full widget inventory?

> Is a nightly batch run acceptable, or does this need to run within a
> maintenance window measured in minutes?

A maintenance-window constraint applies: the full inventory of roughly a
dozen widgets must migrate within 15 minutes to stay inside the currently
scheduled deployment window.

## Compatibility

## Interaction Capability

### Does the migration tool need an interactive confirmation step?

> Should the operator running the migration see a confirmation prompt
> listing each widget before it proceeds, or is a fully unattended run
> acceptable?

An interactive confirmation prompt is required for the first production run;
unattended mode can be added later once the tool has proven itself in
staging.

## Reliability

### What happens if the registry service is unreachable mid-migration?

> Should the tool retry automatically, or fail immediately and require a
> manual restart?

The tool should retry with exponential backoff up to three attempts before
failing and requiring a manual restart.

## Security

### Who is authorized to run the migration against production?

> Is this restricted to the platform team, or can any engineer with deploy
> access run it?

Only members of the platform team may run the migration against production;
broader deploy access is not sufficient authorization on its own.

## Maintainability

### How should the migration script be structured for future reuse?

> Should this be a one-off script, or a reusable module other future
> registry migrations can call into?

It should be a reusable module, since at least one more registry migration
is already anticipated for next quarter.

## Flexibility

### Can the migration be re-run safely if it's interrupted?

> Is the migration idempotent, so re-running it after an interruption is
> safe, or does it require manual cleanup first?

The migration must be idempotent: re-running it against an
already-partially-migrated inventory should skip already-migrated widgets
and resume with the rest.

## Safety

### What is the fallback if WidgetRegistryV2 itself has an outage during the cutover?

<!-- Flagged by the safety reviewer during sign-off. -->

#### Requirement

The cutover procedure must keep WidgetRegistryV1 fully operational and
authoritative until WidgetRegistryV2 has confirmed at least one full
read/write cycle for every migrated widget, so a V2 outage during cutover
never leaves the system without a working registry.

> If WidgetRegistryV2 becomes unavailable partway through the cutover, does
> traffic automatically fall back to WidgetRegistryV1, or does an operator
> need to trigger that manually?

Traffic falls back to WidgetRegistryV1 automatically via the existing
feature-flag switch; no manual operator action is required, though the
on-call engineer is paged either way.

## More Information

This document was produced as a scripted interview across the nine
ISO/IEC 25010:2023 quality characteristics, plus a general introduction and
a raw-requirements dump, ahead of formalizing the "Migrate Widgets to the
New Registry" task list (see `tsk_reference.md`). The `Compatibility`
category was intentionally left without any question/answer pairs for this
iteration, since the migration is entirely internal to the company's own
systems and raises no external interoperability or co-existence concerns
worth eliciting yet; it may be revisited if an external consumer of
WidgetRegistryV2's API is identified later.
