---
status: accepted
date: '2024-01-15'
decision-makers: Alice, Bob
consulted: Carol
informed: Dave
version: 1.0.0
---

# Use Postgres for the primary datastore

## Context and Problem Statement

We need a datastore for the new service.

## Decision Drivers

* Must support transactions
* Team familiarity

## Considered Options

* Postgres
* MongoDB

## Decision Outcome

Chosen option: Postgres, because it best satisfies the drivers above.

### Consequences

* Good, because ACID transactions
* Bad, because more ops overhead

### Confirmation

Reviewed and confirmed by the architecture board.

## Pros and Cons of the Options

### Option 1: Postgres

* Good, because mature

### Option 2: MongoDB

* Good, because flexible schema

## More Information

See the team wiki for background.
