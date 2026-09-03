---
created: '2025-04-01 06:18:52.437Z'
id: c4e7b8a3-1f2d-4e9c-8b6a-3d5f7e9c1a2b
status: active
type: sop
updated: '2025-04-27 14:39:07.916Z'
version: 1.0.0
---

# New Employee IT Account Provisioning

## Purpose

This procedure defines how the IT department provisions accounts,
hardware, and core application access for a new employee between the
confirmation of their start date and the end of their first working
day. It exists so that every new starter can begin productive work
immediately on day one, with the correct access for their role and no
unauthorized privileges.

## Scope

This procedure applies to all permanent and fixed-term employees
onboarded into the engineering and corporate functions. It does not
cover contractors (handled by the vendor-onboarding procedure), interns
covered by the internship program, or access to regulated systems
requiring a separate compliance review (handled by the access-control
review board). It covers directory accounts, email, endpoint
enrollment, and the standard application catalog; bespoke application
access requested outside the standard catalog follows the exception
process in the access-management policy.

## Definitions

- A new starter is an employee whose start date has been confirmed in
  writing by HR and entered into the HRIS.
- The standard application catalog is the published list of
  applications whose access can be granted by role, without an
  additional business justification.
- An endpoint is the laptop or workstation imaged and assigned to the
  new starter.
- An access ticket is the ITSM record that tracks this provisioning
  request end to end.

## Roles and Responsibilities

### Accountable

The IT Operations Manager is accountable for ensuring that every new
employee is provisioned correctly and on time, and for the overall
health of this procedure.

### Responsible

- IT Service Desk engineers create the directory account, enroll the
  endpoint, and assign the standard application roles.
- The hiring manager submits the access ticket with the confirmed role
  and start date, and confirms any role-specific access on day one.
- HR notifies IT of the confirmed start date at least three working
  days before it.

### Support

### Consulted

- Information Security is consulted on any access that falls outside
  the standard application catalog.
- The Facilities team is consulted when the new starter needs a desk or
  building access badge.

### Informed

- The new starter is informed by email once the account is ready and
  the endpoint is available for collection.
- The hiring manager is informed when provisioning is complete.

## Safety and Precautions

Do not grant access that the role does not require: least-privilege is
the default, and any deviation must be recorded on the access ticket
with a business justification and the approving manager's name. Never
reuse a directory account that belonged to a previous employee; every
new starter gets a fresh, uniquely named identity. If the start date
moves or the offer is withdrawn, close the access ticket immediately so
no orphan account is created.

## Procedure

### Step 1: Receive and verify the access ticket

Confirm the access ticket from the hiring manager is complete: it must
name the new starter, the confirmed start date, the role, and the
manager. If any field is missing or the start date is fewer than three
working days away, return the ticket to the hiring manager rather than
proceeding, and record the reason on the ticket.

### Step 2: Create the directory account

Create the directory account using the naming convention in the
identity-management standard. Set an initial password that the new
starter will change on first login, and add the account to the role
groups that map to the standard application catalog for the confirmed
role. Do not add the account to any group outside the standard catalog
at this stage.

### Step 3: Enroll the endpoint

Image the assigned endpoint from the current golden image and join it
to the directory domain. Install the standard endpoint tooling
(endpoint detection and response, full-disk encryption, the corporate
VPN client). Verify the endpoint reports as compliant in the
management console before handing it over.

### Step 4: Assign application access

Grant the applications in the standard catalog for the role. For any
application outside the standard catalog requested on the ticket, route
the request to Information Security for consultation, and only grant it
once that consultation is recorded on the ticket with an approval.

### Step 5: Hand over and close

Email the new starter that the account is ready and the endpoint is
available for collection, with the first-login instructions. Notify the
hiring manager that provisioning is complete. Update the access ticket
with what was provisioned, close it, and record the completion date.

## Related Artifacts

### Requirements

- REQ-9687: Every new employee must be able to log in and send email on
  their first working day.

### Decisions

- DEC-2703: Adopt least-privilege role groups as the default access
  model.

### Goals

- GOL-0007: New employees reach full productive access on day one.

### Acceptance Criteria

- ACC-1234: The access ticket is closed within one working day of the
  start date.

### Sops

- SOP-0042: Offboarding and account de-provisioning.

## More Information

The standard application catalog and the role-to-group mapping are
maintained by the identity-management team and published on the IT
intranet. Provisioning metrics (ticket lead time, day-one readiness
rate) are reported monthly to the IT Operations Manager.

## Updates

### 2025-04-27 16:52:19.384+02:00 - Approved and activated

The procedure was approved by the IT Operations Manager and activated
as the standing reference for new-employee provisioning. It supersedes
the interim onboarding notes used since the start of the year.
