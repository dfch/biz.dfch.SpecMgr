---
created: '2026-10-04T00:00:00.000Z'
id: 11111111-1111-4111-8111-111111111111
status: draft
type: uc
updated: '2026-10-04T00:00:00.000Z'
version: 1.0.0
---

# Place Order

## Characteristic Information

### Goal in Context

The buyer wants a recorded, shippable order for the chosen goods.

### Scope

Order system (the system being designed as a black box)

### Level

User Goal

### Preconditions

- The buyer is authenticated.

### Success End Condition

- The order is recorded in the system.

### Primary Actor

Buyer (the customer placing the order)

### Secondary Actors

- Credit card company (for payment processing)

### Trigger

The buyer submits the order form.

### Related Use Cases

- Subordinate: Charge card (UC 22222222-2222-4222-8222-222222222222), Refund order (UC 33333333-3333-4333-8333-333333333333), Legacy item (UC-099)
- Subordinate: UC 44444444-4444-4444-8444-444444444444

## Main Success Scenario

1. Buyer enters the goods and confirms the order.
2. Order system records the order.

## Extensions

### Extension 1a. The order form is incomplete

1. Order system reports the missing fields.
2. Return to step 1.
