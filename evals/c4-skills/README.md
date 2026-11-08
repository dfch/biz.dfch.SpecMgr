# c4-skills measurement harness (feat-250, Phase 100)

Reproducible container harness that measures OpenCode agent skills for C4
modeling with Structurizr DSL. It runs an OpenCode agent **in an isolated
container** against the local model `qwen3.8-27b-bf16-896k` on the shared
sys0 vLLM server, one trial at a time, and grades the produced workspace
with the **real Structurizr CLI** (never by grepping the DSL).

Development-only: standard library only, not part of the wheel, not part of
the packaged harness bundle, and never imported from `src/`.

## Layout

```
evals/c4-skills/
├── run.py                  # thin launcher (the run entry point, Task 100.100)
├── README.md               # this file
├── c4_skills/              # the importable package (stdlib only)
│   ├── pins.py             # every version pin, the version tuple, the hashes
│   ├── preflight.py        # Task 100.180: record the environment, check the pins, idle check
│   ├── occonfig.py         # Task 100.110: the injected OpenCode configuration
│   ├── sidecar.py          # Task 100.120: the pinned structurizr/mcp sidecar (ephemeral host port)
│   ├── upstream.py         # Task 100.110: run-time fetch of jrjsmrtn/c4-skills at the pinned SHA
│   ├── events.py           # Task 100.140: parser for `opencode run --format json` NDJSON
│   ├── metrics.py          # Task 100.140: validated_before_return, call counts, triage, ...
│   ├── graders.py          # the case gates over the real CLI (pure + Docker collection)
│   ├── stats.py            # Wilson intervals, pass^k, the ACC-008/ACC-012 margin checks
│   ├── report.py           # Task 100.150: report.md + report.json
│   ├── cache.py            # Task 100.130: result cache for `none`/`upstream`
│   ├── runner.py           # Task 100.130: sequential trials, seed, timeout, contention, cache
│   ├── cli.py              # the subcommands (preflight / probe / run / report)
│   └── cases/__init__.py   # the case definitions (Phase 100: the smoke case)
├── results/                # committed, reproducible run records (small)
│   ├── smoke-*/            # preflight.json, run.json, report.{md,json}, trials/
│   └── provenance.md       # Task 100.190: license/provenance table
├── work/                   # gitignored: fresh trial work dirs + the captured
│                           # event streams (over-limit ones never committed)
└── cache/                  # gitignored: result cache + the fetched upstream checkout
```

## Why this layout (Task 100.100 decision)

`evals/c4-skills/` is not a legal Python package name (the hyphen), and the
harness must stay out of the wheel. The least-invasive solution: an inner
importable package `c4_skills/` plus the thin launcher `run.py`, which puts
the harness root on `sys.path` before dispatching to `c4_skills.cli.main`.
The unit tests do the identical `sys.path` insertion in
`tests/evals/conftest.py`, so nothing is installed and `pyproject.toml` is
untouched (no `evals/` in `[tool.setuptools]`, no import from `src/`). This
is feature-scoped development infrastructure, so the decision is recorded
in the feat README's Updates/Decisions Made log, not in an ADR (per the
AGENTS.md "ADR vs. feature-level Decisions Made" criteria).

## How to run

Everything runs under the project's uv-managed Python 3.13 (the pin is
asserted by the preflight); Docker and `jq` are host prerequisites.

```bash
# 1. preflight: record versions, check the pins, report the vLLM idle state
uv run --frozen python evals/c4-skills/run.py preflight

# 2. probe: one trivial trial through the full chain (config + provider + MCP + events)
uv run --frozen python evals/c4-skills/run.py probe

# 3. the Phase 100 smoke run (Task 100.170): the smoke case, none vs upstream, k=2
uv run --frozen python evals/c4-skills/run.py run \
    --cases smoke-create-system --conditions none,upstream --k 2 --label smoke

# 3b. Phases 110-150 add the skill condition with its variant directory
#     (one skill folder, or a root of skill folders; hashed + copied into
#     every skill trial's work dir before the container starts):
uv run --frozen python evals/c4-skills/run.py run \
    --cases <phase-cases> --conditions none,upstream,skill --k 5 \
    --skills-dir .opencode/skill/<name> --label <phase>

# 4. rebuild the report of an existing run
uv run --frozen python evals/c4-skills/run.py report --results-dir evals/c4-skills/results/<run-id>
```

Exit codes: `0` ok; `1` a runtime-shaped failure (a pin/preflight
violation, the sidecar or a trial container failing, a runner error, a
hung Structurizr CLI run -- the graders' `_run_cli` maps its 300 s
`subprocess.TimeoutExpired` to `RuntimeError`, Task 125.130/I3 -- an I/O
failure); `2` a usage-shaped failure (an invalid argument such as
`k <= 0` or a missing/misplaced `--skills-dir`, an unknown case, or a
missing artifact the command needs, e.g. `report` on a dir without
`run.json`). Any other exception type is a harness bug and stays a raw
traceback. The `probe` subcommand's failed outcome is a `2` by its own
convention (a probe that did not verify the chain is not a pin failure).

## Isolation and the shared server

- One fresh work dir + one fresh container per trial; the container gets no
  host OpenCode config, no `AGENTS.md`, no skills except the condition's,
  and the injected config denies `webfetch`/`websearch`/`question`.
- The trial container uses `--network host` (vLLM and the sidecar are bound
  to `127.0.0.1` on the host; there is no bridge route to them). "Isolation"
  is filesystem/config isolation, not network isolation.
- The harness starts its own pinned `structurizr/mcp` sidecar on a free
  ephemeral host port and tears it down after the run; the development MCP
  on port 3000 is never used. Port selection is racy (bind/close ->
  container bind): a sidecar whose logs show a bind/port-in-use failure is
  retried with a fresh port (up to 3 attempts), any other failure aborts
  with the port and the log evidence named.
- The vLLM server is shared (2 sequence slots). The runner refuses to start
  a trial while `vllm:num_requests_running > 0` (it waits, then re-checks
  between trials) and **flags** -- never fails -- a trial that ran while
  another client was active.
- `none`/`upstream` results are cached per (case, condition, version tuple,
  grader hash, skill variant hash); `skill` trials are never cached.

## Pins (the version tuple)

See `c4_skills/pins.py`: `ghcr.io/anomalyco/opencode:2.2.5` (+ digest),
`structurizr/mcp:2026.04.20` + `structurizr/structurizr:2026.10.26-noble`
(the spike-verified matching pair, + digests), vLLM 0.26.0 serving
`qwen3.8-27b-bf16-896k`, host Python 3.13.13, jq 1.6, the
`jrjsmrtn/c4-skills` commit `e86d8a91d3ed793cdf6c035f01d19f1b18cc8b6b`, and
the injected sampling parameters (temperature 0.0, top_p 1.0, seed 1337).
The preflight re-checks the mutable values with every run and aborts on a
mismatch.

## Tests

`tests/evals/` (unittest style, no model call): the event-stream parser and
metrics over pinned fixtures (a verbatim probe capture + a synthetic
tool stream), the graders over pre-exported CLI JSON fixtures (the
known-good/known-bad/known-weak split, ACC-006), the Wilson/pass^k/margin
machinery, the pins/cache/report machinery, and the runner/sidecar/CLI
robustness logic (pure Python, the container layer mocked). The four
Docker-dependent CLI tests skip when Docker is missing. The pre-commit
`pytest` hook is scoped to `src/`+`tests/`+`evals/` changes (a harness-code
change alone also triggers the local suite; CI's full matrix covers it
regardless), so `tests/evals/` runs in pre-commit and CI like every other
test; ruff lints `evals/` from the repo root automatically, and pylint
(advisory, `git ls-files '*.py'`) sees the files once committed.
