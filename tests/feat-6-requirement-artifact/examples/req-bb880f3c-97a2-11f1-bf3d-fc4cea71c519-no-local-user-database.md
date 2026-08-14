---
id: bb880f3c-97a2-11f1-bf3d-fc4cea71c519
type: req
created: 2026-08-13 22:38:55
updated: 2026-08-13 22:38:55
status: draft
version: 1.0.0
---

# No local user database

The system SHALL NOT maintain a local user database. User authentication SHALL be delegated to an external identity provider.

## Description

Maintaining a local user database introduces significant security risks and operational overhead. By delegating authentication to an external identity provider, the system reduces the attack surface, simplifies user management, and ensures compliance with modern security practices.

## Characteristics

1. Security
1. Maintainability

## Level

MUST

## Priority

100

## Tags

- Authentication
- Security
- Architecture

## Source

Security Policy

## Related Artifacts

### Requirements

- Grundschutz: Minimum security standards for information protection

### Goals

- KISS Principle: Keep system architecture simple and maintainable

## More Information

Delegating user authentication to an external identity provider (e.g., OAuth 2.0, SAML, or similar) reduces operational complexity and leverages industry-standard security practices.

## Notes

- Initial draft created 2026-08-13
- Waiting for acceptance criteria to be defined
