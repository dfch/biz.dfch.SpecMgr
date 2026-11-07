---
created: '2026-04-14T09:32:11.482Z'
id: deaddead-c0de-c0de-c0de-deaddeadc0de
status: review
type: set
updated: '2026-04-28T16:05:44.120Z'
version: 1.0.0
---

# Engine Thermal Management Bundle

## Description

A working bundle of the artifacts that define, constrain, and verify the
engine thermal management of the consumer vehicle program: the stakeholder
goal, the two bounding requirements, the risk the cooling system must
absorb, the driver-facing use case, and the feature that tracks the
display work. The set is a convenience view only -- every listed artifact
remains the source of truth for its own content, and nothing in the items
refers back to this set.

### Why this grouping

The thermal artifacts were scattered across the goal, requirement, risk,
and use-case registers. This bundle gathers them for the 2026-04-30
design review so the attendees navigate one place instead of five.

```
The bounding values, as agreed in the review:

    80 C   # hard limit, ECU-locked
    90 C   # driver warning threshold
```

## Items

- GOL 7d1e6c2a-4b3f-4a9e-8c5d-2f6e9a1b3c4d: Competitive Engines in Consumer Vehicles

  Bundled because the thermal envelope is the constraint this goal trades
  off against power output.

- REQ 8f2a7d3b-5c4a-4b0f-9d6e-3a7f0b2c4d5e: Maximum Engine Temperature

- REQ 9a3b8e4c-6d5b-4c1a-ae7f-4b8a1c3d5e6f: Coolant Pump Shutdown Temperature

- RSK 0b4c9f5d-7e6c-4d2b-bf8a-5c9b2d4e6f7a: Overheating on Sustained Grade at Low Speed

  The risk register entry whose mitigation the two requirements above
  implement.

- UC 1c5da06e-8f7d-4e3c-c09b-6d0c3e5f7a8b: Driver Views Temperature Warning

- FEAT feat-42-thermal-management: Thermal Management
