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
9. `analysis/index.html` — a **second, independent model** built by a third session: Monte Carlo
   instead of a deterministic projection, normalised per $1 of NOI instead of a benchmark rent

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
analysis/       third session's independent build: own data, own model, own verifier, own pages
tools/          model.py, build_site.py, check_site.py, export_ledger.py
research/       model report and the manual-review verification ledger
assets/         style.css, app.js (progressive enhancement only)
*.html          the published site (GitHub Pages serves main / root)
COORDINATION.md shared task board for parallel sessions
```

## The second model

`analysis/` is a complete, independent build of the same decision, produced by a third session that
started from the same one-line repository and never saw this one's output.

|  | This site | `analysis/` |
|---|---|---|
| Unit of account | dollars, from a benchmark rent assumption | per $1.00 of NOI — no rent assumed |
| Model | deterministic 2026–2040, breakevens, sensitivity | 20,000-path Monte Carlo, three expiry cases, seeded |
| Headline | extend at a reset, price 2027–28, sell if the numbers clear | sell now, §1031 into a diversified net lease |
| Margin | thin: ~$247k on ~$5.9M of 2040 wealth | wide: 33.26 vs 26.70 per $1 NOI |
| Tax | modelled with an assumed basis | mechanics verified, no after-tax figure claimed |

The direction agrees — redeploying beats holding — and the magnitude does not. That gap is a real
finding, not a defect: it turns on the 2036 exit cap and the cost of the rollover year, so
`analysis/projection.html` publishes the break-even exit cap (~4.7%) as a testable number. Read both
before deciding; neither overrides the other.

Rebuild it separately: `cd analysis && python3 model/projection.py && python3 build.py && python3 verify.py`.

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

## Session E dossier (`session-50002478/`, `scripts/`, `tests/`, `data/research.json`)

A fifth independently built, source-linked dashboard is published from the same legacy Pages deployment at
**https://wingbangboozle1-lang.github.io/Jack2/session-50002478/**. It does not replace the root workbook,
the Session A archive, the `docs/` dossier or the `session-a3a8ec08/` dashboard.

| | |
|---|---|
| Question | Sell before expiry, hold, or pursue a tenant-supported extension under an unverified 2030–2035 expiry range |
| Method | Deterministic normalized monthly cash-flow model; 16 scenario/tail paths and 15 one-way sensitivities; no Monte-Carlo probabilities or property-specific price target |
| Conclusion | Conditional dual-track: obtain executable market bids while reviewing the executed lease and negotiating an extension; no blind hold or automatic renewal |
| Data | 66 regional/tenant evidence rows, 9 official forecast rows, 28 blank property inputs, 30 risks, 16 alternatives, 44 flags, 34 issuing-source records |
| Privacy | Placeholder-only public outputs; no address, APN, owner/tenant personal identifiers, contacts or account data |

Rebuild and verify:

```bash
python research/assemble.py
npm ci
npm run check       # build + 23 Node tests + deterministic/source/link/privacy verification
npm run preview     # local preview on 0.0.0.0:4173
```

The generated dossier is committed under `session-50002478/` because the existing GitHub Pages source is
`main` / root (legacy build). `site/` and `reports/` remain ignored scratch/output directories.

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
