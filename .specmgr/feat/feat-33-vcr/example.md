<!--
DISCUSSION DRAFT — illustrative only, not a schema, not wired into any
tool/resource/model yet (no `vcr/models/v1/` code exists -- see this
feature's README.md, Task List, Phase 0). For the user to review before
Phase 1 (models/parser) starts, mirroring the empirical-draft-first
discipline `sysrs`/`sop` used for their own domains.

Thematically continues `feat-32-sysrs/example.v4.md`'s partner-API-key
scenario ("system shall support revoking a key within 1s of agent
action") to show how a future `sysrs` document's currently-unmodeled
"## Verification and Test Planning" section could instead cross-reference
a `vcr` document like this one. The `REQ`/`UC` id below is a fresh,
fictitious full UUID (not the truncated placeholder ids `sysrs`'s own
examples use), since this file is meant to double as a concrete look at
the real id shape `## Verifies` will carry.

No YAML frontmatter block -- body-only, same convention as
`feat-32-sysrs`'s own `example*.md` discussion drafts.
-->

# API Key Revocation Latency Verification

## Verifies

- REQ 4f2a1b3c-8d5e-4a91-9c72-1e6f8a2b3c4d: Revoke API key within 1s of
  agent action

  Confirms that a support agent revoking a compromised partner API key
  closes the exposure window fast enough to meet the 1-second
  performance requirement.

## Coverage

partial

## Acceptance Criteria

### AC-001 (Test): The revoke endpoint returns 204 within 1s under nominal load

95th-percentile latency from revoke request to `204 No Content` response
stays below 1000 ms, measured under a simulated 50 req/s background
load.

#### Test Steps

1. Issue a new API key via `POST /keys`.
2. Submit `POST /keys/{id}/revoke` and start a timer.
3. Record the wall-clock time to the `204 No Content` response.
4. Repeat 100 times under the simulated background load; assert the
   95th-percentile latency is below 1000 ms.

### AC-002 (Analysis): The latency budget is achievable given gateway overhead

A static review of the API gateway's measured per-hop overhead
(routing, auth, audit-log write) confirms the 1s budget leaves adequate
margin under expected load, without needing a dedicated test run.

### AC-003 (Inspection): The revoke handler has a well-formed not-found error path

#### Test Steps

1. Review the `revoke_key` handler source for a not-found branch.
2. Confirm the returned error body matches the documented error
   contract (`code`, `message`, `request_id`).

### AC-004 (Certification): The revocation audit-log format is compliance-certified

Sign-off from the internal Security Compliance review board that the
audit-log entries written on revocation satisfy the retention/format
policy. Tracked separately from AC-001..003 since it is a formal
certification step, not something this document's author can verify
directly.

## More Information

Verification performed against the staging gateway (build
2026.08.30-rc3). AC-004's Security Compliance sign-off is still
pending, which is why `## Coverage` above is `partial` rather than
`full`.

## Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

### 2026-08-31 07:40:12.500+02:00 — Initial draft created

Initial verification case drafted for the API key revocation latency
requirement. AC-001..003 executed against staging; AC-004 (Security
Compliance certification) still outstanding.
