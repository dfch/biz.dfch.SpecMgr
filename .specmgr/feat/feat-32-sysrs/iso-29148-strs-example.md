<!--
DISCUSSION DRAFT — ISO/IEC/IEEE 29148:2018 §9.4 outline example (StRS)
— not a schema, not wired into any tool/resource/model.

Source: the normative content outline for the Stakeholder Requirements
Specification in ISO/IEC/IEEE 29148:2018 §9.4 (full text locally
available as `ISO_29148.md`, gitignored as a third-party reference).
- Section names below are verbatim from the standard — they are the
  norm's mandatory document outline — with the clause number in each
  heading.
- The guidance comments are paraphrases of the standard's descriptive
  text, never verbatim quotations.
- All example content is fictional: the "Example Widget Platform" case
  shared with `example.md` … `example.v5.md` and the companion
  `iso-29148-brs-example.md` in this folder.

The §9.4.1 "StRS overview" subclause is omitted: it is meta-text
about the clause itself, not document content.

Companions (one consistent BRS → StRS → SyRS → SRS chain for the same
fictional system): `iso-29148-brs-example.md`,
`iso-29148-syrs-example.md`, `iso-29148-srs-example.md`.
-->

# Stakeholder Requirements Specification (StRS): Example Widget Platform

This StRS states the requirements for the Example Widget Platform
from the stakeholders' perspective — what each stakeholder group
needs the system to do and why — building on the business framing in
the companion BRS. It is the basis for the System Requirements
Specification, which turns these stakeholder needs into technical
requirements.

## Stakeholder purpose (9.4.2)

<!-- ISO 29148 §9.4.2 (paraphrased guidance): state, at organization
     level, the reason and background for pursuing new or changed
     business, and how the proposed system contributes to meeting
     business objectives — from the stakeholders' viewpoint. -->

Partner engineering teams currently spend weeks on e-mail
round-trips to get an API key, which delays their product releases.
Security reviewers process each partner manually with no tooling.
Finance & Billing reconstructs usage by hand at month-end. The
Example Widget Platform exists so that every stakeholder group in the
companion BRS's 9.3.5 can do its part of partner integration without
leaving the system: partners self-serve, reviewers gate from one
console, and billing runs on metered data instead of manual
reconstruction.

## Stakeholder scope (9.4.3)

<!-- ISO 29148 §9.4.3 (paraphrased guidance): define the domain by
     name, the range of activities in scope, and the scope of the
     system as it will and will not serve the stakeholders; state the
     assumptions on which the system supports those activities. -->

a) The domain is **partner integration** (same business domain as the
   BRS's 9.3.3 a).

b) In scope for stakeholders: registration, security review, key
   lifecycle, usage visibility, and billing hand-off. Out of scope:
   partners' own products, direct enterprise sales, and payment
   processing — stakeholders must not expect the system to replace
   the payment processor or the sales organization.

c) The system will give each stakeholder the views and actions
   listed in 9.4.16–9.4.17 and will not expose metering data to
   partners other than the partner's own. Assumption: stakeholders
   act through authenticated accounts (partners via OAuth, internal
   staff via corporate SSO).

## Overview (9.4.4)

<!-- ISO 29148 §9.4.4 (paraphrased guidance): describe the major
     internal divisions and external entities and how they are
     interrelated, from the stakeholder's vantage; diagrammatic
     description recommended. -->

From the stakeholders' vantage the interrelation is a queue: partners
arrive through the portal (external entity → Developer Relations
queue → Security review → platform provisioning → activation), and
money flows out the other way (platform metering → Finance & Billing
→ payment processor → partner invoice). The cloud hosting provider is
invisible to stakeholders except as an availability dependency.

## Stakeholders (9.4.5)

<!-- ISO 29148 §9.4.5 (paraphrased guidance): list the stakeholders or
     classes of stakeholders and describe how they are related to the
     development and operation of the system. -->

- **Partner engineers** — operate the portal; their needs are
  self-service, speed, and clear error messages.
- **Support agents** — operate the back-office console on behalf of
  partners; their needs are fast key operations and full audit
  visibility.
- **Developer Relations managers** — approve exceptions and watch the
  onboarding queue; their needs are SLA dashboards.
- **Security reviewers** — perform the P-01 gate; their needs are a
  structured review workflow and evidence fields.
- **Finance & Billing analysts** — reconcile the monthly hand-off;
  their needs are complete, correct metering exports.
- **Executive leadership** — track the quarterly KPIs of the BRS
  9.3.7; their needs are the KPI dashboard only.

## Business environment (9.4.6)

<!-- ISO 29148 §9.4.6 (paraphrased guidance): define the external and
     internal environmental factors stakeholders must consider when
     stating their requirements — market, legal, social, technology. -->

Stakeholders state their requirements under the same four factors as
the BRS's 9.3.6, with two stakeholder-specific consequences: the
data-protection law means EU-based partners require their data to
stay in-region (a partner requirement, not just an internal one), and
the OAuth ecosystem means partner engineers will not accept a
separate credential for the portal (a usability requirement in 9.4.15).

## Mission, goals and objectives (9.4.7)

<!-- ISO 29148 §9.4.7 (paraphrased guidance): describe the business
     results to be obtained through or by the proposed system, as the
     stakeholders will recognize and verify them. -->

Stakeholder-recognizable outcomes, each traceable to a BRS KPI:

- A partner can complete registration-to-activation without contacting
  support (≥ 90% of partners) — the onboarding KPI.
- A support agent can revoke a key in under a minute with one
  confirmation — the support-ticket KPI.
- A billing analyst can close month-end reconciliation without manual
  data reconstruction — the dispute KPI.

## Business model (9.4.8)

<!-- ISO 29148 §9.4.8 (paraphrased guidance): describe the methods by
     which the business goal is achieved, concentrated on the methods
     the system supports, as the stakeholders experience them. -->

As experienced by stakeholders: the three tiers of the BRS 9.3.8 show
up in the portal as different key quotas (Starter 1 key, Growth 10,
Scale unlimited-within-fair-use), different support windows, and
different billing granularity (monthly for Starter, usage-based for
Growth/Scale). The system must make the tier consequences visible at
registration, not after the first invoice.

## Information environment (9.4.9)

<!-- ISO 29148 §9.4.9 (paraphrased guidance): describe the
     organization-level information strategy stakeholders depend on —
     portfolio positioning, long-term system plan constraints,
     database configuration constraints. -->

Stakeholders depend on the BRS 9.3.9 in three places: portal users
see the partner master data (they must not re-enter what the global
partner database already holds); Finance & Billing analysts consume
the billing-backbone hand-off (legacy billing systems are not
supported by the platform); and the 13-month retention of P-03
constrains what the KPI dashboards may show historically.

## System processes (9.4.10)

<!-- ISO 29148 §9.4.10 (paraphrased guidance): describe how and in
     which context the system supports the business activities; system
     processes flow from the business processes with decomposition and
     classification; each uniquely named and numbered, described as a
     sequence of activities. -->

The system processes mirror the BRS business processes one level
lower:

- **SP-01 Registration and activation** (from BP-01): partner
  submits registration in the portal → system validates the
  submission → system routes to the Security review queue → on
  approval the system provisions the account and issues the key →
  partner activates the key in the portal.
- **SP-02 Key lifecycle operations** (from BP-02): issue / rotate /
  revoke / expire, each as a single auditable system action.
- **SP-03 Metering and invoicing hand-off** (from BP-03): system
  meters API calls per partner → system exports the monthly usage
  file → payment processor invoices → system displays the partner's
  own usage report.

## System operational policies and rules (9.4.11)

<!-- ISO 29148 §9.4.11 (paraphrased guidance): describe how the
     business operational policies and rules will likely be addressed
     in the functional requirements of the SyRS/SRS; they shall be
     uniquely named and numbered and referenced in the process
     descriptions. -->

- **P-01** (BRS 9.3.11) becomes a functional requirement: the
  system must block key issuance until the review record is
  approved (SyRS FR-02, SRS KIS-008).
- **P-02** becomes a functional requirement: revoke-then-reissue
  ordering, enforced by the system, not by the agent (SyRS FR-04,
  SRS KIS-002).
- **P-03** becomes a data requirement: metering events retained 13
  months (SyRS IM-01, SRS KIS logical database).

## Operational constraints (9.4.12)

<!-- ISO 29148 §9.4.12 (paraphrased guidance): describe system
     conditions and functional requirements to be imposed on the
     system in conducting the business process; conditions may result
     in performance requirements in the SyRS. -->

- The two BRS 9.3.12 constraints carry over: provisioning within 5
  business days of approval; every key lifecycle event auditable.
- Stakeholder-added: portal responses to key operations must feel
  immediate — partners will not wait more than a few seconds (this
  becomes the SyRS performance requirements PR-01/PR-02).

## System operational modes and states (9.4.13)

<!-- ISO 29148 §9.4.13 (paraphrased guidance): describe the
     operational modes and states that support system operation, as
     stakeholders experience them. -->

- **Normal**: all of SP-01…SP-03 available to all stakeholder groups.
- **Degraded (manual fallback)**: portal read-only for partners;
  back-office still allows key operations for support agents;
  Developer Relations runs the BRS offline procedure. Stakeholders
  must be told, in both portal and console, which mode is active.
- **Maintenance**: announced window, no key operations, metering
  continues.

## System operational quality (9.4.14)

<!-- ISO 29148 §9.4.14 (paraphrased guidance): define the level of
     quality required for system operation — performance,
     compatibility, reliability, security, maintainability,
     portability; state priorities where they conflict. -->

Stakeholder quality levels (refined into the SyRS 9.5.x requirements):

- **Performance**: key operations in seconds, not minutes (9.4.12).
- **Reliability**: the portal is available on the days partners
  onboard — 99.5% monthly is the stakeholder-accepted floor.
- **Security**: key lifecycle is fully audited (P-03); partners see
  only their own data.
- **Maintainability**: support agents operate the console without
  engineering involvement in normal operation.
- **Portability**: EMEA and APAC hubs run the same system
  (BRS 9.3.15).

## User requirements (9.4.15)

<!-- ISO 29148 §9.4.15 (paraphrased guidance): user requirements are
     requirements for use — use-related quality (incl. usability)
     with intended outcomes and quality criteria, user-system
     interaction requirements, and constraints limiting design
     freedom; the context of use shall be specified; they can ground
     the operational scenarios. -->

- **Context of use**: partner engineers use the portal from their
  own organizations in standard browsers, with existing OAuth
  credentials, during working hours, without prior training; support
  agents use the back-office console at their desks with corporate
  SSO, possibly under time pressure during incidents.
- **Use-related quality**: ≥ 90% of partners complete registration
  without contacting support (measurable effectiveness); no action
  the user cannot undo or reverse is offered without a visible
  confirmation (harm avoidance: revocation).
- **Interaction requirements**: the portal speaks the partner's
  OAuth identity (no second credential); the console surfaces the
  audit trail one click away from any key.
- These user requirements ground the operational scenarios
  SC-01…SC-03 below.

## Operational concept (9.4.16)

<!-- ISO 29148 §9.4.16 (paraphrased guidance): describe the proposed
     system at a high level without design details — operational
     policies and constraints, description of the system, modes of
     operation, user classes and involved personnel, support
     environment (Annex A gives the detailed OpsCon treatment). -->

- **Operational policies and constraints**: P-01…P-03 and the
  9.4.12 constraints are operational for every stakeholder action.
- **Description of the system**: a web portal (partners) and a
  back-office console (internal staff) in front of a key management
  service and a metering service.
- **Modes of operation**: normal / degraded / maintenance per
  9.4.13, always visible to the user.
- **User classes**: partner engineers, support agents, Developer
  Relations managers, security reviewers, billing analysts — each
  with exactly the views listed in 9.4.5.
- **Support environment**: self-service help in the portal; support
  tickets reference key ids; 24×5 for Growth/Scale.

## Operational scenarios (9.4.17)

<!-- ISO 29148 §9.4.17 (paraphrased guidance): describe examples of
     how users/operators/maintainers interact with the system in
     important contexts of use; uniquely named and numbered;
     referenced from the (system) process descriptions. -->

- **SC-01 Partner registers and activates a key** (SP-01): the
  partner signs in with their existing OAuth account, submits the
  registration form (company, plan tier, technical contact), receives
  the review-queue status in the portal, and on approval sees the
  issued key and activates it with one click.
- **SC-02 Support agent revokes a compromised key** (SP-02): the
  agent opens the partner's key list in the console, selects the
  compromised key, confirms the revocation (the only destructive
  action requiring confirmation), and the console shows the audit
  entry immediately; reissue follows as a separate action per P-02.
- **SC-03 Partner hits the monthly usage limit** (SP-03): the portal
  shows the partner's own usage report against the tier limit and
  offers the upgrade path (S-03 from the BRS).

## Other detailed concepts of proposed system (9.4.18)

<!-- ISO 29148 §9.4.18 (paraphrased guidance): describe the detailed
     concepts for acquisition, deployment, support, and retirement,
     as stakeholders live them. -->

- **Acquisition**: partners self-acquire Starter in the portal;
  Growth/Scale add a contract step that the portal tracks to
  completion.
- **Deployment**: partners deploy the key into their products; the
  portal shows integration status (key created / first seen /
  active).
- **Support**: support agents work entirely in the console; partners
  are never asked for data the console already shows.
- **Retirement**: the portal warns the partner 30 days before key
  expiry from inactivity; archived accounts keep the 13 months of
  usage data readable by Finance & Billing (P-03).

## Project constraints (9.4.19)

<!-- ISO 29148 §9.4.19 (paraphrased guidance): if appropriate,
     describe the constraints to performing the project within cost
     and schedule, as stakeholders see them. -->

Stakeholders accept the BRS 9.3.19 constraints with one visible
consequence: the MVP ships SP-01 + SP-02 for EMEA only, so APAC
partners wait for increment 2 — the portal must show the EMEA/APAC
availability clearly at registration to avoid dead-ends.
