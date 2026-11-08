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


## Session G dashboard (`session-e618ace7/`) — final integration

A sixth, independent session (`session-e618ace7` / `arena/e618ace7-jack2`) performed a line-by-line review of
everything above and published a **source-linked decision dashboard** at
**https://wingbangboozle1-lang.github.io/Jack2/session-e618ace7/**. It is the recommended entry point: the root navigation now carries an **All workspaces** link to a new
`workspaces.html` index (a single additive change in `tools/build_site.py`), so all seven builds in this
repository are reachable from the landing page.

| | |
|---|---|
| Question answered | Sell the NNN lease before 2030–2035, or renew? |
| Recommendation | **Do not hold to expiry.** Two leading paths within 0.5% of each other on risk-adjusted wealth: (1) extend ~10 years at or above in-place rent in 2027, then sell 2029–2032 with ~12 years of term through a §1031 exchange; (2) sell now through a §1031 exchange. Passive hold is last on the floor and the risk-adjusted measure. |
| Evidence | 110 fact rows, **96 verified** against **19 official sources** read on 2026-11-07, **14 deliberately blank** and flagged. Nothing inferred. |
| Model | Six strategies, deterministic + 10,000-trial seeded Monte Carlo (seed 20261107), CRRA-2 certainty equivalent, 15-cell sensitivity grid, all 20 assumptions published with the range tested |
| Risk | 30-row register mapped to every strategy, including 6 black swans |
| Review | 10 irregularities found in the existing repository (1 URL defect, 1 incomplete tax row, 1 one-sided tenant framing, 3 fillable blanks, plus cleared items) — published with evidence on the site's Flagged for review page |
| Privacy | No address, APN, rent, basis, loan or owner identity anywhere; enforced by a build-failing PII scan |

Rebuild and verify:

```bash
python3 session-e618ace7/scripts/model.py            # deterministic + seeded Monte Carlo
python3 session-e618ace7/scripts/build_site.py       # 14 pages
python3 session-e618ace7/scripts/verify_dataset.py   # 12 rule checks, exits non-zero on failure
```

Two findings worth knowing before reading anything else in this repository:

- The root build's Census source URL (`data/sources.json` S2) is malformed — it silently drops the Los Angeles
  County column. The values it is cited for are correct; the link is not. Corrected URL published as S01 in the
  Session G ledger (flagged R-01).
- Sessions D and E both lead on the tenant's FY2025 net loss without noting that the same SEC dataset shows
  **net income of +$27.9m for the first nine months of FY2026** and a narrowing equity deficit. Both facts are
  published side by side on the Session G tenant page (flagged R-08).


## Session J dashboard (`session-6ad87c21/`) — 2026-11-08

A ninth, independent session (`arena/6ad87c21-jack2`) re-verified the evidence base from scratch on **2026-11-08**
and published a clean decision dashboard at
**https://wingbangboozle1-lang.github.io/Jack2/session-6ad87c21/**. It supersedes nothing: the root build, `docs/`
and Sessions A–I are unchanged and remain live.

| | |
|---|---|
| Recommendation | **Dual track: pursue an early 10–15 year extension at or above in-place rent, prepare a §1031 exit in parallel, sell 2029–2032 with more than ten years of term.** If the extension fails by 31 Dec 2027, sell in 2028. Never let the lease expire. |
| Evidence | 114 fact rows — **92 verified, 4 computed, 3 owner-supplied, 15 deliberately blank** — against **17 official sources opened and read on the access date** |
| Model | Six strategies carried to 2040, deterministic Bear/Base/Bull, a **seeded 10,000-trial Monte Carlo** (seed 20261108), a 7-column sensitivity grid, a 5-point cap-rate break-even and 8 robustness stress cases; **21 assumptions published with the range tested** |
| Risks | 31 rows — 19 business-as-usual and 12 black-swan — each mapped to the four decisions it affects |
| Review | **10 repository irregularities** (I-01…I-10) plus 15 unverified data items, published with evidence and a stated fix |
| Privacy | No address, APN, rent, basis, loan or owner identity anywhere; enforced by a build-failing scan in `scripts/verify.py` |

Headline numbers per $100,000 of in-place NOI at 2040, after tax: hold-to-expiry-and-renew ranks first on the
risk-adjusted measure ($4.26m), extend-then-sell second ($4.15m), sell-now-through-a-§1031 third ($4.00m, and the
best worst-5% floor at $3.47m). A §1031 exchange is worth **+$646,520** against a taxable sale; letting the lease
expire is **−23%** against the leader.

Rebuild and verify:

```bash
python3 session-6ad87c21/scripts/model.py            # deterministic + seeded Monte Carlo
python3 session-6ad87c21/scripts/build_site.py       # 14 pages
python3 session-6ad87c21/scripts/verify.py           # 1,367 checks: sources, blanks, links, PII, model
```

Two facts worth knowing before reading any other workbook in this repository:

- **The tenant is not the brand.** 93.0% of Jack in the Box's 2,115 restaurants are franchised, so the lease on a
  franchised unit is credit to a franchisee entity, not to the issuer. Every dashboard here should be read with that
  in mind.
- **There is no verified cap rate anywhere in this repository**, including here. There is no official public
  cap-rate series; every valuation in every workbook is conditional on an assumption. Obtain a broker opinion of
  value before relying on a level.

## Session I dashboard (`session-343c7030/`) — final integration

A ninth, independent session (`arena/343c7030-jack2`) performed the final integration pass on 2026-11-08 and published
**https://wingbangboozle1-lang.github.io/Jack2/session-343c7030/**. It is now the first entry on
[`workspaces.html`](https://wingbangboozle1-lang.github.io/Jack2/workspaces.html), which lists all nine builds.

| | |
|---|---|
| Question | Sell the NNN lease before it expires in 2030–2035, or renew? |
| Recommendation | **Do not hold to expiry.** Extend now at or above in-place rent, then sell in 2032 with term through a §1031 exchange (S3). Selling now through the same exchange (S1) is 2.1% behind and wins when rent growth disappoints. A taxable sale (S2) costs 4.4% of certainty-equivalent wealth. Holding to expiry (S4) has the higher median and a 5th-percentile outcome $176,615 worse per $100k NOI. |
| Evidence | 98 fact rows: **84 verified** against **16 official sources** read on 2026-11-08, **14 deliberately blank** and published on the flagged page. Nothing inferred. |
| Model | Five strategies, deterministic 2026–2040 plus 15,000-trial seeded Monte Carlo (seed `20261108`), CRRA-2.5 certainty equivalent, 15 published assumptions, 9-cell sensitivity grid, replacement-growth and expiry-year grids |
| Risk | 30-row register: 18 business-as-usual and 12 black-swan events, each mapped to the strategies it bites |
| Review | 13 repository irregularities with evidence and action — including the Census URL defect carried by the root build, which this session **fixed** |
| Privacy | No address, APN, rent, basis, loan term or owner identity anywhere; enforced by a build-failing scan |

Rebuild:

```bash
python3 session-343c7030/scripts/model.py        # data/projections.json
python3 session-343c7030/scripts/build_site.py   # 12 pages
python3 session-343c7030/scripts/verify.py       # 7 rule families, exits non-zero on failure
```

Two things worth knowing before reading anything in this repository:

- **The root build's Census URL is now fixed.** `data/sources.json` S2 pointed at a slug
  (`lacountycalifornia`) that renders a *United States* table and silently drops the county column. Session G flagged it;
  Session G's own corrected URL was published alongside it; Session I has now corrected the shared file itself, re-read both
  columns on 2026-11-08, and rebuilt the root site. No value changed. Evidence: `session-343c7030/flagged.html` R-01.
- **Four commonly cited government URLs return 404** and are flagged rather than copied: the USGS earthquake FAQ, the BOE
  Proposition 13 page, two IRS §1031 pages and the BEA county-income release. Replacement URLs are published with the rows
  they support; the BEA figure is *not* republished because no working official page was found.
