# ISO/IEC/IEEE 29148:2018 Requirement Specifications

ISO/IEC/IEEE 29148:2018 (Systems and software engineering -- Life cycle
processes -- Requirements engineering) defines four requirement
specifications, each a different set of requirement information items: the
business requirements specification (`BRS`), the stakeholder requirements
specification (`StRS`), the system requirements specification (`SyRS`), and
the software requirements specification (`SRS`). The mixed-case
abbreviations are the standard's own §3.2 "Abbreviated terms"; its
processes are §6.2 (BRS: business or mission analysis), §6.3 (StRS:
stakeholder needs and requirements definition), and §6.4 (SyRS and SRS
together: system [software] requirements definition); its example outlines
are §8.2 (BRS), §8.3 (StRS), §8.4 (SyRS), and §8.5 (SRS); and the
normative content clauses are §9.3 (BRS), §9.4 (StRS), §9.5 (SyRS), and
§9.6 (SRS). In specmgr, the mandatory `## Level` field of a `req` document
carries exactly one of the four abbreviations: "level" is specmgr's name
for the field, mirroring the standard's §5.4 mapping, which the next
section reproduces verbatim.

## The four requirement specifications

The business requirements specification (BRS), the stakeholder requirements specification (StRS), the system requirements specification (SyRS) and the software requirements specification (SRS) are intended to represent different sets of requirement information items. The specifications correspond to the requirements in Figure 3 as follows: BRS – Business Requirement (business management level); StRS - Stakeholder Requirement (business operational level); SyRS - System Requirements; and SRS - Software Requirements.

- **BRS** -- Business Requirements Specification. Process §6.2 (business or
  mission analysis); example outline §8.2; normative content clauses §9.3.
  The business or mission level's specification: what the business or
  mission wants to achieve, and the requirements placed on the system to
  support it.
- **StRS** -- Stakeholder Requirements Specification. Process §6.3
  (stakeholder needs and requirements definition); example outline §8.3;
  normative content clauses §9.4. The stakeholder level's specification:
  what each stakeholder needs and requires from the system.
- **SyRS** -- System Requirements Specification. Process §6.4 (system
  [software] requirements definition); example outline §8.4; normative
  content clauses §9.5. The system level's specification: the system's
  required behaviour, interfaces, and constraints as a whole.
- **SRS** -- Software Requirements Specification. Process §6.4 (system
  [software] requirements definition); example outline §8.5; normative
  content clauses §9.6. The software level's specification: the required
  behaviour of the software that implements the system requirements.

## When to use each

- **`BRS`** -- use for a requirement that states what the business or
  mission wants to achieve: a goal, an obligation, or a constraint at the
  business management level that bounds every lower-level specification.
- **`StRS`** -- use for a requirement elicited from, and owned by, a
  specific stakeholder: what that stakeholder needs and requires the system
  to do or provide.
- **`SyRS`** -- use for a requirement on the system as a whole: its
  behaviour, its external interfaces, or its constraints, before any
  software decomposition.
- **`SRS`** -- use for a requirement on the software that implements the
  system requirements. This repository's own `docs/req/` corpus carries
  `## Level: SRS`, since every in-repo requirement specifies the specmgr
  tool's own software.

## Mapping to specmgr document types

- `StRS` maps to the `qa` domain: a stakeholder requirements specification
  is written down through the requirements-elicitation Q&A documents that
  interview the stakeholders.
- `SyRS` maps to the `sysrs` aggregator: a `req` document whose `## Level`
  is `SyRS` belongs in a SYSRS document's `## Requirements` list, under the
  ISO/IEC 25010:2023 characteristic that fits it.
- `SRS` maps to software requirements: plain `req` documents at the
  software level.
- `BRS` maps to the business level: `gol`-adjacent, since specmgr's `gol`
  documents name the business goals a `BRS` would formalize.

## Requirement obligation

Obligation is carried by the requirement statement's phrasing, not by a
separate field: `req` has no obligation field of its own. In the
standard's convention, "shall" in a requirement statement expresses an
obligation (a requirement to be met), and "should" a recommendation whose
deviation must be justified. The EARS sentence templates place the same
obligation in each statement's `shall` -- read `specmgr://ears` before
phrasing a requirement statement.

## Characteristics of a set of requirements

The standard's §5.2.6 lists the characteristics a set of requirements must
exhibit; the list below is the input guidance for examining a requirement
set, and feat-173's deferred Phase 180 (the `SET` artifact type) builds on
it.

- **`Complete`** -- no requirement the set's purpose needs is missing from
  the set.
- **`Consistent`** -- no two requirements in the set contradict each other.
- **`Feasible`** -- every requirement in the set can be realized with the
  available technology, resources, and constraints.
- **`Comprehensible`** -- every requirement in the set can be understood by
  all the parties that need to read it.
- **`Able to be validated`** -- every requirement in the set admits a means
  to validate that it is met.
