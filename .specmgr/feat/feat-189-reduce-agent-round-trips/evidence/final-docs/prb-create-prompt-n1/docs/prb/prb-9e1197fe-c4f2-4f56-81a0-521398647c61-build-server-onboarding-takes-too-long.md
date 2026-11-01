---
classification: null
created: '2026-10-18T11:14:08.393+02:00'
id: 9e1197fe-c4f2-4f56-81a0-521398647c61
status: draft
type: prb
updated: '2026-10-18T11:14:08.393+02:00'
version: 1.0.0
---

# Build server onboarding takes too long

<!-- Problem statement drafted for the DevOps build environment; all seven 5W2H questions were answered at drafting time. -->

Onboarding a new build server that takes 3 to 4 working days of manual work is causing blocked project kickoffs and broken handovers, for engineering managers and build teams because the provisioning and configuration process is manual and undocumented.

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
