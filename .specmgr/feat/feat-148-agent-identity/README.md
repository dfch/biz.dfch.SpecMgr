---
classification: null
created: '2026-09-22 12:57:03.095+02:00'
id: feat-148-agent-identity
status: planning
type: feat
updated: '2026-09-22 12:57:03.095+02:00'
version: 1.0.0
---

# Feature: Separate Git/GitHub/GitLab Identity for Coding-Agent Pushes and Merges

## Plan

### Overview

The coding agent currently authenticates using the same credentials/session as the interactive developer user (a shared `gh auth login` session). Commits, pushes, and merges performed by the agent are therefore indistinguishable from those performed by the human developer in the repository history and hosting platform UI, with no separate identity, scope, or audit trail for agent-driven changes. This feature gives the agent its own git-hosting identity, portable across GitHub and GitLab (self-managed), while preserving the agent's ability to push and merge fully autonomously.

No credential values, account names, tokens, or other secrets are recorded anywhere in this repository or this feature folder — provisioning those is an external, manual step performed directly on each git hosting platform.

### Requirements

- REQ-001: Agent-performed pushes/merges must show a distinct actor (name/avatar) from the human developer's own actor, on both GitHub and GitLab.
- REQ-002: The agent's credential must be scoped only to what it needs (contents read/write, pull request read/write) and must be revocable independently of the human developer's own credentials.
- REQ-003: The developer's own interactive `gh`/git authentication and session must remain unaffected by the agent's credential setup.
- REQ-004: The setup must be documented in a host-agnostic way, applicable to both GitHub and GitLab on-prem without platform-specific lock-in.
- REQ-005: The agent must retain full autonomy to push and merge without a mandatory manual-approval step being introduced.

### Acceptance Criteria

- [ ] ACC-001: A test push/PR/merge performed by the agent shows a different author/actor identity than one performed by the human developer, verifiable in the GitHub/GitLab UI and via `git log`.
- [ ] ACC-002: No token, PAT, account name, or other credential value exists anywhere in this repository's tracked files (including this feature folder) at any point during or after implementation.
- [ ] ACC-003: The developer's personal `gh auth login` session and interactive git configuration are unchanged after the agent's credential is wired up.
- [ ] ACC-004: Automated CI status checks still gate merges to protected branches; no manual human-review step is added as part of this feature.
- [ ] ACC-005: Setup documentation covers both a GitHub bot-account/PAT flow and a GitLab Service Account / Project-Group Access Token flow, using the same underlying pattern.

### Scope

#### Included

- Provisioning guidance for a dedicated bot/service identity per git host (GitHub fine-grained PAT on a machine account; GitLab Service Account or Project/Group Access Token).
- Isolating that credential so it is used only by the agent's own process environment (e.g. agent launch/env config), never the developer's interactive shell or stored `gh`/git session.
- Aligning the git commit-author identity (`user.name`/`user.email`) used by the agent with the same bot identity.
- Optional: a co-author trailer on agent commits for later searchability.

#### Explicitly Out Of Scope

- Commit signing / cryptographic provenance (GPG/SSH signed commits) — not part of this iteration.
- Any change to the human developer's own existing authentication flow.
- Actually creating the bot/service account or generating its token — those are external, manual, one-time actions performed directly on the git hosting platform(s) and are never scripted or stored in this repo.

### Dependencies

#### Depends On

- None.

#### Blocks

- None currently identified.

### Design Notes

Proposed approach, in order:

1. **Provision a bot/service identity per host.** GitHub: a machine account with 2FA enabled, and a fine-grained PAT scoped to only the relevant repo(s), with `Contents: read/write`, `Pull requests: read/write`, `Metadata: read`. GitLab on-prem: a Service Account (Premium/Ultimate self-managed) or a Project/Group Access Token (works on Free/CE too, auto-provisions a scoped bot user), role `Maintainer`, scopes `api` and `write_repository`.
2. **Isolate the credential from the developer's personal session.** The developer's `gh auth login` session is stored per OS user and would otherwise be inherited by any process running as that same user. The agent's credential (`GH_TOKEN` / `GITLAB_TOKEN`) must instead be set only in the environment the agent process itself launches with (e.g. the agent's own launch/env configuration), never exported in the developer's interactive shell rc files. Both `gh` and `glab` prioritize an env-var token over the stored login, so this cleanly overrides only the agent's process.
3. **Align the git author identity with the bot token.** Configure `user.name`/`user.email` for the agent's execution context to match the bot identity, so the commit *author* field lines up with the account that owns the pushing token.
4. **Keep automated CI status checks as the safety net.** Protected branches keep required status checks; no manual review gate is added, preserving full autonomy.
5. **Optional co-author trailer.** Agent commits may include a `Co-authored-by: <bot identity>` trailer purely for later `git log --grep` searchability; this is cosmetic and does not itself provide attribution or security guarantees.

### Related Decisions

- None yet. If a host-specific mechanism (e.g. GitHub App vs. bot account) is later chosen as a hard architectural commitment, record that choice as a proper decision/ADR rather than only here.

### Task List

#### Phase 1: Provisioning and Documentation

- [ ] Task 1.1: Document the exact steps for provisioning a GitHub fine-grained PAT on a dedicated machine account, scoped to this repo, without recording any actual token/account values.
- [ ] Task 1.2: Document the exact steps for provisioning a GitLab Service Account or Project/Group Access Token, scoped to the relevant project(s), without recording any actual token/account values.

#### Phase 2: Agent Wiring

- [ ] Task 2.1: Update the agent's launch/env configuration so its process (and only its process) receives the bot credential via `GH_TOKEN`/`GITLAB_TOKEN`, without touching the developer's shell rc files or stored `gh` session.
- [ ] Task 2.2: Configure agent-scoped `git config user.name`/`user.email` to match the bot identity.
- [ ] Task 2.3 (optional): Wire in a `Co-authored-by:` trailer on agent commits.

#### Phase 3: Verification

- [ ] Task 3.1: Perform a test push/PR/merge via the agent and confirm the actor shown in the GitHub/GitLab UI differs from the developer's own actor.
- [ ] Task 3.2: Confirm the developer's own `gh auth status` / git configuration is unchanged.
- [ ] Task 3.3: Confirm no credential values were written to any tracked file in the repository.

## Progress

### Current Status

**As of 2026-09-22**: Planning complete; issue and feature folder created. No provisioning or wiring work has started yet.

### Blockers

- None yet. Provisioning the bot/service account on each host is an external, manual prerequisite before Phase 2 can begin.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-22 00:00:00.000Z - Created

Feature folder created from GitHub issue #148, capturing the plan for giving the coding agent its own git-hosting identity so agent-driven pushes/merges are distinguishable from the developer's own, without recording any credential values in the repository.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-22 00:00:00.000Z - Full autonomy retained, no commit signing

Agreed the agent should retain full push/merge autonomy (no added manual approval step) and that commit signing is out of scope for this iteration; identity separation via a dedicated bot/service account alone satisfies the attribution requirement.

### Related PRs / Commits

- None yet.

### More Information

Related GitHub issue: #148.
