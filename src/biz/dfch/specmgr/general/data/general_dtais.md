# DTAIS Verification Methods

The five valid `### AC-NNN (Method): ...` method words used by `vcr`'s
`## Acceptance Criteria` (and any other domain that needs to describe how
a criterion is verified):

- `Demonstration` -- observing the system in operation, without
  instrumented measurement, to confirm a qualitative or operational
  characteristic.
- `Test` -- exercising the system under controlled, instrumented
  conditions and comparing measured results against a quantitative
  threshold.
- `Analysis` -- using calculation, modeling, or simulation (not direct
  observation of the built system) to show a requirement is met.
- `Inspection` -- visual or procedural examination of the system,
  design artifacts, or source code, without operating the system.
- `Special` -- any other verification approach not covered by the four
  methods above, e.g. a formal third-party certification/compliance
  sign-off, a supplier's certificate of conformance, or another
  contractually-mandated special process.

## When to apply each method

- **`Demonstration`** -- use when the criterion is about observable
  behavior under realistic operating conditions and a pass/fail
  judgment can be made by watching the system perform, without needing
  instrumented measurement or a controlled test environment. Typical
  for showing that a feature works end to end, that a workflow
  completes, or that a user-facing capability is present. Not
  appropriate when the criterion carries a quantitative threshold (a
  latency budget, a throughput number, an error-rate ceiling) --
  those need `Test` instead, since a demonstration cannot rigorously
  confirm a numeric bound.
- **`Test`** -- use when the criterion states (or implies) a
  quantitative, measurable threshold: a performance budget, a
  tolerance, a pass/fail count against a specified input set, a
  boundary condition. Requires a controlled, instrumented environment
  and a documented, repeatable procedure -- this is exactly what the
  optional `#### Test Steps` sub-section under an acceptance criterion
  is for. Prefer `Test` over `Demonstration` whenever the criterion can
  be reduced to a measured number compared against a threshold.
- **`Analysis`** -- use when direct observation of the built system is
  not practical, not yet possible, or not the most rigorous way to
  confirm the requirement: calculation, modeling, simulation, or a
  static review of a design or specification (e.g. confirming a
  latency budget is achievable given known per-component overheads,
  without running a live test). Also the right choice for criteria
  that must be verified before the relevant part of the system exists
  yet, or for requirements about characteristics (capacity margins,
  worst-case bounds) that are more reliably shown by calculation than
  by sampling a live system.
- **`Inspection`** -- use when the criterion is about the presence,
  form, or content of an artifact -- source code, configuration,
  documentation, an error-message contract -- rather than about
  runtime behavior. Verified by visual or procedural examination
  without operating the system (e.g. reviewing a handler's source for
  a required error-handling branch, or checking that a document
  contains a required section). Prefer `Inspection` over
  `Demonstration`/`Test` whenever the system does not need to be run at
  all to confirm the criterion.
- **`Special`** -- use for verification approaches that fall outside
  the other four methods entirely: a required third-party
  certification or compliance sign-off (e.g. a security or regulatory
  compliance review board), a supplier's certificate of conformance
  for a purchased component, or another contractually-mandated special
  process that the document's own author cannot execute or verify
  directly. `Special` criteria are often the last ones to close on a
  verification case record, since they depend on an external party's
  own schedule rather than the author's own test/analysis/inspection
  activity.

## Relationship to `## Coverage`

`## Coverage` is the document-level roll-up of every `### AC-NNN
(Method): ...` entry's verification status, not a second, independent
outcome field:

- **`full`** -- every acceptance criterion has actually been verified
  via its stated method, with a passing result. There is no
  outstanding criterion, regardless of method -- a `full` verification
  case record with a `Special` criterion means the required
  certification/sign-off has already been obtained, not merely
  requested.
- **`partial`** -- at least one acceptance criterion has been verified
  successfully, but at least one other is still pending or outstanding.
  The typical pattern is a mix of methods the author can execute
  directly (`Demonstration`/`Test`/`Analysis`/`Inspection`, already
  passing) alongside a `Special` criterion still awaiting an external
  party's action -- e.g. an `AC-004 (Special): ...` criterion whose
  formal certification sign-off has not yet arrived, so the document's
  `## Coverage` is `partial` even though every criterion the author
  could verify directly has already passed. `## More Information` is
  the right place to record exactly what is still outstanding and why.
- **`none`** -- no acceptance criterion has been successfully verified
  yet, e.g. a freshly drafted verification case record whose criteria
  are defined but not yet executed against any method.

`## Coverage` therefore always reflects the least-verified criterion in
the set: one still-outstanding `Special` (or any other method's)
criterion is enough to keep the whole document at `partial`, no matter
how many other criteria have already passed.
