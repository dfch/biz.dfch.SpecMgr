# Findings: API investigation of `tekom.termtechnologies.com` (TermXplorer)

**Date:** 2026-08-26
**Method:** read-only black-box investigation — raw HTTP (curl) against the
live server, vendor-site review, analysis of the application's own JS/CSS,
authenticated probes with the public `tekom_EN` demo credentials
(username and password are identical; the public tekom.de page lists the
sister pair `tekom`/`tekom` — see Section 2.1). No write operations were
performed.
**Purpose:** input for a later MCP-server implementation plan that queries
the TermXplorer database (this folder, `feat-0-termxplorer-mcp`).
**Status: findings only — no implementation plan exists yet.**

______________________________________________________________________

## 1. System identification

| Item | Value |
|---|---|
| Product | **TermXplorer** web client (TermSolutions GmbH), part of the "TermTechnologies" suite |
| Version | Core **25.5**, App **25.5** (shown in the page footer) |
| Content owner | **tekom** (Gesellschaft für Technische Kommunikation e.V.) — footer: "Content by tekom" |
| Maintainers of the content | tekom working group **AG TTK** ("Terminologie der Technischen Kommunikation") |
| Stack behind nginx | PHP **8.3.8** (`x-powered-by`), nginx 1.14.2, Smarty templating, Prototype.js + jQuery front end |
| HTTP security | HSTS enabled, `no-store` on auth responses, `referrer-policy: strict-origin`, cookies required |

The front end is an AJAX shell: `index.php` loads a frame, and all content
arrives as **HTML fragments** from `index.php?pack=<Pack>&t=<Type>` (static
assets via `_.php?com/…` / `_.php?front/…`). A plain HTTP client with a
session cookie can drive the whole app — no browser needed (every probe in
this document was raw `curl`).

### Content model available to this account

- **Dictionaries:** `17 tekom-TTK` (the core AG TTK glossary), `24 Proposal`
  (Neuvorschläge), `25 Modification` (Änderungswünsche), `26 iiRDS`
- **Languages:** `1 German (de)`, `2 English (EN)`, `5 Italian (IT)`,
  `4 Notation (nota)` — the source-language option values carry the format
  `langId|rtl|code` (e.g. `1|0|de`)
- **Structure:** Dictionary → **Concept** (id, e.g. `#5006`) → **language
  level** (one per language, id, e.g. `#6839`) → **Terms** (per-language
  designations, id, e.g. `#6363`). Concepts carry the definition; terms
  carry the usage/status information.
- Per-dictionary field/permission flags are embedded in the main page
  (`self.dicts_rules` — dict 17 all `0`, dicts 24/25 several `1`): which
  fields exist/are editable differs per dictionary.

## 2. Official API situation

### 2.1 Public access & sources

- Public landing page: <https://www.tekom.de/services-unsere-angebote/terminologie>
  — describes the freely accessible online terminology database and links
  "Hier geht es zur Suche" to <https://tekom.termtechnologies.com/>.
- Public quick guide (PDF, Stand 2023-06-15):
  <https://www.tekom.de/fileadmin/tekom.de/Technische_Kommunikation/Terminologie/tekom_2023-06-15_Terminologie-TK-Kurzanleitung_de.pdf>
- Public demo credentials listed on both: **Login `tekom` / Passwort
  `tekom`**. The `tekom_EN` account used for this investigation follows the
  same public, username=password pattern (presumably the English-GUI
  variant).

### 2.2 No public API on this host

- Probed (all nginx 404): `/rest`, `/rest/`, `/api`, `/api/v1`,
  `/webservice`, `/ws`, `/txapi*` (including `/txapi/`, `/txapi/docs`,
  `/txapi/openapi.json`), `/swagger`, `/openapi.json`, `/doc`, `/docs`,
  `/help`, `/manual`.
- The vendor's suite **does include official API / term-check products**:
  **tXapi** ("distributes the agreed glossary as glossaries into all
  enterprise systems") and **termXact** (professional term
  check/correction programs), plus OntoTerm (ontologies/taxonomies).
  **There is no evidence tXapi is installed or exposed on this host**, and
  no vendor documentation for these products is publicly available
  (termxact.com carries only marketing pages). Documentation appears to be
  customer/partner-only.
- In-app **Help** is an empty placeholder (`index.php?pack=Help` → "the
  help block will here").
- Vendor contact listed on the project site: **LangOps Intelligence,
  Dr. Rachel Herwartz, contact@langops-intelligence.com** — the party to
  ask about enabling tXapi or granting export rights.

**Conclusion:** any integration today must use the app's internal RPC
endpoints (Section 4), or first negotiate tXapi access with the operator.

## 3. Official data model & semantics (from the public Kurzanleitung)

The public quick guide documents the normative model; it corroborates the
technical findings in Section 4:

- **Normative designations:** in each language, per concept, there is
  exactly **one preferred designation** (Vorzugsbenennung). Designations
  that may also be used get the attribute **"erlaubt"** (observed in the
  data as `admitted`); designations that must not be used get
  **"abgelehnt"** (observed as `do_not_use`). This explains the observed
  status-pill values `preferred` / `admitted` / `do_not_use`.
- **Process status** (per language level; the "Process status" field):
  lifecycle `vorgeschlagen` (proposed) → `in Bearbeitung` (in progress) →
  `zur Abstimmung` (under review) → `Expertenfreigabe` (expert approval).
  Only entries with *Expertenfreigabe* are declared binding for tekom work
  (EN value observed in the data: "expert approval").
- **Concept granularity:** synonyms live in one concept; homonyms
  (polysemes) are kept in separate concepts. Every entry has at least a
  German designation and a German definition.
- **Default search scope:** the three dictionaries *tekom-TTK*,
  *Neuvorschläge* (Proposal, 24) and *Änderungswünsche* (Modification, 25)
  — matching the pre-selected dictionaries observed in the app.
- **The three official quick filters:** Fachgebiet (domain),
  Prozessstatus (process status of the source language), Benennungstyp
  (designation type — for finding abbreviations or proper nouns) — matching
  the dynamic `field_entry[…]` quick-filter form found in the app.
- **Notation as hierarchy:** the "Notation" language (id 4) encodes
  hypernym/hyponym (Oberbegriff/Unterbegriff) relations. With
  dict = tekom-TTK, source language = Notation, target languages = e.g.
  German, a search for `*` returns every concept that has been classified;
  the concept system can also be displayed graphically (the app JS exposes
  a GraphML endpoint — see 4.6; observed, not tested).

## 4. The internal RPC interface (verified live)

All endpoints below verified with `GET`/`POST` + session cookie. Responses
are **HTML fragments** (not JSON), UTF-8.

### 4.1 Authentication & session

| Step | Request | Result |
|---|---|---|
| Obtain session | `GET /` (any page) | sets `PHPSESSID` cookie |
| Login | `POST /admin.php?pack=LoginArea&a=login` with url-encoded `login`, `password`, `suc_ret=index.php`, `ret=/admin.php?pack=LoginArea&suc_ret=index.php` | `302` → `Location: index.php` on success (verified with the `tekom_EN` credentials) |
| Keep-alive | `GET /sessionKeepAlive.php` | `200`, empty body (verified) |
| Logout | `GET /index.php?pack=LoginArea&a=logout&ret=<url>` | session destroyed |
| GUI language | `GET /index.php?pack=Profile&a=setGUILang&code=<en_US\|de_DE\|…>` | 11 GUI languages available |

Session lifetime per the app's own JS: **8 h**
(`sessionLifetime = 28800 * 1000`); the UI prompts 60 s before expiry. A
non-browser client never sees the prompt, so a long-running server should
either re-login or call `sessionKeepAlive.php` periodically.

Verified request example (search, from the shell):

```bash
curl -sS -c cookies.txt "https://tekom.termtechnologies.com/" \
  && curl -sS -b cookies.txt -c cookies.txt -X POST \
     "https://tekom.termtechnologies.com/admin.php?pack=LoginArea&a=login" \
     --data-urlencode "login=<user>" --data-urlencode "password=<pass>" \
     --data-urlencode "suc_ret=index.php" \
     --data-urlencode "ret=/admin.php?pack=LoginArea&suc_ret=index.php"
# then:
curl -sS -b cookies.txt -G "https://tekom.termtechnologies.com/index.php" \
  --data-urlencode "pack=Search" --data-urlencode "t=result" \
  --data-urlencode "q=Funktionsprüfung" \
  --data-urlencode "dictsId=17" --data-urlencode "srcLangId=1" \
  --data-urlencode "tgtLangs=2|5|4" --data-urlencode "itemsOnPage=5" \
  --data-urlencode "searchMode=like" --data-urlencode "comments=0"
```

### 4.2 Term/concept search (the core validation endpoint)

```
GET /index.php?pack=Search&t=result
    &q=<URL-encoded query>
    &dictsId=<dict ids, "|"-joined, e.g. 17|24|25|26>
    &srcLangId=<language id, e.g. 1>
    &tgtLangs=<language ids, "|"-joined, e.g. 2|5|4>
    &itemsOnPage=<n>
    &searchMode=like|fulltext
    &comments=0|1
    &searchType=term|comment        (optional; comment search)
    &langExistanceFilter=always|if_tgt_exists|if_tgt_missing
    &p=<page number>                (optional, pagination)
    &field_entry[<propId>]=<value>  (optional, advanced filters, see 4.6)
```

Notes:

- `q` accepts plain terms (case-insensitive; `like` mode = substring
  match) and **`#<conceptId>` for direct concept lookup**
  (`q=%235006`). `q=*` returns everything (the app's own "show all"
  idiom, officially documented in the Kurzanleitung).
- Umlauts/UTF-8 work when properly percent-encoded (verified:
  `q=Funktionsprüfung` → 1 concept).
- `langExistanceFilter` values come from the `display-data-records`
  setting (`always`, `if_tgt_exists`, `if_tgt_missing`).
- Parameter-name quirk: the result endpoint takes `dictsId`, the
  autocomplete endpoint takes `dictIds` (both verified).

**Response structure (verified):**

```html
<div id="search-summary">Concepts found: <b>3</b></div>
<input type="hidden" id="found-items-qnt" value="3" />
<div class="found-items-list" id="found-items-list-page-1">
  <div class="item" id="concept-5006" class="lite">
    <div class="concept-id">#5006</div>
    <div class="term-result-right">
      <div class="concept-def">
        <div class="lang-name">German</div>
        <div class="term">
          <div class="pill preferred">preferred</div>          <!-- term STATUS -->
          <div class="term-container">
            <span class="term-id">#6363</span>
            <span class="term-title">Funktionsprüfung </span>
          </div>
        </div>
        <!-- …one <div class="term"> per designation… -->
      </div>
      <div class="tgt-lang-item">                                <!-- per target language -->
        <div class="lang-name">English</div>
        <div class="terms-list">
          <div class="term"><div class="pill do_not_use">do not use</div>
            <span class="term-id">#6381</span><span class="term-title">function test </span></div>
          <!-- … -->
        </div>
      </div>
    </div>
  </div>
  <!-- …more items… -->
</div>
<div class="pager">…<span id="page-num">1</span>…</div>
```

Status is a `<div class="pill <status>"><status text></div>` per term.
**Observed status values: `preferred`, `admitted`, `do_not_use`** (per the
normative model in Section 3, each concept/language has at most one
`preferred`). The pill is rendered server-side; the JS/CSS contain no
enumeration, so a parser should treat the status as open-ended (pass
through anything unrecognized).

### 4.3 Autocompletion

```
GET /index.php?pack=Search&t=autocompletion
    &searchFor=term|comment
    &dictIds=<dict ids, "|"-joined>
    &srcLangId=<lang id>
    &term=<min 2 chars, prefix-ish match>
```

Response: `<ul><li>term</li>…</ul>` (empty `<ul>` when no match). Verified:
`term=Pr` → 15 candidates; `term=Test` (no dict filter) → `test`,
`testing`. Useful as a cheap existence/spell-check signal; the full search
(4.2) is the richer validation call.

### 4.4 Concept detail (three-level drill-down)

```
GET /index.php?pack=Search&t=detailedView&conceptId=<id>
GET /index.php?pack=Search&t=loadLangLevelBody&langLevelId=<id>
GET /index.php?pack=Search&t=termLevelBody&termId=<id>
```

- `detailedView` returns a shell: hidden `dict-id` / `concept-id`, one
  `<div id="lang-level-<id>" data-level-id="…">` per language with
  `<span class="data-lang-id" id="data-lang-id-<langId>" data-lang-code="de|EN|…">`.
- `loadLangLevelBody` (per language level) returns the **language-level
  fields** as
  `<div class="field-def"><div class="desc"><Label>:</div><div class="info <value-key>"><text></div></div>` blocks plus a `terms-list`
  of term heads (`id="term-<id>"`, `data-term-id`, term name). **Observed
  labels:** `Process status` (values per Section 3), `Definition`,
  `Definition source`.
- `termLevelBody` (per term) returns the **term fields** in the same
  `field-def` markup. **Observed labels:** `Usage` (e.g. "preferred" — the
  status), `Part of speech`, `Gender`, `Number`, `Context` (example
  sentence), `Context source`, `Link source Context` (contains **raw
  HTML** with an external `<a href>`).
- Field labels/values differ per dictionary/language (the field schema is
  data-dependent) — a parser should key on the `desc` labels, not assume a
  fixed set. Note the `info` element's class carries a "key" version of
  the value (lowercased word tokens, e.g. `expertapproval`, `do_not_use`-
  style) alongside the display text.

### 4.5 Export / Import

- `GET /index.php?pack=ImportExport&t=export_form&<search params from 4.2>` → **denied for `tekom_EN`**:
  `<div style="color:red">You do not have the authorization to view the page.</div>`
- `GET /index.php?pack=ImportExport&t=import_form` exists (import is a
  file-upload form).
- Export would be the clean bulk route (glossary download, e.g. TMX/CSV —
  formats not confirmable without the right). **Bulk validation for this
  account therefore means iterating the search endpoint** (per-term, or
  `q=*` pagination sweeps with a sane `itemsOnPage`).

### 4.6 Advanced filters, dashboard, graph display

- `GET /index.php?pack=Search&t=quickFilter&dictsId=<ids>` returns a
  dynamic filter form; filters are submitted as `field_entry[<propertyId>]=<value>`
  params on the search URL (observed property ids 62, 64, 88, 89, 97 — a
  mix of `<select>` enumerations and free-text inputs). Property ids are
  data-dependent (per dictionary schema) — not stable to hardcode. The
  three official filters (Fachgebiet, Prozessstatus, Benennungstyp) are
  expected to be among them.
- `GET /index.php?pack=Search&t=dashboard&dictsId=<ids>` returns a ~85 KB
  statistics block (per-dictionary/concept counts).
- `GET /index.php?pack=Search&t=graphml` (observed in the app JS, gated by
  a hidden button — for the concept-system graph display, Section 3;
  **not tested**).

### 4.7 Editor & admin packs (for completeness)

- `index.php?pack=Editor&…` (concept/term CRUD: `conceptCreate`,
  `saveTerm`, `saveLangLevel`, `saveProposal`, `deleteConcept`, …) — the
  **editor UI shell loads (200) for `tekom_EN`**; no write operations were
  tested (read-only investigation).
- `admin.php?pack=Admin` → **Access denied** for `tekom_EN` (separate
  error page).

### 4.8 Error shapes (for client robustness)

- Unauthorized fragment: red div "You do not have the authorization to view
  the page."
- Admin denial: full HTML error page "Error! Access denied."
- Unknown path: bare nginx 404 (HTML).
- Login failure: not observed (only the successful login was tested).
- Session expiry: the app redirects to the login frame; a client should
  detect it by re-fetching a known page and checking for the login form /
  absence of the expected fragments.

## 5. Account permission profile (`tekom_EN`)

| Capability | Status |
|---|---|
| Search (all 4 dicts, all langs) | verified |
| Autocompletion | verified |
| Concept/language/term detail drill-down | verified |
| Editor UI (read the shell) | 200 (writes untested) |
| Bulk export | denied |
| Admin | denied |

## 6. Sample data (tekom-TTK, concept #5006 "Funktionsprüfung")

- **German terms:** `Funktionsprüfung` (preferred), `Funktionskontrolle`
  (do not use), `Funktionstest` (admitted), `Funktionscheck` (do not use)
- **English terms:** `functional test` (preferred), `function test` (do not
  use), `functionality test` (admitted), `functioning test` /
  `functional check` (do not use)
- **Definition (DE):** "Tätigkeit zur Bestätigung, dass das zu prüfende
  Objekt imstande ist, die spezifizierte Aufgabe zu erfüllen"
- **Definition source:** "AG TTK DE NH 05.10.2021"
- **Process status:** expert approval
- **Term #6363 (DE) fields:** Usage preferred, Part of speech noun, Gender
  feminine, Number singular, Context "Fristen sind für die erstmalige
  Funktionsprüfung bereits bestehender privater Abwasserleitungen festgelegt
  worden.", Context source "Stadtentwässerungsbetriebe Köln (2021):
  Wissenswertes zur Funktionsprüfung [Zugriff: 16.07.2021, 11:05 MESZ]",
  Link source Context (external URL, Stadtentwässerungsbetriebe Köln)

## 7. Risks & limitations for any future integration

1. **Undocumented, internal interface** — HTML fragments, no versioning
   contract; a server upgrade can break parsing at any time. Mitigations:
   tolerant HTML parsing (lxml/BeautifulSoup), keying on stable attributes
   (`id="concept-*"`, `class="pill"`, `field-def`/`desc`), and a
   health-check query (e.g. `q=*`, expect 200 + the summary div).
2. **Session-based auth only** — no API tokens, no Basic-auth endpoint; the
   client must manage `PHPSESSID`, re-login on expiry, and optionally ping
   `sessionKeepAlive.php`.
3. **No bulk export for this account** — volume queries must be paged
   searches; be conservative with `itemsOnPage` and request rates (no
   rate-limit documentation; the server is a small nginx/PHP box).
4. **Open data vocabularies** — the set of term `Usage` statuses and the
   set of `field-def` labels are data-dependent; Section 3 covers the
   official values for the core dictionary, but parsers must not assume
   closed sets.
5. **Credentials** — the `tekom_EN` pair is public demo access (tekom.de);
   it is a shared account. A real deployment should ask tekom/LangOps for
   dedicated service credentials and store them via secret management, not
   hard-code them.
6. **Strategic alternative** — asking the operator (LangOps Intelligence /
   tekom) for **tXapi** access or **export rights** would yield a
   sanctioned, stable interface; the internal RPC work is the fallback /
   interim route.
7. **Shared public account etiquette** — because the demo credentials are
   public, an MCP server using them should identify itself sensibly (user
   agent), cache where reasonable, and stay well below load the AG TTK
   would notice.

## 8. Open questions for the later MCP plan

- Should the MCP server wrap the internal RPC only, or also attempt tXapi
  if/when provisioned (backend-swappable interface design)?
- Scope: search + status validation only, or also concept detail
  (definition / context / part of speech), the Notation hierarchy, and
  bulk glossary sweeps?
- Which dictionaries/languages as defaults (tekom-TTK de/en/it is the
  apparent core asset; Proposal/Modification by default, as in the app)?
- Credential handling: env var / config file / per-user; dedicated service
  account vs. the public demo pair?
- Parsing tolerance policy & health check; session management (keep-alive
  interval vs. re-login); request-rate budget.
- Read-only guarantee: enforce at the client layer (never call
  `pack=Editor&a=*` write actions, never `ImportExport&t=import`).
- Status vocabulary in tool results: pass through raw server strings
  (`preferred` / `admitted` / `do_not_use`), map to a fixed enum, or both?

## 9. Investigation artifacts (local, disposable)

Working files from this investigation were kept under `/tmp/opencode/`
(cookie jar, fetched HTML/JS/CSS, the Kurzanleitung PDF text). They are
session-bound and intentionally not committed; re-derivable via the
endpoints above.
