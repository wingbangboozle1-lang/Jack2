# Central Los Angeles Jack in the Box (NNN) — sell vs renew decision workbook

A verifiable decision workbook for a single-tenant Jack in the Box restaurant on an NNN lease in
Central Los Angeles, with a lease expiration window of 2030–2035.

**Live site:** https://wingbangboozle1-lang.github.io/Jack2/

> A third, independently built dossier — Monte-Carlo over five strategies, ranked on risk-adjusted
> after-tax wealth — is published from this same Pages deployment at
> **https://wingbangboozle1-lang.github.io/Jack2/docs/** (source in `docs/`, engines in `model/`,
> analysis in `research/00`–`07`). The root site below is unchanged. See `COORDINATION.md` → *Session C*.
>
> A fourth, independently verified dashboard — incorporating Q3 FY2026 SEC Form 10-Q (`JACK`), Fall 2026
> BLS/Treasury releases, post-June 30, 2026 Measure ULA `$5.4M` thresholds, and a 100% browser-local
> IRC §1031 / Prop 13 / Measure ULA simulator — is published at
> **https://wingbangboozle1-lang.github.io/Jack2/session-a3a8ec08/** (source in `session-a3a8ec08/`).
> See `COORDINATION.md` → *Session D*.
>
> A fifth, independently built dashboard — every table row source-linked to an official site, computed
> projections with formulas shown, and a flagged-for-review register — is published from this same Pages
> deployment at **https://wingbangboozle1-lang.github.io/Jack2/session-b4ec6128/** (source in
> `session-b4ec6128/`, working notes in `research/02-demographics.md`–`08-analysis.md`, checker in
> `scripts/verify.py`). The root site below is unchanged. See `COORDINATION.md` → *Session E*.

## What this is

| | |
|---|---|
| Question | Sell the property before the lease expires, or renew and hold? |
| Answer format | A ranked strategy plus six testable decision triggers — not a guess at value |
| Evidence base | 87 metric rows, 76 verified against 23 official sources, 11 deliberately blank and flagged |
| Model | Deterministic 2026–2040 projection in `tools/model.py`, published inputs, breakevens and sensitivity |
| Risk | 24-row register mapped to each decision, including wildfire/earthquake/insurance tail scenarios |
| Privacy | No name, address, APN, loan number or account anywhere in the repo or the site (enforced in code) |

## Read it in this order

1. `index.html` — dashboard
2. `executive-summary.html` — the answer on one page
3. `decision.html` — four scored strategies, the plan, the triggers
4. `market-economics.html` — the verified data
5. `projection-model.html` — how the numbers were produced
6. `risks.html` — what can go wrong, decision by decision
7. `flagged.html` — everything that could **not** be verified, and what to obtain
8. `archive.html` — the parallel session's site, preserved unmodified (a second agent session merged
   its own build to `main` mid-session; nothing was overwritten — see `COORDINATION.md`)

## Reproduce

```bash
python3 tools/model.py        # data/model_output.json + research/model-report.md
python3 tools/build_site.py   # all HTML pages at the repo root
python3 tools/check_site.py   # internal links, source completeness, PII scan, model consistency
python3 tools/export_ledger.py# research/source-ledger.md (manual review copy)
```

Python 3.11, standard library only. No installs, no network needed to build.

## Structure

```
data/           source ledger, metrics, valuation inputs, risks, decisions, requirements, irregularities
session-1944e5a3/  verbatim archive of the parallel session's published site
tools/          model.py, build_site.py, check_site.py, export_ledger.py
research/       model report and the manual-review verification ledger
assets/         style.css, app.js (progressive enhancement only)
*.html          the published site (GitHub Pages serves main / root)
COORDINATION.md shared task board for parallel sessions
```

## Verification rules used

- A value is published **only** if it was read from the official source on the access date (2026-11-06) and that source is linked on the same row.
- If no official value exists, the cell is **blank** and the row is listed on `flagged.html`. Nothing is inferred, interpolated or taken from an aggregator.
- Verified inputs are kept in a different JSON block from analyst assumptions (`data/valuation.json`), and assumptions are labelled on the site.
- The build fails if a row carries a value without a source, if a "verified" row is empty, if an internal link is broken, or if a possible personal identifier appears.

## Scope and limitations

This is internal decision support, not an appraisal, not tax advice and not investment advice. The brief did not include the street
address, APN, current rent, exact expiry date, purchase basis or loan terms, so no parcel-level value, hazard classification or tax
computation is asserted. Those gaps are enumerated as P01–P12 and F01–F11 in `flagged.html`.

## License

No license is included; all rights reserved by the repository owner. A license is recommended before any external reuse of the data tables.


## Session C dossier (`docs/`, `model/`, `research/`)

A separate agent session added a second, independently derived analysis to this repository without
altering anything described above. It is published at `docs/index.html`
(https://wingbangboozle1-lang.github.io/Jack2/docs/) and is self-contained.

| | |
|---|---|
| Question | Hold, renew, or sell — with a lease described as expiring anywhere in a five-year window (2030–2035) |
| Method | 20,000-trial Monte-Carlo over five strategies, including a §1031 exchange, scored on **certainty-equivalent after-tax wealth** (CRRA = 3), not on expected value |
| Conclusion | Do not let the lease run to expiry. Run a dual track: pursue an early 10–15 year extension **and** prepare a §1031 sale. Sell either way — the only variable is whether you sell with 13–15 years of term or with 4–9. |
| Headline numbers | Extension is worth **+25.2%** ($12.48 → $15.62 per $1 of NOI); term decay costs **−22.7%**; the expiry ambiguity alone is worth **~21.6% = $500,000** on a $200k-NOI asset |
| Data | 195 rows, 154 verified against T1 official sources, 25 left blank and flagged, every row carrying a source link |
| Privacy | Owner, tenant, address and APN are placeholders; the Owner's income, net worth, bracket and basis are never collected — the model is normalised to $1.00 of NOI |

Rebuild:

```bash
python3 model/build_facts.py        # 195 rows + integrity assertions
python3 model/projection_model.py   # deterministic; seed 20261106
python3 model/build_site.py         # 11 pages + internal link validation
python3 -m http.server -d docs 8080 # preview
```

The two analyses reach different recommendations because they optimise different things: the root site
ranks strategies on a deterministic projection with explicit decision triggers; `docs/` ranks them on the
tail risk of a stochastic simulation. Neither supersedes the other, and reconciling them is a judgement
call for the Owner.


## Session D dashboard (`session-a3a8ec08/`)

A fourth independent session (`session-a3a8ec08` / `arena/a3a8ec08-jack2`) published a complete 9-page
dashboard and client-side simulator under `session-a3a8ec08/`
(https://wingbangboozle1-lang.github.io/Jack2/session-a3a8ec08/) without altering any prior session's files.

| | |
|---|---|
| Recommended strategy | Two-Stage **Early Blend-and-Extend Inquiry (2026–2027) → Pre-Cliff Sale & IRC §1031 Diversified Exchange (2027–2028)** (`2.03x` expected 10-yr multiple; `$3.09M` mean / `$2.81M` P05 tail floor per `$100k` NOI) |
| Key Fall 2026 official updates | `JACK` Q3 FY2026 Form 10-Q (`2,115` units, `-4.2%` YTD SSS, `$1.47B` debt, `-$901.3M` equity deficit), BLS Oct/Nov 2026 LA employment & CPI (`+3.7%` YoY), Oct 28, 2026 10-Yr Treasury (`5.05%`), post-June 30, 2026 City of LA Measure ULA `$5.4M` (`4.45%`) cliff, CAL FIRE Jan 2025 Eaton & Palisades finals (`16,264` structures destroyed) |
| Interactive private simulator | 100% browser-local calculator (`session-a3a8ec08/projections-decisions.html`) for exact NNN rent, expiry year (`2030–2035`), Prop 13 reassessment shock, Measure ULA cliff, and §1031 tax deferral |
| Verification & privacy | 142 table rows across 9 pages verified against official primary sources; 11 unverified private lease/parcel items left strictly blank; automated zero-PII enforcement (`[REDACTED-OWNER-01]`, `[REDACTED-PROPERTY-01]`) |

Rebuild & verify:

```bash
python3 session-a3a8ec08/scripts/projection_engine.py
python3 session-a3a8ec08/scripts/build_site.py
python3 session-a3a8ec08/scripts/verify_all.py
```

## Session F workbook (`session-643e4aab/`)

A fifth independent session (`643e4aab` / `arena/643e4aab-jack2`) published a 12-page, source-verified
decision workbook at https://wingbangboozle1-lang.github.io/Jack2/session-643e4aab/ without altering any
prior session's files.

| | |
|---|---|
| Recommendation | Do not drift to expiry. Open a renewal priced at a market reset **and** run a §1031 sale in parallel; sell if the achievable price implies a cap rate at or below the **7.18%** breakeven, otherwise keep the asset and take the reset |
| Model result | HOLD_TO_EXPIRY $4,484,252 > SELL_1031_NOW $4,212,704 > EXTEND_THEN_SELL $3,893,300 > SELL_TAXABLE_NOW $3,525,077 per $100k NOI, nominal 2040; holding wins 67.2% of 10,000 draws (seed 20261107) |
| Why sell anyway | Concentration (one tenant, one parcel, one metro) and tail risk that cannot be diversified inside one building — 60% chance of an M6.7+ quake in the LA region within 30 years |
| Data | 129 rows: 97 verified, 4 computed, 3 given, **25 left blank and flagged**, every sourced row carrying a tiered source link from 29 sources |
| Hazards | Dedicated earthquake / wildfire / insurance-market page, including the $1bn FAIR Plan assessment and the 16,251 structures lost in January 2025 |
| Privacy | Address, APN and owner withheld (`[REDACTED-PROPERTY-01]`, `[REDACTED-OWNER-01]`); the verifier scans every generated page for email, phone, SSN, parcel and street-address patterns and fails the build on a match |

Rebuild & verify (CI runs the same three commands and fails on stale output):

```bash
python3 session-643e4aab/model/projection.py    # 10,000-trial Monte Carlo, seed 20261107
python3 session-643e4aab/scripts/build_site.py  # 12 pages + assets/style.css
python3 session-643e4aab/scripts/verify.py      # rows, sources, blanks, links, PII, model consistency
```
