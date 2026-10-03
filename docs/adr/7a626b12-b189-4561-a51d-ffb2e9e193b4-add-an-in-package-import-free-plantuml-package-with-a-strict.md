---
status: accepted
date: '2026-10-03'
decision-makers: dfch
id: 7a626b12-b189-4561-a51d-ffb2e9e193b4
version: 1.0.0
---

# Add an in-package, import-free plantuml package with a strict first-set-wins validation-source chain

## Context and Problem Statement

feat-185-uc-diagrams (GitHub issue #185) formalises the ad-hoc UC → PlantUML pipeline as a versioned part of the package: deterministic renderers for the per-UC usecase diagram, the multi-UC package diagram, and the sequence-diagram skeleton, plus a validation layer for the emitted .puml files (PlantUML ~1 URL encoder, two-mode structure checker, jar/bin/url backends, chain resolver, result model). Two coupled, architecture-level decisions were left unresolved by the plan and are needed before Phase 110 implements the library:

1. Where the PlantUML library lives in the repo. The structure checker's contract is specmgr's emitted subset — it lints what specmgr's own renderers emit, not arbitrary PlantUML (plan Design Notes §6). The plan fixes the placement as src/biz/dfch/specmgr/plantuml/, import-free and stdlib-only, but the alternatives were only weighed in the feature's Decisions Made log, not in an ADR.
2. How the validation chain selects and degrades across sources. The plan freezes exactly three env vars (SPECMGR_PLANTUML_JAR / SPECMGR_PLANTUML_BIN / SPECMGR_PLANTUML_URL) and a strict selection policy (Decisions Made 2026-10-03 08:05, "Strict source selection, no fall-through"), but the policy has consequences beyond this feature: a privacy invariant (a typo'd local source must never silently send diagram content to the public plantuml.com server) that every future diagram domain inherits.

The two are coupled: the chain policy is a property of the library's contract (implemented in plantuml/chain.py and pinned by its no-fall-through test, ACC-003), and the library's placement determines who inherits both. Per the repo's ADR-vs-feature-decision rule (AGENTS.md), both belong in an ADR — they affect more than one feature (the plan's "Blocks": future diagram features for other domains reuse the package and the chain semantics) — and are recorded here together, user-confirmed 2026-10-03.

## Decision Drivers

- The structure checker's contract is specmgr's emitted subset, not a general PlantUML grammar engine — it does not need to be independent of specmgr (plan §6).
- Consuming projects already depend on specmgr: the diagram files live next to specmgr artifacts (<project>/diagrams/uc/), so a second published library would serve no new consumer.
- One published artifact: no second PyPI coordinate to version, publish, or secure.
- Future diagram domains (other than uc) will reuse the package and the chain semantics (plan "Blocks" section).
- The privacy invariant: a set-but-unavailable local source must never silently contact the public server — the policy must make that structurally impossible, not merely tested for (Decisions Made 2026-10-03 08:05).
- Extraction cost must stay cheap in case the subset contract ever outgrows specmgr: import-free (no specmgr imports) and stdlib-only (no new dependency or extra).
- The base library's dependency surface must not change: plantuml/ adds no dependency and no extra (pyproject.toml dependencies stays pydantic + python-dotenv).

## Considered Options

This ADR records two coupled decisions: Options 1–4 for the plantuml/ package placement, Options 5–7 for the validation-chain policy.

- Option 1 (chosen): a new top-level cross-cutting package src/biz/dfch/specmgr/plantuml/ (alongside general/ and models/), import-free, stdlib-only, and NOT a separate PyPI library.
- Option 2: a per-domain copy under uc/plantuml/ — the library local to its first consuming domain.
- Option 3: a separate PyPI library that specmgr depends on.
- Option 4: a vendored third-party PlantUML client/validation library.
- Option 5 (chosen): the strict first-set-wins, no-fall-through chain — exactly three env vars, the first set variable is the only source, a set-but-unavailable source is a hard failure, and only the all-unset state degrades (to the structure-only floor).
- Option 6: a fall-through chain — a misconfigured first source degrades to the next set source.
- Option 7: PATH auto-discovery plus a public plantuml.com default — no configuration required.

## Decision Outcome

Option 1 for placement and Option 5 for the chain policy, recorded together because the policy is a property of the library's contract.

Placement. A new top-level cross-cutting package src/biz/dfch/specmgr/plantuml/ (created in Phase 110) holds encode.py (the ~1 URL encoder), structure.py (the two-mode structure checker plus the shared UNATTRIBUTED marker constant), backends.py (jar + bin), url.py (the single-/svg/-endpoint matrix classifier), and chain.py (the strict chain resolver plus the result model). The package is import-free — no specmgr imports; the dependency direction is always specmgr-domain → plantuml/, never the reverse — stdlib-only (no new dependency or extra; pyproject.toml is unchanged), and not a separate PyPI library (one published artifact; the checker's contract is specmgr's emitted subset; consuming projects already depend on specmgr). Import-free + stdlib-only keeps extraction cheap if the subset contract ever outgrows specmgr.

Chain policy. Validation source selection is strict and configuration-driven over exactly three env vars — SPECMGR_PLANTUML_JAR (path to plantuml.jar, invoked as java -jar <jar> <args>), SPECMGR_PLANTUML_BIN (path to an executable speaking the PlantUML CLI contract — a distro binary or a user-owned platform adapter), SPECMGR_PLANTUML_URL (base URL of a PlantUML server, prefix included) — with no defaults, no PATH auto-discovery, no public default, and no opt-in flags. The first set variable is the only source used: there is no fall-through to any other source on misconfiguration, so a set-but-unavailable JAR with a set public URL never contacts the public URL. A set-but-unavailable source (bad path, missing java, unreachable URL, failed canary) is a hard validation failure — no file write, no call to any other source, no network — reported via the non-raising result's source_state = misconfigured/unavailable with reason + fix_hint. Only the all-unset state degrades, to the structure-only floor (agent path: the sequence file is written with a ' validated: structure-only header comment; CLI path: the deterministic output carries no such header — checker-clean by construction, ACC-001). The full frozen semantics (result-model shape, canary memoisation, chain short-circuit, prompt contract) are recorded in the rulebook specmgr://uc/plantuml §3 and implemented in plantuml/chain.py.

### Consequences

Positive:

- One published artifact, no second PyPI coordinate to version, publish, or secure; future diagram domains get the encoder, checker, backends, and chain with a single import (biz.dfch.specmgr.plantuml).
- The privacy invariant is structural, not aspirational: the no-fall-through chain has no code path that contacts a non-selected source, so a typo'd local source cannot silently phone diagram content to plantuml.com (pinned by ACC-003 with a mocked transport).
- Extraction stays cheap: import-free + stdlib-only means plantuml/ could be lifted out as its own library later without refactoring the rest of the package.
- The base library's dependency surface is unchanged (no new dependency or extra).

Negative / trade-offs:

- The top-level package list grows by a third non-domain package alongside general/ and models/; AGENTS.md's package enumeration must be updated to keep the domain-first story honest (Phase 110, Task 110.175). plantuml/ is not a document type, so it deliberately sits outside the domain-first hierarchy of the document domains.
- A per-domain placement was rejected: a second diagram domain would have to import across domains (uc.plantuml) or duplicate the whole library — both worse.
- No PATH discovery and no public default: a fresh environment with no SPECMGR_PLANTUML_* set has no authoritative validation — only the structure floor. Deliberate (privacy + offline by default), but a user expecting "it just works" must set exactly one variable.
- The strict chain rejects misconfigurations a fall-through chain would paper over: a set-but-broken JAR alongside a healthy set URL is a hard failure, not a degraded success. The failure is explicit, named, and fixable — by design.

### Confirmation

User-confirmed 2026-10-03 (the Phase 100 brief records the decision: a full ADR covering both coupled decisions, "do not re-litigate"). Phase 110 implements and gates it: plantuml/chain.py + result model with the no-fall-through privacy test (ACC-003, mocked transport) and the structure-red short-circuit test; the rulebook specmgr://uc/plantuml (created in the same Phase 100) records the full frozen semantics.

## Pros and Cons of the Options

### Option 1: In-package top-level plantuml/ (chosen)

#### Pros

- One published artifact: no second PyPI coordinate to version, publish, or secure; specmgr consumers get the library for free.
- Future diagram domains reuse the encoder, checker, backends, and chain with a single import (biz.dfch.specmgr.plantuml) — the plan's "Blocks" section assumes exactly this.
- Import-free + stdlib-only keeps extraction cheap if the subset contract ever outgrows specmgr.
- Consistent with the existing cross-cutting placement of general/ and models/ for non-domain code.

#### Cons

- A third top-level non-domain package; AGENTS.md's package enumeration must be updated (Phase 110) to keep the domain-first story honest.

### Option 2: Per-domain copy under uc/plantuml/

#### Pros

- Keeps uc/ self-contained; no top-level surface change in this feature.

#### Cons

- A second diagram domain must either import across domains (uc.plantuml from a future domain — an inverted, surprising dependency) or duplicate the whole library.
- A repo-wide privacy invariant would sit inside one domain, mis-signalling its scope.

### Option 3: Separate PyPI library

#### Pros

- The cleanest boundary if the checker contract ever generalises beyond specmgr's emitted subset; independently versioned.

#### Cons

- A second published artifact to version, publish, and secure, for a contract that is specmgr's emitted subset today.
- Consuming projects already depend on specmgr (the diagrams live next to specmgr artifacts); the library would serve no new consumer.
- Cross-repo development friction for what is, in this feature, one codebase.

### Option 4: Vendored third-party PlantUML library

#### Pros

- Someone else would maintain the PlantUML protocol details.

#### Cons

- No maintained third-party Python library covers the exact contract needed (single /svg/~1 endpoint classification matrix, jar/bin subprocess contract, two-mode structure checker over the emitted subset) — vendoring would mean maintaining a fork.
- A third-party dependency (or a vendored copy of one) violates the stdlib-only / no-new-dependency driver and the offline-by-default posture.

### Option 5: Strict first-set-wins, no fall-through (chosen)

#### Pros

- The privacy invariant is structural: no code path exists that contacts a non-selected source, so a typo'd local source can never silently phone diagram content to plantuml.com.
- Deterministic: the source used is a pure function of the environment; failures are explicit (source_state + reason + fix_hint), never papered over.
- Simple to reason about and to test (ACC-003 pins zero HTTP requests with a mocked transport).

#### Cons

- Rejects misconfigurations a fall-through chain would paper over: a set-but-broken JAR alongside a healthy set URL is a hard failure.
- A fresh environment with no variable set has no authoritative validation (structure floor only) — deliberate, but a "it just works" surprise for some users.

### Option 6: Fall-through chain (degrade to the next set source)

#### Pros

- More tolerant of partial misconfiguration: a broken JAR still gets URL validation.

#### Cons

- Breaks the privacy invariant in exactly the typo scenario it should catch: a misspelled SPECMGR_PLANTUML_JAR path with SPECMGR_PLANTUML_URL set to plantuml.com silently sends diagram content to the public server.
- The source used becomes a function of runtime reachability, not just the environment — non-deterministic across machines and over time.

### Option 7: PATH auto-discovery plus a public plantuml.com default

#### Pros

- Zero configuration: a machine with plantuml on PATH or network access validates out of the box.

#### Cons

- The public default sends diagram content to a third-party server on every validation call for users who never opted in — the exact outcome the privacy invariant exists to prevent.
- PATH discovery makes the source machine-dependent and unpinnable (CI and dev machines may run different plantuml versions); it defeats the version-pinning driver (rulebook §7.3 recommends a pinned JAR).

## More Information

- FEAT feat-185-uc-diagrams — the feature plan (.specmgr/feat/feat-185-uc-diagrams/README.md): §1 artifact map, §2 mapping spec, §3 validation chain, §4 local invocation contract, §5 URL protocol, §6 structure checker, §8 platform adapters; Decisions Made 2026-10-03 08:05 ("Strict source selection, no fall-through", "Backends are jar/bin/url only; platforms adapt via user-owned ..._BIN scripts", "plantuml/ lives in-package (import-free, stdlib-only), not as a separate PyPI library").
- The rulebook specmgr://uc/plantuml (uc/data/uc_plantuml.md), created in Phase 100 of the same feature, is the normative frozen spec both decisions drive; it is served as text/markdown (the domain-knowledge resource shape, the specmgr://rsk/tara precedent).
- Non-raising structured-result precedent for the chain result model: ADR 519d1206-4d2a-4500-9046-6db635209996.
- Platform adapters (docker/k8s/CI/air-gapped) remain user-owned executables and deployments behind SPECMGR_PLANTUML_BIN/SPECMGR_PLANTUML_URL; specmgr ships no wrapper (rulebook §7).
