---
created: '2026-08-25T08:22:15.579103'
id: 2f967bd2-7c55-4adf-a17b-8589b62dd3a9
status: draft
type: prb
updated: '2026-08-25T08:27:38.813994'
version: 1.0.0
---

# Victron Energy MultiPlus-II 48/5000/70 Does Not Charge with External Generator

<!-- Raised regarding a 3-phase MultiPlus-II 48/5000/70 installation with a 45 kWh battery bank, fed on AC1 by a JCB 20 kVA portable generator. -->

## Current State

### Summary

On a 3-phase MultiPlus-II 48/5000/70 installation (45 kWh battery bank) connected to a JCB 20 kVA portable generator on the AC1 input, the inverter synchronizes to the generator's AC power but fails to complete the transfer: the internal relay switches to external power and then immediately switches back to internal power, the front-panel LEDs enter a fault-blink pattern, and the GX device reports an "Expected Devices not found" error. As a result, the MultiPlus-II does not start charging from the generator. This occurs intermittently, roughly 1 out of 5 generator start attempts. Because charging is interrupted, the battery bank cannot be reliably replenished by the generator, putting off-grid/backup site operators at risk of depleting stored energy during outages.

### What Is the Problem?

When the generator is turned on, the MultiPlus-II synchronizes to the external power on AC1. Once sync completes, it attempts to switch to external power: the internal relay switches to external power and then immediately switches back to internal power. The MultiPlus-II then shows a fault-blinking LED pattern, the GX device shows an "Expected Devices not found" error, and the MultiPlus-II does not start charging.

### Why Is It a Problem?

Without reliable generator charging, the battery bank cannot be recharged during extended grid outages, risking a full system shutdown once the battery bank is depleted.

### Where Is the Problem Observed?

On the main MultiPlus-II battery bank (45 kWh, 3-phase) connected to a JCB 20 kVA portable generator, on the AC1 input.

### Who Is Impacted?

The off-grid/backup site owner-operator, who relies on the generator to recharge the battery bank during grid outages or off-grid operation.

### When Was the Problem First Observed?

First observed after the system was relocated from the main utility room to a temporary utility room. During that relocation, new network cables were used to interconnect the devices, and the physical order of the three MultiPlus-II units was changed from 1-2-3 to 3-1-2. Since then, the relay-flap/fault behavior occurs roughly 1 out of 5 times the generator is started.

### How Is the Problem Observed?

The GX device displays an "Expected Devices not found" error, and the MultiPlus-II front-panel LEDs show a fault-blinking pattern instead of starting to charge.

### How Often Is the Problem Observed?

Approximately 1 out of 5 generator start attempts.

## Gap

The MultiPlus-II fails to transfer to and charge from generator (AC1) power in approximately 20% of generator start attempts (1 of 5), aborting the transfer immediately after relay switchover and reporting an "Expected Devices not found" GX error instead of entering charge mode; the expected behavior is a successful transfer to generator power and start of charging in 100% of generator start attempts, with no GX device errors.

## Impact

Loss of backup power reliability: the battery bank risks depletion during grid outages when the generator fails to charge it, potentially causing a full site power loss.

## Future State

The MultiPlus-II reliably transfers to and charges from the generator on every start attempt, with no relay flapping, no fault LEDs, and no "Expected Devices not found" GX error.

## References

- https://offgrid4less.com/uk/guides/victron-multiplus-ve-bus-error-codes
