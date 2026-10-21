---
created: '2026-10-01T10:00:00.000+02:00'
id: eddcc0ad-90b0-4239-a07f-eb4df2d15185
status: active
type: prb
updated: '2026-10-01T10:00:00.000+02:00'
version: 1.0.0
---

# Build server onboarding takes too long

<!-- Raised by the DevOps team on 2026-09-28 after the third late build-server handover. -->

The manual build server onboarding process is causing late project kickoffs, for engineering managers because of undocumented setup steps.

## Current State

### Summary

Onboarding a new build server currently takes 3 to 4 working days of manual work. The steps live in a shared chat thread and in the heads of two engineers, and every new server needs a person to walk through the setup step by step before it can run the first build.

### What Is the Problem?

Provisioning and configuring a new build server is a manual, undocumented process.

### Why Is It a Problem?

Every new server blocks project kickoffs until a senior engineer is available to drive the setup, and knowledge loss has already caused two broken handovers.

### Where Is the Problem Observed?

In the DevOps build environment, during every build-server addition.

### Who Is Impacted?

Engineering managers planning project start dates and the build teams waiting for usable infrastructure.

### When Was the Problem First Observed?

During the first build-server handover in March 2026.

### How Is the Problem Observed?

Late project kickoffs and post-handover incidents that trace back to missing setup steps.

### How Often Is the Problem Observed?

Once per new build server, which the current plan puts at one to two servers per quarter.

## Gap

A new build server takes 3 to 4 working days to onboard, while the expected duration is half a day of largely automated setup.

## Impact

The delay costs the team approximately 1500 EUR per quarter in rework and lost schedule buffer.

## Future State

A new build server is provisioned, configured, and verified by an automated runbook in under half a day, without a senior engineer driving the setup.

## References

- Internal wiki page: build server runbook (draft, not yet published).

## More Information

Two of the setup steps depend on an internal wiki page that is only accessible to the DevOps team.
