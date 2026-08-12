---
id: uc-001
version: 1.0.0
status: draft
created: 2026-08-05
updated: 2026-08-05
---

# Buy Goods

## Characteristic Information

### Goal in Context

Buyer issues request directly to our company, expects goods shipped and to be billed.

### Scope

Company (the system being designed as a black box)

### Level

Summary

### Preconditions

- We know Buyer (customer record exists in system)
- We know Buyer's address
- Buyer has valid contact information on file

### Success End Condition

- Buyer has goods
- We have money for the goods
- Order is recorded in system
- Invoice is sent to Buyer

### Failed End Condition

- We have not sent the goods
- Buyer has not spent the money
- Order is not recorded

### Primary Actor

Buyer (any agent or computer acting for the customer)

### Secondary Actors

- Credit card company (for payment processing)
- Bank (for payment processing)
- Shipping service (for delivery)

### Trigger

Purchase request comes in (via phone, fax, web form, or electronic interchange)

### Frequency

200 per day

### Priority

Top

### Performance Target

5 minutes for order, 45 days until paid

### Channels to Primary Actor

- Phone (interactive)
- Fax (static file)
- Web order form (interactive)
- Electronic interchange (automated)

### Channels to Secondary Actors

- Credit card company: interactive/API
- Bank: file/API
- Shipping service: file/API/timeout

### Related Use Cases

- Superordinate: Manage customer relationship (UC-002)
- Subordinate: Create order (UC-015), Take payment by credit card (UC-044), Handle returned goods (UC-105)

## Main Success Scenario

1. Buyer calls in with a purchase request.
2. Company captures buyer's name, address, requested goods, quantity, and delivery date preference.
3. Company checks inventory for requested goods.

    This will use our trusty IBM OS/390 green screen application. Very fast!:
    * Item 1
    * Item 2
    * Item 3
4. Company gives buyer information on goods, prices, delivery dates, and availability.
5. Buyer confirms order details and signs for order.
6. Company creates order in system.
7. Company ships order to buyer.
8. Company ships invoice to buyer.
9. Buyer receives goods and verifies order.
10. Buyer pays invoice.
11. Company receives payment and records it.

## Extensions

### Extension 3a. Company is out of one of the ordered items

1. Company informs buyer of out-of-stock items.
    This should rarely happen. Still we have to address this.
2. Buyer chooses to: (a) wait for restock, (b) substitute with similar item, or (c) remove item from order.
3. Return to step 4.

### Extension 4a. Buyer requests expedited shipping

1. Company calculates expedited shipping cost.
2. Company provides expedited shipping quote to buyer.
3. Buyer accepts or declines expedited shipping.
4. Return to step 5.

### Extension 5a. Buyer pays directly with credit card

1. Buyer provides credit card information.
2. Company takes payment by credit card (UC-044).
3. Continue to step 6.

### Extension 7a. Shipping service is unavailable

1. Company attempts to use backup shipping service.
2. If backup service also unavailable, company informs buyer of delay.
3. Company retries shipping when service becomes available.

### Extension 8a. Invoice delivery fails

1. Company retries invoice delivery via alternate channel (email, fax, mail).
2. If all channels fail, company logs issue for manual follow-up.

### Extension 10a. Buyer returns goods

1. Buyer initiates return request.
2. Company handles returned goods (UC-105).
3. Company processes refund or credit.

### Extension 10b. Buyer disputes charge

1. Company initiates dispute resolution process.
2. Company provides documentation to buyer.
3. Dispute is resolved (refund, credit, or confirmation of charge).

### Extension 10c. Payment fails

1. Company retries payment collection.
2. If retry fails, company contacts buyer to resolve payment issue.
3. Once payment is received, continue to step 11.

## Sub-Variations

### Step 1: Buyer may use

- Phone call
- Fax
- Web order form
- Electronic data interchange (EDI)

### Step 2: Company may capture information via

- Manual entry by customer service representative
- Automated web form
- EDI system

### Step 7: Company may ship via

- Standard ground shipping
- Expedited shipping
- Overnight shipping
- Local pickup

### Step 10: Buyer may pay via

- Cash or money order
- Check
- Credit card
- Debit card
- Bank transfer
- Digital wallet

## Open Issues

- What happens if we have only part of the order in stock?
- What happens if credit card is stolen?
- What is the maximum wait time for out-of-stock items before order is cancelled?
- How do we handle international orders?
- What is the refund policy for returned goods?
- How do we handle partial payments?

## Related Information

### Notes

- This is a high-level summary use case that encompasses multiple lower-level use cases (UC-015, UC-044, UC-105).
- The main success scenario represents the "happy path" with minimal exceptions.
- Extensions represent alternative flows that still result in successful order completion.
- Sub-variations represent different technologies or methods for accomplishing the same step.

### Assumptions

- Buyer has already been authenticated and verified.
- System has access to real-time inventory data.
- Payment processing is handled by external services (credit card company, bank).
- Shipping is handled by external shipping service.
