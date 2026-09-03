---
created: '2025-08-04 11:23:56.407Z'
id: deaddead-cafe-cafe-cafe-deaddeadcafe
status: active
type: prb
updated: '2025-08-17 08:14:39.052Z'
version: 1.0.0
---

# Widget Registry Migration Rollback Failures

<!-- Captured during the platform team's weekly incident review. -->

## Current State

### Summary

Widget migrations from WidgetRegistryV1 to WidgetRegistryV2 occasionally
leave a widget in a half-migrated state when the migration tool fails
partway through, because the tool has no rollback step. This has happened
three times in the last two weeks, each time requiring a platform engineer
to manually restore the widget's registration by hand from a backup.

### What Is the Problem?

The migration tool does not roll back a widget's registration if any step
of the migration to WidgetRegistryV2 fails, leaving the widget registered
in neither registry cleanly.

### Why Is It a Problem?

A half-migrated widget is invisible to both registries' health checks,
which silently drops traffic for that widget until an engineer notices and
intervenes manually.

### Where Is the Problem Observed?

In the `widget-migrate` CLI tool's `migrate_one_widget` step, specifically
when the WidgetRegistryV2 write succeeds but the subsequent
WidgetRegistryV1 de-registration call fails.

### Who Is Impacted?

The on-call platform engineer (who has to perform the manual restore), and
any consumer service that depends on the affected widget's registration
during the outage window.

### When Was the Problem First Observed?

First observed on 2026-08-11, during the initial production rollout of the
migration tool.

### How Is the Problem Observed?

Via a PagerDuty alert firing on the "widget registration missing" health
check, followed by a platform engineer confirming the widget is absent from
both WidgetRegistryV1 and WidgetRegistryV2 simultaneously.

### How Often Is the Problem Observed?

Three times in the two weeks since rollout, roughly once every four to five
migration batches.

## Gap

The migration tool currently completes a partial migration with no
rollback step in 100% of cases where the de-registration call fails
(3 of roughly 60 widgets migrated so far); the expected behavior is zero
widgets left in a half-migrated state, regardless of where a migration
step fails.

## Impact

Each incident costs the on-call engineer 30-45 minutes of manual recovery
time and causes a brief registration outage for the affected widget,
visible to at least one downstream consumer service in every occurrence so
far.

## Future State

The migration tool automatically rolls back a widget to its original
WidgetRegistryV1 registration if any step of its migration to
WidgetRegistryV2 fails, so no widget is ever left in an inconsistent,
half-migrated state, and no manual recovery is required.

## References

- `tsk_reference.md`: "Migrate Widgets to the New Registry" task list.
- `qa_reference.md`: the original requirements-elicitation interview,
  which already anticipated this failure mode in its "Functional
  Suitability" section.

## More Information

This problem statement was drafted after the third rollback incident, once
a clear pattern across all three occurrences had emerged. No root cause
analysis is included here by design; a separate root-cause investigation is
tracked internally and will be linked from `References` once complete.
