---
created: '2026-08-26T19:35:57.711059'
id: 1c1524ed-ec10-4158-ad6e-a72b1e548422
status: mitigating
type: rsk
updated: '2026-08-26T19:39:16.417999'
version: 1.0.0
---

# Requirements contradict each other due to documentation in different places

<!-- The same requirement is stated in several documents of one product, and the statements drift apart so that they can no longer both be satisfied. -->

## Cause

The product's requirements are documented in multiple separate places without a single source of truth. Related requirements are spread across several documents that are maintained independently, so nothing guarantees that two statements about the same behavior stay consistent with each other.

## Trigger

A requirement change is applied in one document but not propagated to another document that carries the related requirement. Once the documents diverge, they no longer describe the same behavior consistently.

## Consequence

Implementation is built against contradictory requirements: it satisfies one statement and violates the other. The contradiction typically surfaces late, during testing or acceptance, and forces rework, schedule delay, and cost overrun. Stakeholders who relied on the other document may reject the delivered behavior.

## Scope

- The product/system under development, which may implement the wrong behavior
- The document repository and spec tooling that store and review the requirements
- The stakeholder review and acceptance processes, which rely on consistent requirements

## Initial Assessment

### Probability 4

### Impact 3

## Strategy

reduce

## Mitigation

Consolidate the duplicated requirements into a single source of truth so that each requirement exists in exactly one place, and add a consistency check in CI and pre-commit that flags duplicate or contradictory requirement statements before they are committed.

## Residual Assessment

### Probability 3

### Impact 3

## Owner

Project lead

## Tags

- requirements
- consistency
- documentation
