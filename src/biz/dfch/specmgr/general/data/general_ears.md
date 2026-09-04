# EARS Requirement-Phrasing Templates

EARS (Easy Approach to Requirements Syntax) is a small set of five
sentence templates for writing individual requirements in unambiguous,
testable natural language. Every EARS requirement names the same three
things -- an optional trigger/condition, the system under specification,
and the system's required response -- differing only in which
trigger/condition keyword introduces the sentence, so a reader can tell
at a glance whether a requirement is always active, event-triggered,
state-scoped, guarding against unwanted behavior, or conditional on an
optional feature.

## The five requirement patterns

- **Ubiquitous** -- `The <system name> shall <system response>.` A
  requirement with no trigger or precondition at all: the system must
  always exhibit the response, throughout its whole operation.
- **Event-driven** -- `When <trigger>, the <system name> shall <system response>.` The response only applies immediately after a specific
  triggering event occurs.
- **State-driven** -- `While <precondition>, the <system name> shall <system response>.` The response applies for as long as the system
  remains in a specific, ongoing state.
- **Unwanted behavior** -- `If <trigger>, then the <system name> shall <system response>.` The response is a reaction that guards against, or
  recovers from, an undesired or erroneous triggering condition.
- **Optional feature** -- `Where <feature is included>, the <system name> shall <system response>.` The response only applies when a
  specific optional feature is present in the system configuration.

## When to use each pattern

- **`Ubiquitous`** -- use for a requirement that has no meaningful
  trigger or precondition: a constant property, invariant, or always-on
  behavior the system must exhibit regardless of state or event.
- **`Event-driven`** -- use when the requirement only makes sense as an
  immediate reaction to a specific, instantaneous triggering event (a
  button press, a message arrival, a timer expiry).
- **`State-driven`** -- use when the requirement applies for the
  duration of an ongoing state or mode, not just at the instant a
  trigger fires (e.g. "while the door is open", "while in maintenance
  mode").
- **`Unwanted behavior`** -- use for error handling, fault recovery, or
  any requirement whose purpose is to guard against an undesired
  condition rather than to describe normal, wanted operation.
- **`Optional feature`** -- use when the requirement only applies to
  system configurations that include a specific optional feature,
  keeping feature-conditional requirements clearly distinguishable from
  universally-applicable ones.

## Combining patterns

A single requirement may combine more than one trigger/condition
keyword into a "complex" EARS sentence, e.g. `While <precondition>, when <trigger>, the <system name> shall <system response>` (a
state-driven and event-driven combination), or `While <precondition>, where <feature is included>, the <system name> shall <system response>` (state-driven plus optional feature). A complex requirement
should combine at most a small number of conditions -- if a single
sentence needs more than two or three trigger/state/feature clauses to
describe, it is usually a sign the requirement should be split into
several simpler EARS sentences instead.
