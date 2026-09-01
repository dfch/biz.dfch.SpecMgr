<!--
DISCUSSION DRAFT — ISO/IEC/IEEE 29148:2018 §9.5 outline example (SyRS)
— not a schema, not wired into any tool/resource/model.

Source: the normative content outline for the System Requirements
Specification in ISO/IEC/IEEE 29148:2018 §9.5 (full text locally
available as `ISO_29148.md`, gitignored as a third-party reference).
- Section names below are verbatim from the standard — they are the
  norm's mandatory document outline — with the clause number in each
  heading.
- The guidance comments are paraphrases of the standard's descriptive
  text, never verbatim quotations.
- All example content is fictional: the "Example Widget Platform" case
  shared with `example.md` … `example.v5.md` and the companion
  `iso-29148-brs-example.md` / `iso-29148-strs-example.md` in this
  folder.

The §9.5.1 "SyRS overview" subclause is omitted: it is meta-text
about the clause itself, not document content.

Companions (one consistent BRS → StRS → SyRS → SRS chain for the same
fictional system): `iso-29148-brs-example.md`,
`iso-29148-strs-example.md`, `iso-29148-srs-example.md`.
-->

# System Requirements Specification (SyRS): Example Widget Platform

This SyRS identifies the technical requirements of the Example Widget
Platform — the system of interest — derived from the business
purpose and stakeholder needs stated in the companion BRS and StRS.
It describes what the system shall do, in terms of function,
performance, interfaces, and quality, without prescribing the design.

## System purpose (9.5.2)

<!-- ISO 29148 §9.5.2 (paraphrased guidance): define the reason(s)
     for which the system is being developed or modified. -->

The Example Widget Platform is developed to replace the manual,
e-mail-driven partner onboarding process with a self-service system
that provisions partner accounts, manages the full API key lifecycle
(issue, rotate, revoke, expire) under the security-review gate, and
meters API usage for the billing hand-off — reducing onboarding from
more than six weeks to five business days (BRS 9.3.7).

## System scope (9.5.3)

<!-- ISO 29148 §9.5.3 (paraphrased guidance): define the scope by
     naming the system, stating the results of the earlier needs
     analysis (what the system will and will not do), and describing
     its application with top-level benefits, objectives, goals. -->

a) The system is named **Example Widget Platform** (EWP).

b) Needs-analysis result: partner API onboarding takes more than six
   weeks of manual handling (BRS 9.3.2). The EWP will onboard
   partners, run the key lifecycle, and meter usage; it will not
   process payments (payment processor), manage legal contracts
   (Developer Relations), or build partners' products.

c) Application and top-level objectives: a web portal for partners,
   a back-office console for internal staff, and the two backing
   services (key management, metering) — delivering the three KPIs
   of BRS 9.3.7 (5-day onboarding, 50 integrations/quarter, 50%
   fewer support tickets).

## System overview (9.5.4)

<!-- ISO 29148 §9.5.4 (paraphrased guidance): describe at a general
     level the major elements of the system, including human elements
     and how they interact; diagrams and narrative define the context
     and all significant interfaces crossing the system boundary. -->

The EWP comprises four technical elements — partner portal,
back-office console, key management service (KMS-SRV), metering
service (MTR-SRV) — and two human elements — partner engineers and
internal staff (support agents, security reviewers, Developer
Relations managers, billing analysts). A context diagram is
recommended; the prose version: partners reach the portal over
HTTPS; internal staff reach the console over corporate SSO; the
portal and console both call KMS-SRV and MTR-SRV; KMS-SRV reads and
writes the global partner database and the key store; MTR-SRV
consumes API-call events and exports the monthly billing file to the
payment processor.

### System context (9.5.4.1)

<!-- ISO 29148 §9.5.4.1 (paraphrased guidance): describe the major
     elements and their interactions at a general level, defining all
     significant interfaces crossing the system boundary. -->

Interfaces crossing the EWP boundary:

- **I-01 Partner identity**: OAuth 2.1 from the partner's identity
  provider into the portal (inbound).
- **I-02 Partner widget API**: the partner product calls the EWP
  widget endpoints with its issued key (inbound; metered).
- **I-03 Internal SSO**: corporate SSO into the console (inbound).
- **I-04 Billing hand-off**: monthly usage export to the payment
  processor (outbound).
- **I-05 Partner master data**: read/append against the global
  partner database (both directions).
- **I-06 Cloud hosting**: EWP runs inside the cloud hosting
  provider's tenancy (availability dependency only).

### System functions (9.5.4.2)

<!-- ISO 29148 §9.5.4.2 (paraphrased guidance): describe the major
     system capabilities, conditions, and constraints. -->

- **F-1 Partner onboarding**: registration, validation, review
  routing, provisioning, activation (SP-01).
- **F-2 Key lifecycle**: issue, rotate, revoke, expire — each a
  single auditable action under the P-01 gate (SP-02).
- **F-3 Usage metering**: per-partner, per-API-call event capture
  and monthly export (SP-03).
- **F-4 Stakeholder views**: partner usage report, SLA dashboard,
  audit trail, KPI dashboard — the four views of StRS 9.4.5.
- **Conditions/constraints**: F-2 operates only in normal and
  degraded modes (StRS 9.4.13); F-3 must continue during
  maintenance.

### User characteristics (9.5.4.3)

<!-- ISO 29148 §9.5.4.3 (paraphrased guidance): identify each type of
     user/operator/maintainer (by function, location, device type),
     the number in each group, the nature of their use, and their
     characteristics and capabilities. -->

- **Partner engineers** (external, any location, standard browsers):
  thousands of individuals; technical; use the portal briefly per
  onboarding and rarely thereafter; no prior training (StRS 9.4.15).
- **Support agents** (internal, desk, browser): ~15; use the console
  continuously, under incident time pressure; no engineering
  background.
- **Security reviewers** (internal, desk, browser): ~5; use the
  review queue daily; skilled, but the console must still make the
  evidence fields explicit.
- **Developer Relations managers / billing analysts / executives**
  (internal, browser): ~10 combined; dashboard-only users.

## Functional requirements (9.5.5)

<!-- ISO 29148 §9.5.5 (paraphrased guidance): define the functional
     requirements applicable to system operation. -->

- **FR-01** The system shall validate a partner registration
  submission (company data, plan tier, technical contact) and reject
  incomplete submissions with field-level feedback.
- **FR-02** The system shall block key issuance until the security
  review record for the partner is approved (P-01).
- **FR-03** The system shall issue an API key within 2 s of
  registration acceptance.
- **FR-04** The system shall support revoking a key within 1 s of
  the agent's action; a revoked key shall fail validation
  immediately, and reissue shall be a separate action (P-02).
- **FR-05** The system shall support rotating a key: a new key is
  issued, the old key stays valid for a 24 h grace period, then
  expires.
- **FR-06** The system shall meter every API call per partner with
  timestamp, endpoint, and result.
- **FR-07** The system shall produce the monthly per-partner usage
  export in the billing-backbone format.

## Usability requirements (9.5.6)

<!-- ISO 29148 §9.5.6 (paraphrased guidance): define usability and
     quality-in-use requirements and objectives — measurable
     effectiveness, efficiency, satisfaction, and avoidance of harm
     in specific contexts of use. -->

- **UR-01** ≥ 90% of partners shall complete registration-to-
  activation without contacting support (StRS 9.4.15, measured
  quarterly).
- **UR-02** The portal shall be operable by a first-time partner
  engineer without prior training or documentation.
- **UR-03** The only destructive action (revocation) shall require an
  explicit confirmation and shall be immediately visible in the audit
  trail (harm avoidance).
- **UR-04** The active system mode (normal / degraded / maintenance,
  StRS 9.4.13) shall be displayed in both portal and console.

## Performance requirements (9.5.7)

<!-- ISO 29148 §9.5.7 (paraphrased guidance): define the critical
     performance conditions — dynamic actions/changes, quantitative
     endurance criteria, and performance per operational phase and
     mode. -->

- **PR-01** Key issuance shall complete within 2 s at the 95th
  percentile (from FR-03).
- **PR-02** Key revocation shall complete within 1 s at the 95th
  percentile (from FR-04).
- **PR-03** Metering shall sustain 5,000 API-call events/s with
  20,000 events/s peaks, without event loss, in normal mode.
- **PR-04** Portal pages shall load within 3 s at the 95th
  percentile over partner networks.
- **PR-05** In degraded mode, the console shall continue to serve
  key operations at the PR-01/PR-02 bounds.

## System interface requirements (9.5.8)

<!-- ISO 29148 §9.5.8 (paraphrased guidance): specify requirements
     for interfaces among system elements and with external entities
     (including the human element); define interdependencies and
     constraints (protocols, devices, standards, fixed formats);
     graphic representation allowed where it adds clarity. -->

- **SI-01** (I-01) The portal shall accept OAuth 2.1 assertions from
  partner identity providers; no parallel credential store.
- **SI-02** (I-02) The widget API shall be stateless HTTPS/JSON,
  authenticated by the issued key; key validation shall respond
  within 100 ms at the 99th percentile.
- **SI-03** (I-03) The console shall authenticate via corporate SSO
  with role-based access (support / reviewer / manager / analyst).
- **SI-04** (I-04) The monthly usage export shall use the fixed
  billing-backbone schema; format changes require a version bump and
  a 6-month dual-run.
- **SI-05** (I-05) Reads against the partner master database shall
  not exceed 10% of its allocated read capacity; appends use the
  database's existing API only.
- **SI-06** All cross-boundary traffic shall use TLS 1.2 or newer.

## System operations (9.5.9)

<!-- ISO 29148 §9.5.9 (paraphrased guidance): define the operational
     quality requirements of the system — human system integration,
     maintainability, reliability, and other quality characteristics. -->

### Human system integration requirements (9.5.9.1)

<!-- ISO 29148 §9.5.9.1 (paraphrased guidance): reference applicable
     documents; specify special requirements such as constraints on
     allocating functions to personnel and communications/
     personnel-equipment interactions; define requirements for areas
     where human error would be particularly serious. -->

- **HSI-01** Key operations in the console shall be single-click with
  the full context (partner, key, audit entry) visible — no
  engineering involvement in normal operation (StRS 9.4.14).
- **HSI-02** The revocation workflow is the high-error-sensitivity
  area: the console shall show the key's recent usage before the
  confirmation (an active key in production is a visible warning).
- **HSI-03** Security reviewers shall be able to record approval,
  rejection, and evidence links without leaving the review queue.

### Maintainability requirements (9.5.9.2)

<!-- ISO 29148 §9.5.9.2 (paraphrased guidance): specify quantitative
     maintainability requirements for the planned maintenance and
     support environment — times, rates, complexity, action indices,
     accessibility to components. -->

- **MNT-01** Mean time to repair for a failed platform component
  shall be ≤ 15 min using the runbook; no component shall require
  a single named engineer.
- **MNT-02** Preventative maintenance (dependency updates) shall be
  schedulable inside the monthly maintenance window without partner
 -visible outage beyond the announced window.
- **MNT-03** All configuration (tier quotas, rate limits, mode
  flags) shall be changeable via the console or IaC without code
  release.

### Reliability requirements (9.5.9.3)

<!-- ISO 29148 §9.5.9.3 (paraphrased guidance): specify system
     reliability requirements in quantitative terms, including the
     conditions under which they are met; may include a reliability
     apportionment model. -->

- **RLY-01** The portal shall be available 99.5% per calendar month
  in normal mode.
- **RLY-02** KMS-SRV shall be available 99.9% per calendar month —
  it sits on the key-operation critical path and is apportioned
  higher than the portal.
- **RLY-03** MTR-SRV shall lose no metering events in normal mode
  under the PR-03 load (apportionment: event persistence is
  durable-write before acknowledgment).

### Other quality requirements (9.5.9.4)

<!-- ISO 29148 §9.5.9.4 (paraphrased guidance): define how the system
     will implement other quality requirements such as compatibility
     and portability. -->

- **OQR-01** Compatibility: the portal shall work in the two current
  major versions of the two dominant browsers.
- **OQR-02** Portability: the EWP shall deploy identically to the
  EMEA and APAC cloud regions (BRS 9.3.15) with region-specific
  configuration only.

## System modes and states (9.5.10)

<!-- ISO 29148 §9.5.10 (paraphrased guidance): if the system can
     exist in various operational modes or states, define them (with
     diagrams as appropriate) and define the modes and states
     requirements. -->

- **Normal**: all functions F-1…F-4 available; PR-01…PR-05 apply.
- **Degraded**: portal read-only; console key operations and metering
  continue (PR-05); mode banner per UR-04; entry condition is
  platform-side failure, exit is manual re-enable by Platform
  Engineering.
- **Maintenance**: announced window; no key operations; metering
  continues; portal and console show the window.
- A mode-transition diagram is recommended; transitions are:
  normal → degraded (automatic on failure detection), degraded →
  normal (manual), any → maintenance (scheduled), maintenance →
  normal (scheduled).

## Physical characteristics (9.5.11)

<!-- ISO 29148 §9.5.11 (paraphrased guidance): define the physical
     requirements (weight, volume, dimensions, installation
     characteristics, materials, markings, interchangeability,
     workmanship) and adaptability requirements (growth, expansion,
     capability, contraction). -->

### Physical requirements (9.5.11.1)

<!-- ISO 29148 §9.5.11.1 (paraphrased guidance): include constraints
     on weight, volume, dimension; construction characteristics of
     the installation site; materials; nameplates/markings;
     interchangeability; workmanship. -->

The EWP has no physical hardware of its own: it runs as managed
containers in the cloud hosting provider's tenancy (I-06). The only
physical constraint is regional co-location — each hub's containers
run in that region's availability zones (BRS 9.3.15, data
residency).

### Adaptability requirements (9.5.11.2)

<!-- ISO 29148 §9.5.11.2 (paraphrased guidance): define requirements
     for growth, expansion, capability, and contraction — e.g. spare
     capacity for expected future demand. -->

- **ADP-01** The platform shall scale horizontally: adding container
  replicas shall raise capacity linearly up to 10× the baseline
  without redesign.
- **ADP-02** A third region (NA, BRS 9.3.8) shall be addable by
  configuration and deployment only — no code change.
- **ADP-03** Per-partner rate limits shall be adjustable per partner
  at runtime (the fair-use mechanism for Scale tier).

## Environmental conditions (9.5.12)

<!-- ISO 29148 §9.5.12 (paraphrased guidance): include the
     environmental conditions to be encountered — natural, induced,
     electromagnetic, self-induced, threat, cooperative; and the
     legal/regulatory, political, economic, social, business
     environments. -->

- **Natural**: not applicable (datacenter-hosted).
- **Induced**: cloud hosting provider power and network failures —
  the platform shall survive a single availability-zone loss
  (ADP-01/RLY-01).
- **Self-induced**: the platform's own peak load (PR-03) is the
  design load; sustained overload degrades per 9.5.10, never
  corrupts data.
- **Threat**: the key store is the primary threat target — see
  System security requirements.
- **Legal/regulatory**: data residency per partner region (StRS
  9.4.6).
- **Business**: partner churn and volume growth per BRS 9.3.7
  (capacity planning input to ADP-01).

## System security requirements (9.5.13)

<!-- ISO 29148 §9.5.13 (paraphrased guidance): define security
     requirements for the facility housing the system and for
     operational security of the system itself — access limitations,
     log-on/passwords, data protection and recovery, protection
     against accidental or malicious access/use/modification/
     destruction/disclosure. -->

- **SE-01** Keys shall be generated and stored in the cloud key
  management service; no key material in application databases in
  plaintext.
- **SE-02** All cross-boundary and inter-service traffic shall use
  TLS 1.2 or newer (SI-06).
- **SE-03** Console access shall be role-based (SI-03); the support
  role cannot approve its own partner's review.
- **SE-04** Every key lifecycle event shall be written to a
  tamper-evident audit log (append-only, hash-chained).
- **SE-05** Key issuance shall be rate-limited per partner, not
  globally (default 100 keys/h/partner) — a compromised partner
  account must not starve other partners.
- **SE-06** Portal sessions shall expire after 30 min of inactivity;
  console sessions after 15.

## Information management requirements (9.5.14)

<!-- ISO 29148 §9.5.14 (paraphrased guidance): define requirements
     for the system's management of information it receives,
     generates, or exports — types and amounts, protections, backup
     and archiving. -->

- **IM-01** Metering events shall be retained 13 months (P-03), then
  archived read-only for 12 more.
- **IM-02** The key store and partner database shall be backed up
  nightly; RPO ≤ 24 h, RTO ≤ 4 h.
- **IM-03** Partner personal data shall be minimized: the portal
  collects only the registration fields of FR-01; no free-text
  fields that can capture more.
- **IM-04** The monthly export (FR-07) is the only partner data
  leaving the EWP boundary (I-04).

## Policy and regulation requirements (9.5.15)

<!-- ISO 29148 §9.5.15 (paraphrased guidance): derive requirements
     from organizational policies and business practices and from
     relevant external regulations that affect operation or
     performance; specify derived health-and-safety criteria where
     applicable. -->

- **RG-01** The platform shall comply with the data-protection law
  of each operating region; EU-region partner data shall be stored
  and processed in-region (OQR-02 + 9.5.11.1).
- **RG-02** Corporate audit policy requires the SE-04 audit log to
  be exportable to the central audit system monthly.
- **RG-03** Labor policy: support agents' console access is
  time-bounded to their employment record (SI-03/SE-03 interlock).
- **Health and safety**: no additional criteria derived — the system
  is office/remote-operated software with no physical plant.

## System life cycle sustainment requirements (9.5.16)

<!-- ISO 29148 §9.5.16 (paraphrased guidance): outline the quality
     activities (reviews, measurement collection and analysis) that
     realize a quality system; include facilities for operational-
     and depot-level support, spares, sourcing and supply,
     provisioning, technical documentation and data, and personnel
     training. -->

- **SLS-01** Monthly KPI review against BRS 9.3.7 (onboarding time,
  integration volume, ticket rate) with measurements collected
  automatically from the platform.
- **SLS-02** Runbooks for every mode transition and for MNT-01
  repairs, reviewed each increment.
- **SLS-03** Initial cadre training: 2 support agents per hub
  certified before go-live; refresher each increment.
- **SLS-04** Technical documentation (API reference, console guide,
  runbooks) ships with every release.

## Packaging, handling, shipping and transportation requirements (9.5.17)

<!-- ISO 29148 §9.5.17 (paraphrased guidance): define requirements
     imposed on the system to ensure it can be packaged, handled,
     shipped, transported, and stored within its intended operational
     context. -->

- **PKG-01** The EWP has no physical packaging, handling, or
  shipping requirements (cloud-hosted per 9.5.11.1).
- **PKG-02** Release artifacts (container images) shall be signed,
  stored in the private registry, and immutable per version;
  deployment is the only "transport" step (I-06).

## Verification (9.5.18)

<!-- ISO 29148 §9.5.18 (paraphrased guidance): provide the
     verification approaches and methods planned to qualify the system
     or system element; recommended to be given in parallel with the
     requirements in 9.5.5–9.5.17. -->

Verification approach per requirement group (parallel to 9.5.5–
9.5.17):

- **FR-01…FR-07**: test — functional test suite per release; FR-03/
  FR-04 additionally load-tested against PR-01/PR-02.
- **UR-01…UR-04**: demonstration — usability study with three
  partners for UR-01/UR-02; inspection of the console flow for
  UR-03/UR-04.
- **PR-01…PR-05**: test — load test harness replaying the PR-03
  profile; quarterly re-run.
- **SI-01…SI-06**: test — interoperability test with a reference
  partner identity provider and the billing backbone in a staging
  region.
- **9.5.9–9.5.11**: analysis — apportionment and scaling analysis
  per increment; MNT-01 exercised in game days.
- **9.5.12–9.5.17**: inspection — audit-log hash-chain check (SE-04),
  backup-restore drill (IM-02), region deployment dry-run (OQR-02/
  ADP-02).

## Assumptions and dependencies (9.5.19)

<!-- ISO 29148 §9.5.19 (paraphrased guidance): list the assumptions
     and dependencies applicable to the system requirements that
     should be taken into account in allocating and deriving
     lower-level requirements. -->

- **A-01** The global partner database exists and keeps its current
  availability (SI-05 depends on it).
- **A-02** Partner identity providers support OAuth 2.1 (SI-01);
  partners without it use the portal's hosted identity.
- **A-03** The cloud hosting provider offers key-management and
  container services in both operating regions (SE-01, 9.5.11.1).
- **D-01** The billing-backbone consolidation (BRS 9.3.9 b) completes
  before MVP — FR-07's format is defined against the new backbone.
- **D-02** Lower-level derivation: KMS-SRV carries FR-02…FR-05,
  SE-01, SE-04, SE-05 (specified in the companion SRS for the Key
  Issuance Service); MTR-SRV carries FR-06, FR-07, PR-03, RLY-03.
