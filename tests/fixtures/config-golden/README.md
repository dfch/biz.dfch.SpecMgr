# config-golden fixtures

Pre-migration `specmgr://config` golden (feat-208, Task 110.115 — REQ-005,
ACC-005): the resource's exact JSON payload captured BEFORE Phase 120's
base-dir read-site migration, so Task 140.120 can prove the migration
changed no observable behaviour (byte-identical output).

## `specmgr-config.pre-migration.json`

The `specmgr://config` resource's own serialized payload
(`general.resources.config.config_info()`'s `ConfigInfo` result through the
mcp SDK's resource serialization path — `pydantic_core.to_json(result,
fallback=str, indent=2).decode()`, the `FunctionResource.read` call for a
non-`str` return; not a hand-rolled dump), captured under controlled
conditions:

- **CWD**: a fresh temp dir `T0` (`tempfile.mkdtemp`); every `base_dir`
  field in the payload is `T0`-prefixed and absolute — the fixture keeps
  `T0`'s absolute paths **raw** (the `T0` prefix of this capture is
  visible in the file; normalization happens only in the Phase 140
  comparison test).
 - **Environment**: none of the 12 registered env vars set
   (`SPECMGR_DOCS_DIR`, `SPECMGR_FEAT_DIR`, `SPECMGR_MCP_TRANSPORT`,
   `SPECMGR_MCP_HOST`, `SPECMGR_MCP_PORT`, `SPECMGR_SIMILARITY_DISABLED`,
   `SPECMGR_FEAT_WARMUP_DISABLED`, `SPECMGR_PLANTUML_JAR`,
   `SPECMGR_PLANTUML_BIN`, `SPECMGR_PLANTUML_URL`, `SPECMGR_TESTS_NO_DOTENV`,
   `FASTEMBED_CACHE_PATH`) — hence every `env_var_set`/`disabled`/`set`
   flag is `false` and `selected` is `"none"`.
- **Install**: the standard all-extras venv, so the `similarity` section's
  `extra_installed` (`find_spec("fastembed")`, a spec lookup, never an
  import) is stably `true`.
- **Capture process**: the eight non-`cli` owning modules imported first
  (so the registry — and therefore the set of names removed from the
  environment — is full), `cli` deliberately NOT imported (its
  module-level dotenv load is a side effect the capture must not run);
  `SPECMGR_TESTS_NO_DOTENV` (the `cli`-owned 13th var) removed by its
  literal name.

The `similarity.cache_dir` field is the **process** temp dir
(`<tempdir>/fastembed_cache`, i.e. `FASTEMBED_CACHE_PATH`'s own fallback
expression), NOT `T0` — that is today's behaviour and must be preserved
by the migration.

## Phase 140 contract (Task 140.120)

After Phase 140's migrations (the Typer defaults + the `FASTEMBED_CACHE_PATH`
config read routed through the registry accessor), the same capture
procedure must produce JSON that is **byte-identical** to this fixture once
the temp-dir prefixes are normalized (the `T0` capture prefix in the
`base_dir` fields, and the process temp dir in `cache_dir`). The
comparison test does NOT live in this phase.

## `specmgr-config.post-sharding.json`

Post-sharding `specmgr://config` golden (feat-245 Phase 125, Task 125.120
— REQ-003): the resource's exact JSON payload captured AFTER the sharded
layout landed, through the same serialization path and under the same
controlled conditions as the pre-migration fixture above. The only
intended difference to `specmgr-config.pre-migration.json` is the thirteen
`SPECMGR_DOCS_DIR` domains' `base_dir` values gaining the `/en` suffix
(`docs/<type>/en` — the omitted-language resolution of feat-245's uniform
sharded layout); the `feat` domain's `base_dir` and every other field are
unchanged.

**The live byte-comparison test in `tests/general/resources/test_config.py`
(`TestConfigGoldenIdentity`) compares against THIS post-sharding fixture**
once the temp-dir prefixes are normalized — not against the pre-migration
one: feat-245's sharding is an intended, observable payload change, so the
pre-migration fixture is no longer a live comparison target. It is kept as
an immutable provenance baseline (never regenerated, never renamed): it
documents the captured-BEFORE state that proved feat-208's migration
changed no observable behaviour, and the contract text above about that
baseline stays true. `test_config.py` additionally pins the distinction
itself (the pre-migration fixture's thirteen `base_dir` values carry no
`/en` suffix; the post-sharding one's do).
