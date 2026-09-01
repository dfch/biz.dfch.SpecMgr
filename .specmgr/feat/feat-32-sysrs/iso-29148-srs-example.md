<!--
DISCUSSION DRAFT — ISO/IEC/IEEE 29148:2018 §9.6 outline example (SRS)
— not a schema, not wired into any tool/resource/model.

Source: the normative content outline for the Software Requirements
Specification in ISO/IEC/IEEE 29148:2018 §9.6 (full text locally
available as `ISO_29148.md`, gitignored as a third-party reference).
- Section names below are verbatim from the standard — they are the
  norm's mandatory document outline — with the clause number in each
  heading.
- The guidance comments are paraphrases of the standard's descriptive
  text, never verbatim quotations.
- All example content is fictional: the "Example Widget Platform" case
  shared with `example.md` … `example.v5.md`; this SRS zooms onto one
  concrete software product of that system — the Key Issuance
  Service — derived from the companion `iso-29148-syrs-example.md`.

The §9.6.1 "SRS overview" subclause is omitted: it is meta-text
about the clause itself, not document content.

Companions (one consistent BRS → StRS → SyRS → SRS chain for the same
fictional system): `iso-29148-brs-example.md`,
`iso-29148-strs-example.md`, `iso-29148-syrs-example.md`.
-->

# Software Requirements Specification (SRS): Key Issuance Service

This SRS is a specification for one software product — the **Key
Issuance Service (KIS)** — the key management service (KMS-SRV) of
the Example Widget Platform. It specifies the KIS to a level of
detail sufficient for its design, development, and verification,
derived from the SyRS requirements FR-02…FR-05, SI-01, SE-01, SE-04,
SE-05, IM-01, PR-01, PR-02, and RLY-02 (SyRS 9.5.19 D-02).

## Purpose (9.6.2)

<!-- ISO 29148 §9.6.2 (paraphrased guidance): delineate the purpose
     of the software to be specified. -->

KIS owns the full partner API key lifecycle: it issues keys under
the security-review gate, rotates them, revokes them, validates them
for the widget API, and writes the tamper-evident audit record for
every action. Portal, console, and the metering service consume KIS
through its REST API; no other component stores or mutates key state.

## Scope (9.6.3)

<!-- ISO 29148 §9.6.3 (paraphrased guidance): describe the scope by
     naming the software product(s), explaining what they will do,
     describing their application with relevant benefits/objectives/
     goals, and staying consistent with higher-level specifications. -->

a) The product is the **Key Issuance Service (KIS)**, one
   deployable, stateless software component of the Example Widget
   Platform.

b) KIS will: issue, rotate, revoke, expire, list, and validate API
   keys; enforce the review gate and per-partner rate limits; emit
   audit events; expose the key REST API. KIS will not: handle
   registration (portal), meter API calls (MTR-SRV), store partner
   master data (global partner database), or render any UI.

c) Application: KIS is the fulfillment of the SyRS key-lifecycle
   function F-2; its benefits are the 5-day onboarding KPI (BRS
   9.3.7) and the revocation-within-1-s security posture (SyRS
   FR-04).

d) Consistency: this SRS is consistent with the SyRS 9.5.x sections
   listed in the document header; where the two differ, the SyRS
   wins and this SRS must be corrected.

## Product perspective (9.6.4)

<!-- ISO 29148 §9.6.4 (paraphrased guidance): define the system's
     relationship to other related products; if the product is an
     element of a larger system, relate the larger system's
     requirements to the product's functionality and identify the
     interfaces; a block diagram of the larger system is recommended;
     then describe how the software operates within its constraints
     (system, user, hardware, software, communications interfaces,
     memory, operations, site adaptation, interfaces with services). -->

KIS is an element of the larger Example Widget Platform. Block
diagram (prose version): partner portal and back-office console both
call KIS over the internal API mesh; the widget API's validation
path calls KIS per request (cached, ≤ 1 s TTL); KIS reads/writes the
key store (managed database), the global partner database (read-only
for review state), the cloud key-management service (key material),
and the message broker (audit events).

### System interfaces (9.6.4.1)

<!-- ISO 29148 §9.6.4.1 (paraphrased guidance): list each system
     interface and identify the functionality of the software to
     accomplish the system requirement and the interface description
     to match the system. -->

- **KIS-SI-1** ↔ portal: KIS provides registration-acceptance key
  issuance (SyRS FR-03) via `POST /keys`.
- **KIS-SI-2** ↔ console: KIS provides rotate/revoke (SyRS FR-04/
  FR-05) and the key list view via `POST /keys/{id}/rotate`,
  `POST /keys/{id}/revoke`, `GET /keys?partner={id}`.
- **KIS-SI-3** ↔ widget API (validation path): KIS provides
  active/revoked/expired state via `GET /keys/{id}/status` (SyRS
  SI-02's 100 ms p99 bound).
- **KIS-SI-4** ↔ message broker: KIS publishes audit events (SyRS
  SE-04) to the `kis-audit` topic.

### User interfaces (9.6.4.2)

<!-- ISO 29148 §9.6.4.2 (paraphrased guidance): specify the logical
     characteristics of each interface between the software product
     and its users; a UI style guide can provide consistent rules. -->

KIS has no direct human interface — portal and console render it.
Logical characteristics of its API as the "user interface": JSON
responses, pagination on list endpoints, idempotency-key support on
all mutating endpoints (so retries never double-issue), and
machine-readable error codes with human-readable messages (KIS-UR-01
below).

### Hardware interfaces (9.6.4.3)

<!-- ISO 29148 §9.6.4.3 (paraphrased guidance): specify the logical
     characteristics of each interface between the software and
     hardware elements — configuration characteristics, supported
     devices and how, protocols. -->

None. KIS runs on cloud virtual machines/containers with no device-
specific support; the only hardware-relevant fact is that it must
run unmodified on the cloud hosting provider's standard instance
types in both operating regions (SyRS OQR-02).

### Software interfaces (9.6.4.4)

<!-- ISO 29148 §9.6.4.4 (paraphrased guidance): specify the use of
     other required software products and interfaces with other
     application systems; for each required product: name, mnemonic,
     specification number, version number, source; for each
     interface: purpose and message content/format. -->

Required software products:

| Product | Mnemonic | Spec | Version | Source |
|---|---|---|---|---|
| Managed relational database (key store) | DB | vendor spec | current maintained | cloud hosting provider |
| Cloud key-management service (key material) | KMS | vendor spec | current maintained | cloud hosting provider |
| Message broker (audit events) | BROKER | vendor spec | ≥ 3.x | cloud hosting provider |
| Global partner database client library | PDB-CLI | internal spec PDB-1 | 2.x | Platform Engineering |

Interface formats: DB — SQL via the managed client; KMS — vendor
REST API for generate/store/fetch-key-ref (KIS never fetches key
material into its own memory longer than the issuing call); BROKER —
JSON envelope, schema `KIS-AUDIT-1` (see KIS-EVT-1); PDB-CLI —
read-only queries against the review-state table.

### Communications interfaces (9.6.4.5)

<!-- ISO 29148 §9.6.4.5 (paraphrased guidance): specify the various
     interfaces to communications such as local network protocols. -->

Internal mesh: mTLS, HTTP/2. Ingress to portal/console: TLS 1.2+
over the load balancer (SyRS SI-06). No direct partner-network
traffic reaches KIS.

### Memory constraints (9.6.4.6)

<!-- ISO 29148 §9.6.4.6 (paraphrased guidance): specify applicable
     characteristics and limits on primary and secondary memory. -->

KIS is stateless: primary memory limit 2 GB per instance (cloud
quota); validation results cached in memory with a ≤ 1 s TTL to meet
KIS-007's 100 ms p99. No secondary memory of its own — durability
lives in DB/KMS/BROKER (KIS-MEM-1).

### Operations (9.6.4.7)

<!-- ISO 29148 §9.6.4.7 (paraphrased guidance): specify the normal
     and special operations required by the user — modes of
     operation, interactive vs unattended periods, data processing
     support functions, backup and recovery. -->

Normal operation is unattended; humans act only through portal/
console. Special operations: manual cache flush (admin endpoint,
audited) after a suspected validation drift; scheduled grace-period
expiry job (24 h after each rotation, KIS-004). Backup/recovery:
none for KIS itself (stateless per KIS-MEM-1); recovery is a
redeploy — the key store's nightly backup (SyRS IM-02) is the
durable state.

### Site adaptation requirements (9.6.4.8)

<!-- ISO 29148 §9.6.4.8 (paraphrased guidance): define requirements
     for data or initialization sequences specific to a given site,
     mission, or operational mode, and site/mission-related features
     to modify for a particular installation. -->

Per-region configuration only: KMS key id, DB endpoint, BROKER topic
prefix, and the partner-database region flag (for RG-01 in-region
processing). No site-specific data or initialization sequences; a
region is added by configuration (SyRS ADP-02).

### Interfaces with services (9.6.4.9)

<!-- ISO 29148 §9.6.4.9 (paraphrased guidance): specify interactions
     with services, e.g. Software-as-a-Service or cloud services. -->

Two SaaS interactions: the cloud key-management service (key
material generation and custody — KIS stores only the KMS key ref in
DB) and the managed database (key records). Both are consumption of
hosting-provider services, not partner-facing SaaS.

## Product functions (9.6.5)

<!-- ISO 29148 §9.6.5 (paraphrased guidance): summarize the major
     functions the software will perform, organized understandably
     for a first-time reader; textual or graphical methods allowed;
     use cases/scenarios may be used; the summary is not a design. -->

KIS performs five major functions, each detailed in Functions
(9.6.12):

- **Issue** a new key for an approved partner (KIS-001, KIS-008).
- **Rotate** a key with a 24 h grace period on its predecessor
  (KIS-004).
- **Revoke** a key immediately, with audit (KIS-002, KIS-005).
- **Validate** a key for the widget API within 100 ms p99
  (KIS-007).
- **Enforce** the per-partner issuance rate limit (KIS-006).

A function-relationship diagram is recommended: portal/console →
{Issue, Rotate, Revoke} → key store; widget API → Validate → key
store (cached); all four → audit topic; Issue/Rotate/Revoke ←
rate limiter.

## User characteristics (9.6.6)

<!-- ISO 29148 §9.6.6 (paraphrased guidance): describe the general
     characteristics of the intended user groups, including those
     influencing usability (education, experience, disabilities,
     technical expertise); state reasons for later requirements, not
     the requirements themselves. -->

KIS's direct users are software (portal, console, widget API), not
humans — which is why its "user interface" is an API (9.6.4.2). Its
indirect human users are the SyRS 9.5.4.3 groups, reached through the
rendering components: their technical expertise and no-training
expectations (SyRS UR-02) are the reasons behind KIS-UR-01/UR-02's
clear error responses and the OpenAPI document.

## Limitations (9.6.7)

<!-- ISO 29148 §9.6.7 (paraphrased guidance): generally describe
     items that limit the supplier's options — regulatory
     requirements/policies, hardware limitations, interfaces to other
     applications, parallel operation, audit functions, control
     functions, language requirements, handshake protocols, quality
     requirements, criticality, safety/security, physical/mental, and
     limitations sourced from other systems. -->

- **Regulatory (a)**: data residency — KIS instances process only
  their own region's partner keys (SyRS RG-01).
- **Interfaces to other applications (c)**: the audit-event schema
  `KIS-AUDIT-1` is consumed by the central audit system (SyRS RG-02)
  and is versioned; breaking changes need a 6-month dual-run, mirroring
  SyRS SI-04's convention.
- **Audit functions (e)**: every KIS action must produce its audit
  event before it reports success to the caller (KIS-005) — audit is
  not optional post-processing.
- **Quality requirements (i)**: the SyRS apportionment gives KIS
  99.9% monthly availability (SyRS RLY-02) — the highest in the
  platform.
- **Safety and security (k)**: key material never leaves the cloud
  KMS in KIS's memory longer than the issuing call (9.6.4.4); KIS
  treats every unauthenticated request as hostile.
- **From other systems (m)**: the widget API's 100 ms p99
  validation bound (SyRS SI-02) is imposed on KIS from outside and
  drives KIS-MEM-1's cache.

## Assumptions and dependencies (9.6.8)

<!-- ISO 29148 §9.6.8 (paraphrased guidance): list each factor that
     affects the requirements — not design constraints, but factors
     whose change would force this SRS to change. -->

- **ASS-1** The cloud KMS remains available in both regions (9.6.4.9);
  if KMS is deprecated, KIS-001/002's custody model must change.
- **ASS-2** The review-state table in the global partner database
  keeps its schema (9.6.4.4); a schema change alters KIS-008's gate
  read.
- **ASS-3** The message broker delivers at-least-once; if the
  platform switches to exactly-once semantics, KIS-005's dedup
  handling can be simplified.

## Apportioning of requirements (9.6.9)

<!-- ISO 29148 §9.6.9 (paraphrased guidance): apportion software
     requirements to software elements; state where allocation is
     initially undefined; summarize in a cross-reference table by
     function and element; identify requirements delayed to future
     versions. -->

| SyRS requirement | KIS function (9.6.12) | Notes |
|---|---|---|
| FR-02 (review gate) | F-1 Issue | gate check KIS-008 |
| FR-03 (issue ≤ 2 s) | F-1 Issue | KIS-001 |
| FR-04 (revoke ≤ 1 s) | F-2 Revoke | KIS-002 |
| FR-05 (rotate + grace) | F-3 Rotate, F-5 Grace expiry | KIS-004 |
| SI-02 (validation 100 ms) | F-4 Validate | KIS-007 |
| SE-01 (key custody) | all | 9.6.4.4 KMS interlock |
| SE-04 (audit log) | all | KIS-005, KIS-EVT-1 |
| SE-05 (per-partner limit) | F-1 Issue | KIS-006 |
| PR-01/PR-02 | F-1/F-2 | KIS-001/KIS-002 bounds |
| RLY-02 (99.9%) | all | attributes, 9.6.18 |

Delayed to a future increment: multi-region active-active failover
(currently region-pinned per 9.6.4.8) — no requirement number yet.

## Specified requirements (9.6.10)

<!-- ISO 29148 §9.6.10 (paraphrased guidance): specify the software
     system requirements to a level sufficient for design,
     development, and verification; they shall conform to the
     requirement characteristics of the standard (cl. 5.2), be
     cross-referenced, uniquely identifiable, and describe every
     input, output, and function. -->

- **KIS-001** KIS shall issue a new API key within 2 s at the 95th
  percentile of a `POST /keys` request for an approved partner.
- **KIS-002** KIS shall revoke a key within 1 s at the 95th
  percentile of a `POST /keys/{id}/revoke` request; a revoked key
  shall fail validation immediately after the revocation response.
- **KIS-003** Every key record shall carry: key id, partner id, KMS
  key ref, status (active / rotating / revoked / expired), creation
  timestamp, expiry timestamp, and rotating-from key id.
- **KIS-004** Rotation shall issue a new active key, set the
  predecessor's status to rotating with a 24 h grace period, and
  expire the predecessor when the grace period ends.
- **KIS-005** Every lifecycle action (issue, rotate, revoke,
  grace-expiry) shall write an audit record — actor, action, key id,
  partner id, timestamp, source IP — to the `kis-audit` topic before
  the action reports success.
- **KIS-006** KIS shall reject key issuance when the partner's
  issuance count in the current hour reaches the per-partner limit
  (default 100, configurable per partner).
- **KIS-007** `GET /keys/{id}/status` shall return active /
  rotating / revoked / expired within 100 ms at the 99th
  percentile.
- **KIS-008** KIS shall refuse issuance unless the partner's review
  record in the global partner database is approved (SyRS FR-02).

Inputs and outputs of every requirement are detailed in External
interfaces (9.6.11); functions in 9.6.12.

## External interfaces (9.6.11)

<!-- ISO 29148 §9.6.11 (paraphrased guidance): define all inputs into
     and outputs from the software, complementing (not repeating)
     9.6.4.1–9.6.4.5; per interface: name, purpose, source/
     destination, valid range/accuracy/tolerance, units, timing,
     relationships, data formats, command formats, data items. -->

- **KIS-API-1** `POST /keys` — purpose: key issuance. Source:
  portal (on behalf of the partner). Input: partner id (valid range:
  existing, review-approved per KIS-008), plan tier (Starter /
  Growth / Scale), idempotency key (any UUID). Output: key record
  (KIS-003 fields). Timing: KIS-001 (2 s p95). Format: JSON.
  Command: single POST, 201 on success, 409 on rate-limit (KIS-006),
  422 on gate failure (KIS-008).
- **KIS-API-2** `POST /keys/{id}/revoke` — purpose: revocation.
  Source: console (support agent). Input: key id (must exist, status
  active or rotating), agent id, confirmation token. Output: revoked
  key record. Timing: KIS-002 (1 s p95). Format: JSON.
- **KIS-API-3** `GET /keys/{id}/status` — purpose: validation.
  Source: widget API (per request, cached). Input: key id. Output:
  status enum (KIS-003). Timing: KIS-007 (100 ms p99). Format: JSON.
  Relationship: the only read path used at line rate; all other
  reads go through KIS-API-4.
- **KIS-API-4** `GET /keys?partner={id}` — purpose: key list for the
  console. Source: console. Input: partner id, optional status
  filter, page cursor. Output: paginated key records (≤ 50/page).
  Timing: 500 ms p95. Format: JSON.
- **KIS-EVT-1** `kis-audit` topic — purpose: audit event stream.
  Destination: central audit system, metering (cross-reference),
  SIEM. Data items: actor, action, key id, partner id, timestamp
  (UTC, ISO 8601, millisecond), source IP, region. Format: JSON
  envelope, schema `KIS-AUDIT-1`. Timing: published before the
  action's success response (KIS-005); at-least-once delivery
  (ASS-3).

## Functions (9.6.12)

<!-- ISO 29148 §9.6.12 (paraphrased guidance): define the fundamental
     actions in accepting/processing inputs and processing/generating
     outputs — validity checks, exact sequence of operations,
     responses to abnormal situations (overflow, communication
     facilities, hardware faults, error handling/recovery), effect of
     parameters, and input/output relationships (sequences,
     conversion formulas); partitioning into sub-functions is
     allowed and does not imply design partitioning. -->

- **F-1 Issue** (`KIS-API-1`): 1) validate inputs (partner exists,
  tier valid, idempotency key well-formed) → 2) check review gate
  (KIS-008) → 3) check rate limit (KIS-006) → 4) generate key in KMS,
  obtain key ref → 5) write key record (KIS-003) → 6) publish audit
  event (KIS-005) → 7) respond 201 with the record. Abnormal: KMS
  failure → 503, no partial record, no rate-limit consumption;
  gate/rate failures → 422/409 before step 4, no KMS call.
- **F-2 Revoke** (`KIS-API-2`): 1) validate key id and status →
  2) set status revoked, record revocation timestamp → 3) publish
  audit event → 4) flush the validation cache entry (≤ 1 s,
  KIS-002's immediacy) → 5) respond 200. Abnormal: already revoked →
  409, idempotent no-op for the audit (one event per state change).
- **F-3 Rotate** (`KIS-API-2` sibling `POST /keys/{id}/rotate`):
  1) validate → 2) F-1 steps 4–7 for the new key (same partner, tier)
  → 3) set predecessor rotating with 24 h expiry → 4) publish two
  audit events (issue + rotate) → 5) respond 201 with the new record.
- **F-4 Validate** (`KIS-API-3`): 1) check cache (TTL ≤ 1 s) → 2) on
  miss, read key record → 3) check expiry (grace-expired → expired)
  → 4) cache and respond. Parameter effect: the cache TTL is the
  single knob trading freshness for the 100 ms bound; TTL must stay
  ≤ 1 s per KIS-002.
- **F-5 Grace expiry** (scheduled job, hourly): 1) select rotating
  keys past their 24 h expiry → 2) set status expired → 3) publish
  an audit event per key (actor = system). Abnormal: DB read
  failure → retry with backoff, never skip a key twice (job is
  idempotent on state).

Input/output sequences: F-1 output (key record) is the input to F-2/
F-3/F-4; F-3 output is a new F-1 record plus a state change on an
existing one; F-5 consumes F-3's predecessors. No conversion
formulas — all transformations are state transitions of the KIS-003
record.

## Usability requirements (9.6.13)

<!-- ISO 29148 §9.6.13 (paraphrased guidance): define usability and
     quality-in-use requirements and objectives for the software —
     measurable effectiveness, efficiency, satisfaction, harm
     avoidance in specific contexts of use. -->

- **KIS-UR-01** Every error response shall carry a machine-readable
  code (stable, documented) and a human-readable message naming the
  violated requirement (e.g. `RATE_LIMITED (KIS-006)`).
- **KIS-UR-02** An OpenAPI 3 document of KIS-API-1…KIS-API-4 shall
  be published with every release and kept in sync (effectiveness:
  portal/console developers build against it without KIS source
  access).
- **KIS-UR-03** No endpoint shall accept key material — only key
  refs/ids — so that a caller cannot misuse the API to exfiltrate
  material (harm avoidance, supports SE-01).

## Performance requirements (9.6.14)

<!-- ISO 29148 §9.6.14 (paraphrased guidance): specify static and
     dynamic numerical requirements; state performance in measurable
     terms (the standard's own example: a percentage of transactions
     within a time bound, not "the user shall not have to wait"). -->

Static:

- **KIS-PERF-1** KIS shall support 10,000 active partners and 50,000
  live keys per region.
- **KIS-PERF-2** KIS shall handle 500 validations/s sustained with
  2,000/s peaks per region.

Dynamic (measurable):

- **KIS-PERF-3** 95% of key issuance requests shall be processed in
  less than 2 s (KIS-001).
- **KIS-PERF-4** 95% of revocation requests shall be processed in
  less than 1 s (KIS-002).
- **KIS-PERF-5** 99% of validation requests shall be processed in
  less than 100 ms (KIS-007).

## Logical database requirements (9.6.15)

<!-- ISO 29148 §9.6.15 (paraphrased guidance): specify logical
     requirements for information placed into a database — types of
     information used by the functions, frequency of use, accessing
     capabilities, data entities and relationships, integrity
     constraints, security, data retention. -->

Entities (key store DB, 9.6.4.4):

- **key_record**: KIS-003 fields; accessed by key id (validation
  rate, KIS-PERF-2) and partner id (listing); unique constraint: at
  most one active-or-rotating key per (partner, slot) per tier quota.
- **audit_event**: KIS-EVT-1 items, append-only, hash-chained (each
  row references the previous row's hash) — supports SE-04's
  tamper-evidence; frequency: one row per lifecycle action.
- **rate_limit_state**: (partner id, hour bucket, count) — short-TTL
  rows, pruned after 24 h.

Integrity: status transitions follow the F-1…F-5 graph only (active →
rotating → expired; active → revoked; rotating → expired); no
direct update to audit_event (application-level enforced, DB trigger
where available). Security: DB holds key refs, never key material
(SE-01); connection via managed identity, no static credentials.
Retention: key_records 13 months after partner archival (SyRS IM-01
interlock), audit_events 13 months (KIS-EVT-1), rate_limit_state 24 h.

## Design constraints (9.6.16)

<!-- ISO 29148 §9.6.16 (paraphrased guidance): specify constraints on
     the software design imposed by external standards, regulatory
     requirements, or project limitations. -->

- **KIS-DC-1** KIS shall be deployed as a signed container image on
  the managed Kubernetes tenancy (SyRS PKG-02, 9.5.11.1).
- **KIS-DC-2** KIS shall be stateless per instance (KIS-MEM-1) —
  horizontal scaling and region pinning both depend on it.
- **KIS-DC-3** KIS shall be written in Python 3.13 on the platform's
  standard API framework (project limitation: one language per
  service in the platform).

## Standards compliance (9.6.17)

<!-- ISO 29148 §9.6.17 (paraphrased guidance): specify requirements
     derived from existing standards or regulations — report format,
     data naming, accounting procedures, audit tracing; e.g. a trace
     recording before/after values of all changes. -->

- **KIS-SC-1** KIS shall comply with OAuth 2.1 as the platform's
  identity standard (SyRS SI-01) — KIS validates the caller
  assertions issued by the portal/console, it does not run an
  authorization server.
- **KIS-SC-2** Audit tracing: every change to key_record shall be
  recorded in audit_event with before/after status values
  (KIS-SC-2a), satisfying SyRS RG-02's corporate audit policy.
- **KIS-SC-3** Data naming: all KIS identifiers are lowercase
  UUIDs; all timestamps UTC ISO 8601 with millisecond precision
  (platform convention, mirrors the billing-backbone schema of
  SyRS SI-04).

## Software system attributes (9.6.18)

<!-- ISO 29148 §9.6.18 (paraphrased guidance): specify the required
     attributes of the software product — reliability, availability,
     security, maintainability, portability — each with its concrete
     required factors. -->

- **Reliability (a)**: KIS shall achieve the KIS-PERF-3…5 bounds
  continuously; a single request failure shall never corrupt key
  state (all F-1…F-5 mutations are single-transaction).
- **Availability (b)**: KIS shall guarantee 99.9% monthly
  availability (SyRS RLY-02) via multi-replica deployment in two
  availability zones, checkpoint/restart on crash (stateless
  restart ≤ 30 s, no recovery step).
- **Security (c)**: KIS shall (1) use the cloud KMS for all key
  material (9.6.4.4); (2) keep the audit_event log hash-chained and
  append-only (KIS-SC-2); (3) check data integrity of key_record on
  read (status-graph validation per F-4); (4) restrict all mutating
  endpoints to authenticated internal callers (KIS-UR-03, SE-03).
- **Maintainability (d)**: KIS shall keep one function per module
  mirroring F-1…F-5, expose its configuration only through the
  documented 9.6.4.8 set, and limit any single module to the
  platform's complexity budget (SyRS MNT-03's console/IaC rule
  applies to KIS configuration changes).
- **Portability (e)**: KIS shall (1) contain no host-dependent code
  (pure container); (2) build from the platform's shared base image;
  (3) run on any Kubernetes ≥ 1.29 tenancy; (4) use no vendor-
  specific API outside the 9.6.4.4 product list.

## Verification (9.6.19)

<!-- ISO 29148 §9.6.19 (paraphrased guidance): provide the
     verification approaches and methods planned to qualify the
     software, recommended in parallel with 9.6.10–9.6.18. -->

Parallel to 9.6.10–9.6.18:

- **KIS-001…KIS-008**: test — unit tests per function (F-1…F-5) plus
  a release load test asserting KIS-PERF-3…5; KIS-008 has an
  explicit negative test (issuance with unapproved review record
  must 422 and must not call KMS).
- **KIS-EVT-1 / KIS-SC-2**: inspection — audit hash-chain check in
  CI against a fixture stream; before/after completeness review of
  every state transition.
- **KIS-UR-01…03**: inspection — error-code table review; OpenAPI
  diff against the previous release in CI.
- **KIS-PERF-1/2**: test — capacity test at 10× baseline (SyRS
  ADP-01 profile).
- **9.6.18 attributes**: analysis — reliability from the
  availability-zone failure drill; portability from a build-and-run
  in a clean Kubernetes cluster per release candidate.

## Supporting information (9.6.20)

<!-- ISO 29148 §9.6.20 (paraphrased guidance): consider additional
     supporting information — sample input/output formats, background
     information, description of the problems to be solved, special
     packaging instructions; state explicitly whether these items are
     part of the requirements. -->

**These items are illustrative background, not requirements.**

Sample `KIS-API-1` exchange (abridged):

```json
POST /keys
{ "partner_id": "7d1f…", "plan_tier": "growth",
  "idempotency_key": "c2a9…" }
→ 201 Created
{ "key_id": "9be4…", "partner_id": "7d1f…",
  "kms_key_ref": "arn:…/key/9be4…", "status": "active",
  "created": "2026-09-14T08:30:00.000Z",
  "expires": "2027-09-14T08:30:00.000Z", "rotating_from": null }
```

Background: the problem solved is the SyRS 9.5.2 purpose — six weeks
of manual key handling replaced by gated, audited, sub-second key
operations. Special packaging: none beyond KIS-DC-1 (signed image,
private registry).
