# TARA risk-response strategies for `rsk` documents

`rsk` documents (risk register entries) carry a mandatory `## Strategy`
section with exactly one lowercase word naming the TARA response chosen for
the risk. **TARA** is the risk-response framework: **T**ransfer, **A**ccept,
**R**educe, **A**void. Only the four valid words below are accepted by the
schema — anything else (including the TARRA-era words `tolerate`, `assign`,
`recover`, or any capitalized/compound variant) is a validation error:

- `transfer`
- `accept`
- `reduce`
- `avoid`

## When to apply each strategy

Read the risk's matrix coordinates (`## Initial Assessment`, see the risk
matrix document) to pick a strategy:

- **Low probability / high impact → `transfer`**
  The risk is unlikely but would be severe if it hit. Shift the consequence
  to a party better able to bear it: an insurer, a vendor contract with
  liability clauses, or another organization that owns the exposure.
- **High probability / high impact → `avoid`**
  The risk is both likely and severe. Do not proceed with the activity that
  carries it: eliminate the `## Cause` or the `## Trigger` (drop the
  feature, change the design, refuse the input). An `avoid` strategy
  typically closes the risk entry (`status: closed`/`dropped`) rather than
  leaving residual exposure.
- **High probability / low impact → `reduce`**
  The risk is likely but the consequence is bounded. Apply `## Mitigation`
  measures that lower the probability or the impact (guardrails, checks,
  whitelists, redundancy) so the residual risk lands in a lower zone.
- **Low probability / low impact → `accept`**
  The risk is unlikely and bounded. No treatment is warranted: keep
  `## Mitigation` as `none` and monitor the risk in the register.

The four quadrants are a guideline, not a rule — the documented
rationale of the choice matters more than the quadrant label, and a risk
near a quadrant boundary may legitimately take an adjacent strategy.

## Interaction with `## Mitigation`

`## Mitigation` is the treatment section between the two assessments and
holds the concrete measures bridging `## Initial Assessment` and
`## Residual Assessment`:

- `reduce`: concrete measures are mandatory (e.g. "Replace the parser with
  a maintained library; restrict uploads to a format whitelist."). The
  residual assessment must reflect their effect.
- `transfer`: name the transfer mechanism (contract clause, insurance
  policy, delegated owner). Residual exposure is what remains after the
  transfer.
- `avoid`: describe what is eliminated (the cause, the trigger, or the
  activity itself).
- `accept`: write `none` — acceptance means no treatment is taken.

## Interaction with the frontmatter `status`

The `rsk` frontmatter `status` is a six-value lifecycle:

- `open` — identified and monitored; no treatment decided or started yet.
- `mitigating` — `## Mitigation` treatment is in progress (typically
  `strategy: reduce` or `transfer`); the residual assessment is provisional
  until the measures land.
- `accepted` — the residual risk is formally accepted (typically
  `strategy: accept`, or a `reduce` whose residual zone is tolerated).
- `occurred` — the risk event materialized; the entry is tracked as an
  incident alongside its mitigation history.
- `closed` — resolved or expired (typically `strategy: avoid`, or all
  measures completed and verified).
- `dropped` — removed from the register (not a real risk, a duplicate, or
  out of scope).

`status` tracks the lifecycle state of the entry; `strategy` tracks the
chosen response. They are independent fields: an `open` entry already has
a `strategy` (every risk in a register has a disposition), and a
`mitigating` entry's `strategy` is whatever response is being executed.
