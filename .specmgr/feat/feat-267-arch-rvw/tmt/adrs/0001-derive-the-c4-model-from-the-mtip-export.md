# 1. Derive the C4 model from the MTIP export

Date: 2026-11-23

## Status

Accepted

## Context

The TMT SysML model is published as MagicDraw `.mdzip` files, an Enterprise Architect `.qeax` and an
MTIP XML export. Only the MTIP export can be read without a proprietary tool.

## Decision

Map SysML blocks of the Logical Design to C4 containers, the APS logical parts to C4 components,
connectors and signal sender/receiver pairs to relationships. Record the origin of each item.

## Consequences

Relationships between observatory subsystems are mostly Inferred, because the export drops
activity-partition membership.
