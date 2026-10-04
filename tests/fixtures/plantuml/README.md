# PlantUML recorded fixtures (feat-185-uc-diagrams, Phase 110 — amended 2026-10-04)

Recorded **2026-10-04** (re-recorded after the URL-protocol amendment to the
classic encoding — rulebook §5.1) from live servers, for the **offline**
URL-dialect classifier tests (`tests/plantuml/test_url.py`) and the byte-safe
error-scan tests (`tests/plantuml/test_backends.py`). The classifier asserts
on **body signatures** (the placeholder/bad-URL markers, the `<svg` prefix),
never on body sizes — the sizes below are provenance notes, and they drift
between server builds and (for the 400 welcome page) with the submitted
payload (rulebook §5.2 drift note (c)).

| File | Source | Elicitation | Observed |
|---|---|---|---|
| `jetty_real_svg.svg` | `plantuml-server:jetty` @ `http://localhost:8080` (PlantUML 1.2026.8, bare-path protocol) | `GET /svg/{classic(canary.puml)}` — valid diagram | 200, 2095 B, real SVG |
| `jetty_400_placeholder.svg` | same | `GET /svg/{classic(aass_error.puml)}` — syntax error | 400, 8522 B, "Welcome to PlantUML!" placeholder |
| `jetty_200_placeholder.svg` | same | `GET /svg/~1{hex(canary.puml)}` — a legacy-prefixed payload, which 1.2026.8 does not decode (rulebook §5.1): the request-error placeholder | 200, 5377 B, "Welcome to PlantUML!" placeholder |
| `public_real_svg.svg` | `https://www.plantuml.com/plantuml` (public server) | `GET /svg/{classic(canary.puml)}` — valid diagram | 200, 2100 B, real SVG |
| `public_400_placeholder.svg` | same | `GET /svg/{classic(aass_error.puml)}` — syntax error | 400, 8532 B, "Welcome to PlantUML!" placeholder |
| `public_badurl_200.svg` | same | `GET /svg/{bare-deflate-hex(aass_error.puml)}` — a non-classic payload form | 200, 2957 B, "generated a bad URL" explanatory SVG |
| `public_check_ok.png` | same | `GET /check/{classic(canary.puml)}` — the public `/check/` PNG-asset dialect (OK asset) | 69 B, sha256 `9cfe511e6aa8f17c…` |
| `public_check_error.png` | same | `GET /check/{classic(aass_error.puml)}` — the public `/check/` PNG-asset dialect (error asset) | 68 B, sha256 `cf9a9dfe95636420…` |
| `aass_check_stderr.txt` | the CLI jar (`plantuml-cli` container, 1.2026.8) | stderr of `java -jar plantuml.jar --check-syntax --no-error-image -pipe < aass_error.puml` (exit 200) | 55 B, the three-line `ERROR` block (rulebook §4) |
| `canary.puml` / `aass_error.puml` | — | the canary mini-diagram (rulebook §3.5) / the canonical error fixture (rulebook §5.6, from PlantUML's own docs) | text |

**`{classic(…)}`** = the amended canonical encoding (rulebook §5.1): the
PlantUML custom-base64 (alphabet `0-9A-Za-z-_`, digits first) of the
raw-deflate stream of the file's UTF-8 bytes, no prefix — the `SoWkI…` form.

The two PNG `/check/` assets are **documentation fixtures only** — the frozen
protocol does not use `/check/` (rulebook §5.5); their sha256 prefixes
(`9cfe511e…`, `cf9a9dfe…`) match the rulebook's §5.6 record and stayed
byte-stable across the 2026-10-03 → 2026-10-04 server drift (rulebook §5.2
drift note (d)).

**Encoding provenance (important):** the 2026-10-03 design-time record
froze a `~1` hex payload — a documentation error: `~1` is not a real
PlantUML URL-decoder prefix, and no current 1.2026.8 deployment accepts any
prefixed hex form over HTTP (jetty answers the 200 request-error placeholder,
plantuml.com the 200 "generated a bad URL" explanatory). The classic
no-prefix encoding renders on both (the public server decodes raw-deflate
only; the zlib-wrapped variant is answered "bad URL" there), so it is the
amended protocol (user-approved 2026-10-04 — see the feature plan's Progress
entry). The classifier tests exercise the (status, body) pairs as recorded;
the encoding used to elicit a body is orthogonal to the classification.
