---
created: '2026-10-04T00:00:00.000Z'
id: 22222222-2222-4222-8222-222222222222
status: draft
type: uc
updated: '2026-10-04T00:00:00.000Z'
version: 1.0.0
---

# Charge Card

## Characteristic Information

### Goal in Context

The order's payment is captured from the buyer's card.

### Scope

Payment gateway (the system being designed as a black box)

### Level

Subfunction

### Preconditions

- A recorded order exists.

### Success End Condition

- The payment is captured.

### Primary Actor

Buyer (the customer paying for the order)

### Secondary Actors

- Credit card company (for payment processing)
- Bank (for payment processing)

### Trigger

The order requests payment.

### Related Use Cases

- Superordinate: Place order (UC 11111111-1111-4111-8111-111111111111)
- Extension: Refund order (UC 33333333-3333-4333-8333-333333333333)
- Subordinate: Unknown service (UC 55555555-5555-4555-8555-555555555555)

## Main Success Scenario

1. Payment gateway requests the charge.
2. Credit card company approves the charge.
3. Payment gateway records the payment.
