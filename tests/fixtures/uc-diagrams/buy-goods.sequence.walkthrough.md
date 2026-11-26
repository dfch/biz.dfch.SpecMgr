# Buy Goods sequence diagram — Phase 140 walkthrough record

feat-185-uc-diagrams, Task 140.120 (ACC-002 evidence). The record of running
the `generate_uc_sequence_diagram` prompt flow (rulebook §3.8) against the
packaged "Buy Goods" example UC. Companion artifact:
`buy-goods.sequence.walkthrough.puml` — the final agent-owned diagram, pure
(no commentary lines; the commentary lives here).

## Execution method

- Executed by invoking **this worktree's own code directly** (a
  `uv run --frozen python` driver): the `uc.tools` functions `create_uc`,
  `get_uc`, and `get_uc_sequence_skeleton` called as plain Python (the MCP
  tool wrappers are thin and return the originals), `plantuml.chain.
  validate_plantuml` for the validation loop, and a plain file write for the
  host-native `.puml` write. The session's specmgr MCP server points at a
  **different checkout**, so the MCP server layer is deliberately out of
  scope for this run; everything below exercises the same functions the MCP
  tools wrap.
- Isolated `SPECMGR_DOCS_DIR` (a fresh `/tmp` dir — the UC document and its
  `diagrams/` live only there, never in this repo's `docs/` or the repo
  tree).
- Validation source: `SPECMGR_PLANTUML_URL=http://localhost:8080` — the
  gitignored repo-root `.env`, loaded `override=False` exactly as
  `tests/conftest.py` does — the self-hosted PlantUML 1.2026.8 jetty; the
  chain's selected source was `('url', 'http://localhost:8080')`.
- Date: 2026-10-05.

## Setup (flow steps 1–5)

- Step 1 (read the rulebook): the driver's attribution decisions below cite
  the rulebook's own sections (§2.9.3, §2.9.5, §2.11, §3.8); the rulebook is
  the frozen spec (`specmgr://uc/plantuml`).
- The UC document was created from the packaged example's **body**
  (`uc/data/uc_example.md`, frontmatter stripped) via `create_uc` → id
  `04e49ada-9157-4c6b-b714-774ba4a3061b` (fresh uuid4, `status=draft`,
  `version=1.0.0`).
- `get_uc(04e49ada-…)` parses cleanly: title `Buy Goods`, level `Summary`
  (no `ParseFailureResult` — the flow's step-3 stop condition did not fire).
- **Subfunction judgment (flow step 4, rulebook §2.11):** the level is
  `Summary`, not `Subfunction` → the judgment is trivially "proceed"; no
  question required.
- Skeleton (flow step 5): `get_uc_sequence_skeleton(04e49ada-…)` returned
  text **byte-identical** to the committed golden
  `buy-goods.sequence.golden`, carrying exactly 5 `UNATTRIBUTED` markers
  (lines 15, 74, 80, 101, 105 of the skeleton):

| Line | Marker |
|---|---|
| 15 | `' UNATTRIBUTED trigger: Purchase request comes in (via phone, fax, web form, or electronic interchange)` |
| 74 | `' UNATTRIBUTED ext 7a step 2: If backup service also unavailable, company informs buyer of delay.` |
| 80 | `' UNATTRIBUTED ext 8a step 2: If all channels fail, company logs issue for manual follow-up.` |
| 101 | `' UNATTRIBUTED ext 10b step 3: Dispute is resolved (refund, credit, or confirmation of charge).` |
| 105 | `' UNATTRIBUTED ext 10c step 2: If retry fails, company contacts buyer to resolve payment issue.` |

## Attribution (flow step 6)

Five markers, five attributions. **One deliberate question** (ACC-002); the
other four are pinned by the free text itself.

| Marker | Arrow adopted | Basis |
|---|---|---|
| trigger | `Buyer -> Company: Purchase request comes in (via phone, fax, web form, or electronic interchange)` | The Goal in Context names the Buyer as the one who *issues* the request; the trigger's receiver is fixed to the system (§2.9.5). |
| ext 7a step 2 | `Company -> Buyer: If backup service also unavailable, company informs buyer of delay.` | The sentence names both actors. |
| ext 8a step 2 | `Company -> Company: If all channels fail, company logs issue for manual follow-up.` | Internal Company logging; no other actor is involved → self-message. |
| ext 10b step 3 | `p2 -> Company: Dispute is resolved (refund, credit, or confirmation of charge).` | **Genuinely ambiguous — asked via the `question` tool contract; see the transcript below.** |
| ext 10c step 2 | `Company -> Buyer: If retry fails, company contacts buyer to resolve payment issue.` | The sentence names both actors. |

### Question transcript (the `question` tool contract, flow step 6)

> **Q (extension 10b "Buyer disputes charge", step 3):** The step reads
> "Dispute is resolved (refund, credit, or confirmation of charge)." Its text
> names no actor, and no participant is excluded by the wording. Who sends
> this message — the Company, the Buyer, the Credit card company (p2), or the
> Bank?
>
> **A (adopted):** the **Credit card company (p2)** — i.e.
> `p2 -> Company: Dispute is resolved (refund, credit, or confirmation of
> charge).`
>
> **Reasoning:** in this UC's world a charge dispute is a payment-network
> matter — its resolution (refund, credit, or confirmation of the charge) is
> driven by the payment processor, not by the Company or the Buyer. The UC's
> own Secondary Actors list names the credit card company "(for payment
> processing)" and its Assumptions state "Payment processing is handled by
> external services (credit card company, bank)"; of those, the credit card
> company is the named processor of the disputed *card* charge (the Bank
> handles transfers, not card disputes). The step is delivered **to** the
> Company, which had initiated the dispute resolution process (ext 10b step
> 1) and provided documentation (step 2) — the processor's resolution lands
> on the system. This is the attribution the packaged example
> (`uc/data/uc_plantuml_example.md`) records for the same marker — the
> walkthrough agrees with the model.

### Corrected pre-filled arrows

**None.** Every pre-filled arrow was reviewed against the free text. The one
worth calling out: step 2's positionally pre-filled receiver
(`Company -> Buyer: Company captures buyer's name, address, …`) is the
outcome the rulebook §2.9.3 worked example freezes verbatim ("the rule is
positional, not semantic"), and the free text (the Company capturing the
Buyer's own details) shows no reason to correct it.

## Zero-marker check (flow step 7)

The attributed diagram carries **zero** `UNATTRIBUTED` markers — driver
assertion `"UNATTRIBUTED" not in final_text` passed.

## Validation loop (flow step 8, rulebook §3.8)

Selected source: the URL jetty (`SPECMGR_PLANTUML_URL`, first-set wins —
`SPECMGR_PLANTUML_JAR`/`_BIN` unset).

1. **Skeleton** (pre-write): `structure_ok=true`, `valid=true`,
   `rendered=true`, `checked_by="url"`, `source_state="ok"`,
   `available=true` — with the 5 expected UNATTRIBUTED-marker **warnings**
   (markers are `'` comments the real parser accepts, §6.5; the zero-marker
   rule is the agent flow's, not the checker's).
2. **Attributed final diagram** — the full result model, quoted:

```
{
  "structure_ok": true,
  "valid": true,
  "rendered": true,
  "checked_by": "url",
  "errors": [],
  "warnings": [],
  "source_state": "ok",
  "available": true,
  "reason": null,
  "fix_hint": null
}
```

Green at the highest available layer (the parser) **and** zero markers ⇒ the
write precondition held. A validation source was configured, so the
structure-only state (and its `' validated: structure-only` header, rulebook
§3.4) did not apply — the written file carries no header.

## Host-native write (flow step 9)

- Path (isolated project):
  `/tmp/opencode/uc-walkthrough-_hpzi7mg/diagrams/uc/04e49ada-9157-4c6b-b714-
  774ba4a3061b.sequence.puml` — a plain file write; **no specmgr tool writes
  `.puml`**.
- sha256 of the written text:
  `88979f439d6c116643d921de78ff9e553cb48992f5288e7f7ea9bf69b44fbe4a`.
- Committed record artifact:
  `tests/fixtures/uc-diagrams/buy-goods.sequence.walkthrough.puml`
  (byte-identical copy — sha256 verified after the copy; this is the
  ACC-001 pinning test's source of truth).

## Cross-checks

- Final text == the packaged example (`uc/data/uc_plantuml_example.md`) with
  its `'` reasoning comments stripped — driver assertion passed (the
  walkthrough's attributions match the packaged model on all five markers).
- The committed walkthrough `.puml` contains no `'` lines at all (pure
  diagram; the structure checker therefore reports zero warnings on it).

## Step 10 report (per the flow)

- Written path: `/tmp/opencode/uc-walkthrough-_hpzi7mg/diagrams/uc/
  04e49ada-9157-4c6b-b714-774ba4a3061b.sequence.puml`
- Validation outcome: `checked_by=url`, `valid=true`, `rendered=true`,
  `source_state=ok`
- Questions asked: **1** (ext 10b step 3) — answer adopted: `p2 -> Company`
- Pre-filled arrows corrected: **0**
- Nothing committed by the flow (commit policy belongs to the user /
  orchestrator).

## 2026-10-06 correction + re-verification (Phase 145 — post-implementation review)

**The `rendered=true` verdicts quoted above were a misread — they are
superseded by this section. The original record (dated 2026-10-05) is kept
as written; this correction does not rewrite it.**

**What was misread.** The jetty `GET {base}/svg/{enc}` answer for this
diagram was **200 + a PlantUML crash page**, not a real render: the body
says "PlantUML (1.2026.8) has crashed." and embeds the
`java.lang.ClassCastException` trace (`TileBuilder.buildOne`). The
pre-amendment URL classifier accepted that crash page as a real-diagram SVG
(`is_real_svg`), so the chain reported `valid=true` / `rendered=true`. The
trigger is a known PlantUML 1.2026.8 crash bug: a **bare** `note left`/
`note right` block following a self-message's note tile (attached or
detached) with no intervening non-self message. This diagram ends with the
self-message step 11 (`Company -> Company: Company receives payment and
records it.`) followed by two consecutive bare `note left` final blocks —
exactly the crashing shape. The same shape crashes the jar source (exit 200
+ the `ClassCastException` trace on stderr, no parseable `ERROR` block).
All three committed sequence artifacts (the golden, the packaged example,
this walkthrough file) were affected identically.

**What the re-verification shows (2026-10-06, both independent sources —
dev jetty 1.2026.8 + the same-build `plantuml-cli` jar
1.2026.8/149874a).**

1. **Old shape crashes (both sources):** the pre-correction file (sha256
   `88979f439d6c116643d921de78ff9e553cb48992f5288e7f7ea9bf69b44fbe4a` — the
   sha cited in the Host-native write section above) returns jetty 200 + the
   crash-page SVG (13054 B, "has crashed" + the `ClassCastException` trace)
   and jar `--check-syntax` exit 200 + the `ClassCastException` trace on
   stderr (no parseable `ERROR` block). A minimal repro (the recorded
   `tests/fixtures/plantuml/crash_shape.puml`) crashes identically on both.
2. **New shape renders truly (both sources):** the corrected file below
   validates green at both sources, and the render-proof SVG **body**
   carries the diagram text (e.g. the final note line "Buyer has goods")
   with **no** crash marker — jetty: 200 + a 36 KB real SVG; jar:
   `--check-syntax` exit 0 and `--svg` exit 0 with the text in the body.
   The anchored form (`note left of {participant}`) is verified OK
   everywhere the bare form crashed (two consecutive anchored notes after a
   self-message, anchored notes after an attached note), with the note text
   present in the rendered SVG.
3. **The classifier gap is closed** (rulebook §5.2 crash line): a 200 +
   crash page is now a recognised INVALID row (`valid=false`, line-0
   finding carrying the crash exception class, fix hint pointing at the
   §2.9 anchored notes), and `is_real_svg` rejects the crash page — so this
   class of misread (crash page accepted as a render) is impossible again.

**The corrected artifact.** The committed
`buy-goods.sequence.walkthrough.puml` was re-recorded on 2026-10-06 per the
user-approved ruling (A: unanchored notes become `note left of
{primary-actor-alias}` — here `Buyer`, the primary actor's §2.9.1
declaration alias): its three unanchored note headers (lines 9, 112, 118)
changed from `note left` to `note left of Buyer`; **every attribution,
message, and comment-stripped line is otherwise byte-identical** — the
ACC-001 pinning still holds (the corrected file == the re-recorded skeleton
with the same frozen marker→arrow table). New sha256 of the corrected
`.puml`: `82dae3926ffd1daa99bb889e5c5d01ab6983211095be8bdee311dbdc5ae43737`
(the old sha above stays with the original pre-correction text). The
packaged example (`uc/data/uc_plantuml_example.md`) and the sequence golden
(`tests/fixtures/uc-diagrams/buy-goods.sequence.golden`) were re-recorded
with the identical three-header change; their render proofs are pinned by
the env-gated live tests (`tests/uc/tools/test_validate_plantuml.py`,
Phase 145: SVG body text present, no crash marker).
