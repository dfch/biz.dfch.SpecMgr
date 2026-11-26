---
status: accepted
decision-makers: dfch
id: 8cf940c5-3100-485c-a12d-14b59b631712
version: 1.0.0
---

# id/filename/addressing scheme: server-generated UUID, {id}-{slug}.md, directory-scan resolution

## Context and Problem Statement

ADR files must be addressable by the MCP tools via a unique identifier. The filename must be both human-readable and stable. Questions: (1) what format should the id be (sequential counter, UUID, etc.)? (2) what is the filename format? (3) how does the server resolve an id to a file path (cached index, directory scan, etc.)? (4) where is the ADR base directory?

## Decision Drivers

Human-readable filenames; unique, stable ids that don't require external state (counters); id resolution that works even after concurrent file edits; configurable base directory for different deployment contexts.

## Considered Options

Sequential counter filenames (0001-..., 0002-...) vs. UUID-prefixed filenames ({uuid}-{slug}.md); cached id-to-path index vs. fresh directory scan; CLI argument vs. environment variable for base-directory config.

## Decision Outcome

Use server-generated UUID strings as the `id` field (created once by create_adr, never reassigned). Filename format is `{id}-{slug}.md` where `slug` is derived from the ADR title at creation time. id-to-path resolution is performed via fresh directory scan + frontmatter parse on every call (no cached index), ensuring correctness under concurrent hand-edits. The ADR base directory is configurable via the `SPECMGR_ADR_DIR` environment variable (default `./docs/adr`). Option numbering within a single ADR uses a monotonically increasing, never-reused counter (not the id); deleting an option leaves a gap.

### Consequences

Filenames are human-readable and slug-based (e.g., `abc123-use-madr-4-0-0.md`). No external counter state required; UUIDs are globally unique. Fresh directory scans on every lookup guarantee correctness even after concurrent edits. Environment-variable config allows flexible deployment (different base directories for different test runs, CI, production). Trade-off: slightly longer filenames due to UUID prefix; directory scans are more expensive than O(1) index lookups, but acceptable at expected scale.

## More Information

id-to-path resolution is implemented in adr/tools/_paths.py: find_adr_path(id), iter_adr_paths(), adr_base_dir(). Option numbering is managed by models/adr/v1/mutations.py (option_create).
