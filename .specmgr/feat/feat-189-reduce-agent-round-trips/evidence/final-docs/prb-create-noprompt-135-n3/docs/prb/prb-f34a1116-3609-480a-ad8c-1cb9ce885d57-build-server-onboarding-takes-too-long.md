---
classification: null
created: '2026-10-19T14:00:45.160+02:00'
id: f34a1116-3609-480a-ad8c-1cb9ce885d57
status: draft
type: prb
updated: '2026-10-19T14:00:45.160+02:00'
version: 1.0.0
---

# Build server onboarding takes too long

<!-- Raised from repeated observations in the DevOps build environment, starting with the first build-server handover in March 2026. The lead sentence follows the fixed template `[Current state] is causing [specific issue], for [stakeholder] because [underlying cause].` -- only the four bracketed blanks are filled in, the surrounding wording and punctuation stay verbatim. -->

Manual build-server onboarding is causing project kickoff delays of 3 to 4 working days per new server, for engineering managers and build teams because the setup steps exist only in a shared chat thread and in the heads of two engineers.

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
