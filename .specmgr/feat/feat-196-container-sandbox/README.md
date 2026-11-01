---
classification: null
created: '2026-10-06T07:35:24.052+02:00'
id: feat-196-container-sandbox
status: planning
type: feat
updated: '2026-10-06T07:35:24.052+02:00'
version: 1.0.0
---

# Feature: Containerized Sandbox for Per-Worktree OpenCode Sessions

## Plan

### Overview

Parallel OpenCode sessions (one per `git worktree`, used to work on multiple features at once) currently run directly on the host with no isolation: an agent's `bash`/search tools can wander the whole filesystem (e.g. `find /`), which is expensive, rude, and distracts the agent with context that should never have been in scope. This feature adds an opt-in devcontainer-based sandbox -- one container per feature branch, built on an independent `git clone` from `origin` (no host worktree/`.git` directory coupling) -- plus a lightweight, always-on `opencode.json` permission baseline as defense in depth regardless of whether the container is used.

### Requirements

- REQ-001: Each sandboxed session runs in its own container, cloned directly from `origin` for a given branch, with no bind mount of the host's `.git` directory or any other worktree.

- REQ-002: Git authentication inside the container uses a scoped, short-lived GitHub token/`gh`-CLI credential passed in via environment variable -- never the host's real SSH key.

- REQ-003: A host-side wrapper script can bring up a container for a given branch and drop straight into an `opencode` session inside it.

- REQ-004: Network egress restriction is supported as an explicit, opt-in mode, off by default, selected via a separate devcontainer config rather than a runtime flag on the default one.

- REQ-005: A baseline `opencode.json` permission configuration (denying whole-filesystem `bash`/`external_directory` scans) is added independently of the container work, since it is useful with or without the sandbox.

### Acceptance Criteria

- [ ] ACC-001: `scripts/oc-sandbox.sh <branch>` brings up a container that has cloned only the given branch of this repo and nothing else from the host filesystem, and drops into an `opencode` session inside it.

- [ ] ACC-002: Running `find /` (or an equivalent whole-filesystem scan) inside the container only sees the container's own filesystem, never the host's.

- [ ] ACC-003: `scripts/oc-sandbox.sh <branch> --restricted` brings up the same container with network egress restricted, using a clearly marked placeholder allowlist (GitHub, PyPI) ready to extend with a model-provider host when needed.

- [ ] ACC-004: A committed `opencode.json` denies `find /*`-style whole-filesystem bash invocations and restricts `external_directory` to the workspace, independent of container use.

### Scope

#### Included

- `.devcontainer/Dockerfile` (uv/Python + Node + `opencode` + `gh` CLI).

- `.devcontainer/devcontainer.json` (default, open network, clone-from-origin).

- `.devcontainer/devcontainer.restricted.json` (opt-in, adds `NET_ADMIN`/`NET_RAW` + firewall init script with a placeholder allowlist).

- `scripts/oc-sandbox.sh` host-side wrapper (`devcontainers/cli`-based).

- Baseline `opencode.json` permission rules (bash/external_directory scoping).

#### Explicitly Out Of Scope

- Actually enabling/enforcing the network-restriction mode by default -- it ships off, as an option only.

- Filling in the restricted mode's model-provider allowlist entries -- left as a placeholder until a specific provider/host is chosen.

- Any change to how `git worktree` itself is used on the host; this feature only changes how a session inside a container obtains the branch (independent clone, not a worktree mount).

- Remote/cloud devcontainer backends (Codespaces, Gitpod) -- local Docker/Podman only for now.

### Dependencies

#### Depends On

- None.

#### Blocks

- None.

### Design Notes

Originating discussion covered the alternatives considered:

- Why not mount the host worktree + shared `.git` into the container? Linked `git worktree` checkouts point their `.git` file at the main repo's `.git/worktrees/<slug>` directory, so a container would need that exact host path bind-mounted too, breaking portability (CI, a different host) and introducing a narrow race if two containers' sessions touch shared refs or run `git gc` concurrently. Independent clone-per-container avoids all of this.

- Why keep network restriction as an opt-in, not the default? It is not currently enforced by policy, and specifying a correct, working egress allowlist (model-provider API host, GitHub, package registries) up front would require answers that are not needed yet. Shipping it as a separate `devcontainer.restricted.json` keeps the default path simple while leaving a ready-made place to fill in the allowlist later.

- Why a fine-grained PAT/`gh` token instead of mounting `~/.ssh`? Scoped to this one repo, easy to rotate/revoke, and avoids exposing the host's real SSH private key material to every ephemeral container.

### Related Decisions

- None yet.

### Task List

#### Phase 100: Image and Base Container Config

- [ ] Task 100.100: Write `.devcontainer/Dockerfile` (uv/Python base, Node, `git`, `opencode` CLI via `npm install -g opencode-ai`, `gh` CLI, non-root user with host-matched UID/GID).

- [ ] Task 100.110: Write `.devcontainer/devcontainer.json` (default/open-network variant) with `containerEnv`/`remoteEnv` for `GH_TOKEN`/`BRANCH` and a `postCreateCommand` doing a partial `git clone` + checkout + `uv sync --all-extras --frozen`.

- [ ] Task 100.120: Verify a container built from this config can clone the repo, check out a branch, and run `uv run --frozen pytest` successfully with no host filesystem access beyond the container's own clone.

#### Phase 110: Restricted Network Variant (Opt-In)

- [ ] Task 110.100: Write `.devcontainer/devcontainer.restricted.json` adding `NET_ADMIN`/`NET_RAW` capabilities to `runArgs` and a `postStartCommand` invoking the firewall init script.

- [ ] Task 110.110: Write `init-firewall.sh` (baked into the image, inert unless invoked) with default-deny egress, DNS/loopback/established allowed, and placeholder allowlist entries for GitHub and PyPI plus a TODO line for the model-provider host.

- [ ] Task 110.120: Verify the restricted container can still clone/push to GitHub and run `uv sync`, and that an arbitrary unlisted host is unreachable from inside it.

#### Phase 120: Host Wrapper and Defense-in-Depth Config

- [ ] Task 120.100: Write `scripts/oc-sandbox.sh <branch> [--restricted]`, selecting the `--config` path accordingly, passing `BRANCH`/`GH_TOKEN` through, and running `devcontainer up` plus `devcontainer exec -- opencode`.

- [ ] Task 120.110: Add a baseline `opencode.json` with `permission.bash`/`external_directory` rules denying whole-filesystem scans, scoped to the workspace directory.

- [ ] Task 120.120: Document the sandbox workflow: how to mint the scoped PAT, how to invoke the wrapper script, and how/when to flip on the restricted variant later.

## Progress

### Current Status

**As of 2026-10-06**: Feature just created from a planning discussion; no implementation has started yet.

### Blockers

- None yet.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-06T12:00:00.000Z - Created

Feature created from a plan-mode discussion about isolating parallel OpenCode sessions running against multiple `git worktree` checkouts. Settled on clone-per-container (not a worktree/`.git` mount) after weighing isolation/portability trade-offs, a fine-grained PAT/`gh`-token auth model, and an opt-in (off-by-default) network-restriction variant. Tracked under GitHub issue #196.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-06T12:00:00.000Z - Clone-per-container instead of worktree/.git mount

Chose to have each container perform its own independent `git clone` from `origin` rather than bind-mounting the host's `git worktree` checkout and its shared main-repo `.git` directory. The worktree model's benefits (shared object store, instant creation, local-branch visibility without pushing) matter for host-side parallelism, not for a long-lived per-branch container, whereas the mount approach couples the container to an exact host path and introduces a narrow race on shared refs. Independent clone-per-container is fully portable (works unmodified in CI or on a different host) at the one-time cost of a clone per container, mitigated with a partial clone.

### Related PRs / Commits

- [Issue #196](https://github.com/dfch/biz.dfch.SpecMgr/issues/196): tracking issue for this feature.

### More Information

None.
