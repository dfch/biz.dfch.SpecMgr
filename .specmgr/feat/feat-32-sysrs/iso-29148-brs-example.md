<!--
DISCUSSION DRAFT — ISO/IEC/IEEE 29148:2018 §9.3 outline example (BRS) —
not a schema, not wired into any tool/resource/model.

Source: the normative content outline for the Business Requirements
Specification in ISO/IEC/IEEE 29148:2018 §9.3 (full text locally
available as `ISO_29148.md`, gitignored as a third-party reference).
- Section names below are verbatim from the standard — they are the
  norm's mandatory document outline — with the clause number in each
  heading.
- The guidance comments are paraphrases of the standard's descriptive
  text, never verbatim quotations.
- All example content is fictional: the "Example Widget Platform" case
  shared with `example.md` … `example.v5.md` in this folder.

The §9.3.1 "BRS overview" subclause is omitted: it is meta-text about
the clause itself, not document content.

Companions (one consistent BRS → StRS → SyRS → SRS chain for the same
fictional system): `iso-29148-strs-example.md`,
`iso-29148-syrs-example.md`, `iso-29148-srs-example.md`.
-->

# Business Requirements Specification (BRS): Example Widget Platform

This BRS documents Example Corp's motivation for developing the
Example Widget Platform, the business processes and policies under
which the platform is used, and the top-level requirements from the
business's own perspective. It is the highest-level specification in
the chain: the StRS refines it for the stakeholders, the SyRS for the
system, and the SRS for the Key Issuance Service product.

## Business purpose (9.3.2)

<!-- ISO 29148 §9.3.2 (paraphrased guidance): state, at organization
     level, the reason and background for pursuing new or changed
     business to fit a new management environment, and how the
     proposed system contributes to meeting business objectives. -->

Example Corp sells embeddable analytics widgets to business partners.
The partner-integration business is changing from a manual,
sales-engineer-driven model to a self-service model because the
current process loses deals: onboarding a partner today takes more
than six weeks of e-mail round-trips. The proposed system — the
Example Widget Platform, a self-service portal plus a back-office —
contributes to the business objective of turning partner integration
from a service project into a product capability.

## Business scope (9.3.3)

<!-- ISO 29148 §9.3.3 (paraphrased guidance): define the business
     domain by name; define the range of business activities included
     (and, helpfully, the entities outside the scope); describe the
     scope of the system being developed, including the assumptions on
     which business activities are supported by the system. -->

a) The business domain under consideration is **partner
   integration**: everything Example Corp does to onboard, bill, and
   support partners that embed its widgets.

b) In scope: partner registration, security review, API key
   lifecycle, usage metering, and the billing data hand-off to the
   external payment processor. Out of scope, deliberately named: the
   partners' own products, direct enterprise sales (owned by the
   sales organization), and payment processing itself (owned by the
   payment processor).

c) The system being developed supports the business activities above.
   Assumption: partners submit accurate company and contact
   information at registration; inaccurate submissions are caught by
   the security review, not by the platform.

## Business overview (9.3.4)

<!-- ISO 29148 §9.3.4 (paraphrased guidance): describe the major
     internal divisions and external entities of the business domain
     and how they are interrelated; a diagrammatic description is
     recommended. -->

Internal divisions: **Developer Relations** (partner success and
onboarding liaison), **Platform Engineering** (builds and operates
the platform), **Finance & Billing** (metering reconciliation and
invoice follow-through), and **Security** (performs the partner
security review). External entities: the **partners** themselves, the
**cloud hosting provider**, and the **payment processor**.

Interrelation (diagram recommended; prose substitute): a partner
registers in the portal; Developer Relations routes the submission to
Security for review; on approval, Platform Engineering's platform
provisions the account and issues the key; metering data flows to
Finance & Billing, which hands off to the payment processor; support
requests loop back to Developer Relations.

## Major Stakeholders (9.3.5)

<!-- ISO 29148 §9.3.5 (paraphrased guidance): list the major
     stakeholders or classes of stakeholders and describe how they
     influence the organization and business, or are related to the
     development and operation of the system. -->

- **Partner engineering teams** — primary consumers of the
  self-service flow; their time-to-integration is the business KPI.
- **Developer Relations managers** — own the onboarding SLA and
  approve exceptions.
- **Security reviewers** — gate key issuance (policy P-01 below);
  their throughput caps onboarding speed.
- **Finance & Billing analysts** — rely on the metering hand-off for
  accurate invoicing; billing disputes trace back to metering errors.
- **Executive leadership** — holds the quarterly integration-volume
  goal; funds the project.
- **Payment processor** — external; constrains the billing data
  format (see 9.3.9 c).

## Business environment (9.3.6)

<!-- ISO 29148 §9.3.6 (paraphrased guidance): define external and
     internal environmental factors to consider when understanding the
     business and eliciting stakeholder requirements — market trends,
     laws and regulations, social responsibilities, technology base. -->

- **Market trend**: the API economy is shifting toward self-service
  integration; competitors already onboard partners in days, not
  weeks.
- **Laws and regulations**: data-protection law applies to partner
  data and requires regional storage for partners in regulated
  regions.
- **Social responsibilities**: published, honored SLAs; transparent
  pricing of API usage.
- **Technology base**: cloud-native hosting; OAuth-based identity
  ecosystem that partners already use.

## Mission, goals and objectives (9.3.7)

<!-- ISO 29148 §9.3.7 (paraphrased guidance): describe the business
     results to be obtained through or by the proposed system. -->

Business results (measurable, not a feature list):

- Average partner onboarding time reduced from more than six weeks to
  **5 business days or fewer**.
- Partner integrations completed per quarter raised from **12 to 50**.
- Onboarding-related support tickets reduced by **50%** within two
  quarters of go-live.

## Business model (9.3.8)

<!-- ISO 29148 §9.3.8 (paraphrased guidance): describe the methods by
     which the business mission is expected to be achieved,
     concentrated on the methods the system supports — products and
     services, geographies, distribution channels, alliances and
     partnerships, finance and revenue model. -->

- **Products and services**: tiered partner plans (Starter, Growth,
  Scale) differing in key quotas and support level.
- **Geographies**: EMEA and APAC launch; NA follows in a second
  increment.
- **Distribution channels**: the self-service portal replaces the
  sales-engineer channel for onboarding.
- **Alliances and partnerships**: payment processor (billing), cloud
  hosting provider (infrastructure).
- **Finance and revenue model**: per-API-call usage billing metered
  by the platform and invoiced by the payment processor.

## Information environment (9.3.9)

<!-- ISO 29148 §9.3.9 (paraphrased guidance): describe the
     organization-level strategy on common bases for multiple
     information systems — project portfolio priorities, long-term
     system plan constraints, and database configuration constraints. -->

a) **Project portfolio**: the platform is one of two active projects
   pursuing partner growth; it is prioritized over the legacy partner
   portal refresh, which is cancelled.

b) **Long-term system plan**: the three legacy billing systems are
   being consolidated into one billing backbone (separate
   portfolio project); the platform integrates with the new backbone
   only, never with the legacy systems.

c) **Database configuration**: organization-level partner master
   data lives in one global partner database; the platform must not
   fork partner records — it consumes and appends to that database
   under its existing availability constraints.

## Business processes (9.3.10)

<!-- ISO 29148 §9.3.10 (paraphrased guidance): describe the
     procedures of business activities and possible system interfaces
     within them — how and in which context the system supports the
     business; each process uniquely named and numbered, described as
     a sequence of activities (diagram recommended). -->

- **BP-01 Partner onboarding**: partner submits registration →
  Developer Relations triages → Security performs review → platform
  provisions account and issues key → partner activates the key.
- **BP-02 API key lifecycle**: issue (via BP-01) → periodic rotate →
  revoke on compromise → expire on inactivity.
- **BP-03 Partner invoicing**: platform meters usage → monthly
  hand-off to payment processor → processor invoices partner →
  Finance & Billing reconciles and pursues disputes.

## Business operational policies and rules (9.3.11)

<!-- ISO 29148 §9.3.11 (paraphrased guidance): describe the logical
     propositions applied in conducting the business processes — start/
     branch/terminate conditions, judgment criteria, evaluation
     formulas; uniquely named and numbered, referenced by the business
     processes; these become functional requirements in the SyRS/SRS. -->

- **P-01**: No API key shall be issued before the security review is
  recorded as approved for the partner.
- **P-02**: A reported key compromise shall be handled by revoking
  the key first and reissuing second; reissue without revocation is
  prohibited.
- **P-03**: Usage data shall be retained for 13 months to support
  billing disputes.

## Business operational constraints (9.3.12)

<!-- ISO 29148 §9.3.12 (paraphrased guidance): describe conditions
     imposed on conducting the business process — e.g. performance
     constraints (process finished within a day of the trigger) or
     management requisites (every occurrence monitored and recorded). -->

- Onboarding provisioning shall be completed within **5 business
  days** of an approved security review.
- Every key lifecycle event (issue, rotate, revoke, expire) shall be
  recorded and auditable.

## Business operational modes (9.3.13)

<!-- ISO 29148 §9.3.13 (paraphrased guidance): describe methods to
     conduct the business operation in unsteady states — e.g. extreme
     load, or a manual operation mode when the proposed system is not
     available. -->

- **Normal mode**: all of BP-01…BP-03 run through the platform.
- **Manual fallback mode**: when the platform is unavailable,
  Developer Relations provisions accounts on the offline spreadsheet
  and issues keys by the emergency procedure; entries are reconciled
  into the platform when it recovers.

## Business operational quality (9.3.14)

<!-- ISO 29148 §9.3.14 (paraphrased guidance): define the level of
     quality required for the business operation — which quality
     characteristic wins where they conflict; may include high-level
     usability/quality-in-use objectives. -->

Speed of onboarding outranks full automation: for edge cases
(enterprise partners with custom data-protection agreements), manual
handling by Developer Relations is acceptable as long as the 5-day SLA
is met.

## Business structure (9.3.15)

<!-- ISO 29148 §9.3.15 (paraphrased guidance): identify and describe
     the business structures relevant to the system — organizational,
     role-and-responsibility, geographic, resource-sharing — and the
     need to align system functions to them and to future changes. -->

- **Organizational structure**: the four divisions of 9.3.4 report
  to the Head of Partner Ecosystem.
- **Role and responsibility structure**: Partner Manager (liaison to
  each partner), Security Reviewer (owns the P-01 gate), Billing
  Analyst (owns BP-03 reconciliation).
- **Geographic structure**: EMEA hub (Berlin) and APAC hub
  (Singapore); each hub handles its region's onboarding queue.
- **Resource sharing**: the global partner database (9.3.9 c) is
  shared between both hubs; the platform must support future
  re-hubbing without data migration.

## High-level operational concept (9.3.16)

<!-- ISO 29148 §9.3.16 (paraphrased guidance): describe the proposed
     system at a high level without design details — operational
     policies and constraints, description of the system, modes of
     operation, user classes and involved personnel, support
     environment. (Annex A gives the detailed OpsCon treatment.) -->

- **Operational policies and constraints**: P-01…P-03 and the two
  constraints of 9.3.12 apply to the platform's operation.
- **Description of the proposed system**: a web portal for partners
  plus a back-office console for internal staff, backed by a key
  management service and a metering service.
- **Modes of system operation**: normal, manual fallback, and a
  scheduled maintenance window (see 9.3.13).
- **User classes**: partner engineers (portal), support agents and
  Developer Relations managers (back-office console).
- **Support environment**: cloud-hosted; 24×5 support for Growth and
  Scale tier partners, business-hours support for Starter.

## High-level operational scenarios (9.3.17)

<!-- ISO 29148 §9.3.17 (paraphrased guidance): describe examples of
     how users/operators/maintainers interact with the system in
     important contexts of use; uniquely named and numbered;
     referenced from the business processes (9.3.10). -->

- **S-01 Partner registers and activates a new API key** — the
  happy path of BP-01; the primary scenario driving most downstream
  requirements.
- **S-02 Support agent revokes a compromised API key** — the
  exception path of BP-02; drives the security and audit
  requirements.
- **S-03 Partner hits the monthly usage limit** — BP-03 branch; the
  portal suggests a plan upgrade.

## Other high-level life-cycle concepts (9.3.18)

<!-- ISO 29148 §9.3.18 (paraphrased guidance): describe how the
     system of interest is to be acquired, deployed, supported, and
     retired. -->

- **Acquisition**: partners subscribe via the portal; Starter is
  self-serve, Growth/Scale require a Developer Relations contract
  step.
- **Deployment**: partners integrate the issued key into their own
  products; no Example Corp hardware ships.
- **Support**: tiered per 9.3.16; support tickets reference the key
  id for fast correlation.
- **Retirement**: keys expire after 90 days of inactivity; dormant
  partner accounts are archived after 12 months, retaining the 13
  months of usage data per P-03.

## Project constraints (9.3.19)

<!-- ISO 29148 §9.3.19 (paraphrased guidance): describe constraints to
     performing the project within cost and schedule. -->

- **Cost**: fixed project budget approved for two increments; no
  contingency beyond 10%.
- **Schedule**: MVP (BP-01 + BP-02, EMEA only) at the end of
  quarter 2; the full scope of this BRS by end of quarter 4.
- **Team**: at most six engineers allocated; Platform Engineering
  borrows from the billing-backbone project only for integration
  work.
