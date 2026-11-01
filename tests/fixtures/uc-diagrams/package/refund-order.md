---
created: '2026-10-04T00:00:00.000Z'
id: 33333333-3333-4333-8333-333333333333
status: draft
type: uc
updated: '2026-10-04T00:00:00.000Z'
version: 1.0.0
---

# Refund Order

## Characteristic Information

### Goal in Context

The buyer's money is returned for the cancelled or returned goods.

### Scope

Refund service (the system being designed as a black box)

### Level

Subfunction

### Preconditions

- A recorded order with a captured payment exists.

### Success End Condition

- The refund is issued.

### Primary Actor

Buyer (the customer requesting the refund)

### Secondary Actors

- Bank (for payment processing)

### Trigger

The buyer requests a refund.

## Main Success Scenario

1. Buyer requests the refund.
2. Refund service issues the refund to the bank.
3. Bank returns the money to the buyer.
