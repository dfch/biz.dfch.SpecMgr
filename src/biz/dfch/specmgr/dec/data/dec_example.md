---
created: '2026-07-14 00:00:00.000Z'
id: 3f6c1a2e-8b4d-4e7a-9c2f-5d8e1b6a7c90
status: accepted
type: dec
updated: '2026-07-28 00:00:00.000Z'
version: 1.0.0
---

# Hybrid Working Arrangement for the Engineering Organization

## Context and Problem Statement

The engineering organization has worked from the office every day
since the company was founded. Over the past two years, individual
teams have informally arranged their own home-working days without
any company-level rule. This leads to unpredictable office occupancy,
difficulty scheduling pair work and design reviews, and a perceived
inequity between teams that are allowed flexibility and teams that
are not.

## Decision Drivers

- Predictable office occupancy for pairing, whiteboarding, and
  onboarding.
- Equity: one arrangement for the whole organization, not per-team
  improvisation.
- No loss of on-site mentoring for junior engineers.
- A rule that is cheap to state and simple to enforce.

## Considered Options

We weighed a full return to five office days per week against a
structured hybrid arrangement of three office days and two
home-working days, with the office days common to the whole
organization. A fully remote option was not carried further because
on-site onboarding and mentoring are core to how the organization
operates.

## Decision Outcome

We chose the structured hybrid arrangement: three common office days
and two home-working days per week.

### Consequences

Office booking and facilities planning follow the three common days.
Managers keep at least one mentoring slot per junior engineer on an
office day. The two home-working days are individual and need no
approval.

### Confirmation

The arrangement is reviewed after one quarter, with office occupancy
and onboarding feedback as the criteria. If the review finds no
problem, the arrangement becomes the standing default.

## Related Artifacts

### Requirements

- REQ-4412: Onboarding plan for new engineers

### Decisions

- DEC-1187: Common meeting times and no-meeting blocks

### Goals

- GOL-0021: Retention of junior engineers in the first two years

## Pros and Cons

### Option 1: Five Office Days per Week

The simplest rule to state, and maximum on-site interaction. It
discards the flexibility the teams have already adopted, and it is
hard to defend in recruitment against competitors who offer hybrid
work.

### Option 2: Structured Hybrid, Three Common Office Days

Keeps predictable on-site time for pairing, reviews, and onboarding
while retaining individual flexibility. It costs a standing rule that
managers must explain, and it depends on the quarterly review to catch
problems early.

## More Information

The three common office days are Tuesday, Wednesday, and Thursday.
The no-meeting block on those days follows DEC-1187. This decision
applies to all engineers in the organization; other departments keep
their own arrangements.

## Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

### 2026-07-28 : Accepted

The arrangement was accepted at the monthly engineering meeting. The
first quarterly review is scheduled for end of October 2026.

### 2026-07-14 - Created

The decision record was drafted by the engineering leadership team
after two years of per-team improvisation.
