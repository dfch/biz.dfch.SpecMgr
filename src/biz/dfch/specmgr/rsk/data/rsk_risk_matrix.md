# The 5x5 risk matrix for `rsk` documents

Every `rsk` document carries two 5x5 assessments: `## Initial Assessment`
(BEFORE mitigation) and `## Residual Assessment` (AFTER mitigation). Each
assessment is one cell of the same risk matrix, given by two integer
coordinates — the probability that the risk event occurs, and the impact
if it does — both on a 1..5 scale, written in the H3 heading values
(`### Probability {1..5}`, `### Impact {1..5}`).

## Scale anchors

**Probability** (1..5) — how likely the risk event is:

- `1` = rare
- `5` = almost certain

Values 2..4 form a graduated scale between the two anchors (increasing
likelihood).

**Impact** (1..5) — how severe the consequence is:

- `1` = negligible
- `5` = severe

Values 2..4 form a graduated scale between the two anchors (increasing
severity).

## Zone table

The matrix cell for a given probability `p` and impact `i` is the zone of
their product `p x i`:

| p \ i | 1        | 2        | 3         | 4         | 5         |
|-------|----------|----------|-----------|-----------|-----------|
| 5     | medium   | high     | very high | very high | very high |
| 4     | low      | medium   | high      | very high | very high |
| 3     | low      | medium   | medium    | high      | very high |
| 2     | low      | low      | medium    | medium    | high      |
| 1     | low      | low      | low       | low       | medium    |

## Product thresholds

The zone is derived from the product `p x i` (range 1..25):

- `1-4` → `low`
- `5-9` → `medium`
- `10-14` → `high`
- `15-25` → `very high`

These are the same thresholds the schema derives: the `level` of each
assessment is a computed field from the product (1-4 `low`, 5-9 `medium`,
10-14 `high`, 15-25 `very high`) and is never written into the document.

## Reading initial and residual together

The two assessments form the register's audit trail for the treatment:

- `## Initial Assessment` is the risk as identified, before any measures.
- `## Strategy` (TARA: `transfer`/`accept`/`reduce`/`avoid`) names the
  chosen response.
- `## Mitigation` holds the concrete measures.
- `## Residual Assessment` is the risk after those measures.

A `reduce` strategy implies residual < initial: the mitigation must move
the cell to a lower zone (or at least a lower product) — e.g. initial
4x3=12 (`high`) → residual 2x3=6 (`medium`). A `transfer` lowers the
residual exposure that remains with the organization; an `avoid` removes
the risk rather than leaving a meaningful residual cell; an `accept`
leaves the residual equal to the initial (no treatment was taken), and the
entry's `status` records the acceptance. If a `reduce` entry's residual
assessment is not lower than its initial one, the mitigation section does
not support the claimed strategy and the entry should be reviewed.
