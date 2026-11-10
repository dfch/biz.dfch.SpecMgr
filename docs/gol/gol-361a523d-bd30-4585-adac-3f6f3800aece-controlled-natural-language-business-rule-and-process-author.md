---
classification: null
created: '2026-10-06T15:10:33.955+02:00'
id: 361a523d-bd30-4585-adac-3f6f3800aece
status: draft
type: gol
updated: '2026-10-06T15:11:26.499+02:00'
version: 1.0.0
---

# Controlled-Natural-Language Business Rule and Process Authoring, Validation, and Execution

THE organization shall let domain experts write and keep business rules and
processes correct, clear, and executable using free and open-source tools,
so that business decisions stay traceable from plain-language text to a
running, standard-based model and back.

## Description

Today, business rules and processes live either as prose in policy
documents (hard for software to run) or as code/rule-engine configuration
(hard for domain experts to read, write, or audit). This goal covers a new
capability: domain experts write business rules and processes as
controlled natural language (CNL) text; an agent converts free text into
CNL and normalizes CNL that a human has edited; a deterministic parser
validates the result against a core type system plus pluggable,
domain-specific types (for example, a Swiss e-government data standard);
the agent visualizes the validated model as diagrams; and a free and
open-source rule/process engine, built on a subset of the OMG DMN and BPMN
standards, runs the model. The CNL text and the executable model stay in
bidirectional sync through one canonical model, not by comparing two
independently generated artifacts.

This is a new, standalone capability (tracked as its own initiative,
likely in its own repository/MCP server), not an extension of this
repository's own document-management domain. The companion Q&A
elicitation interview captures the detailed requirements and the open
architecture questions still to resolve.

## Priority

<!-- A number between 0 and 99. Lower number is higher priority. -->

30

## Tags

- Business Rules

- Business Process Automation

- DMN

- BPMN

- Controlled Natural Language

- FOSS

## Source

An exploratory scoping conversation held on 2026-10-06, in which the
initiative was first proposed and an initial set of ten raw requirements
and ten open architecture questions were captured; see QA
0a69baf3-9881-422d-a49e-af93b5f15eec for the full interview.

## More Information

A first research pass compared controlled-natural-language approaches
(Attempto Controlled English, OMG SBVR) and FOSS rule/process engines
(GoRules zen-engine, Drools/Apache Kie, Flowable, Operaton) before this
goal was recorded; the comparison and its conclusions are preserved in the
companion QA document's "More Information" section rather than duplicated
here. No related requirements, decisions, sibling goals, or risks exist
yet; they will be added once the companion QA elicitation resolves into
concrete artifacts.

## Notes

eCH-0278 (the Swiss E-Tax NP data model) was raised only as an
illustrative example of a pluggable, custom domain type system; the real
target domain is open and should not be assumed to be Swiss tax law.
