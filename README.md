# Central Los Angeles Jack in the Box (NNN) — sell vs renew decision workbook

A verifiable decision workbook for a single-tenant Jack in the Box restaurant on an NNN lease in
Central Los Angeles, with a lease expiration window of 2030–2035.

**Live site:** https://wingbangboozle1-lang.github.io/Jack2/

> A third, independently built dossier — Monte-Carlo over five strategies, ranked on risk-adjusted
> after-tax wealth — is published from this same Pages deployment at
> **https://wingbangboozle1-lang.github.io/Jack2/docs/** (source in `docs/`, engines in `model/`,
> analysis in `research/00`–`07`). The root site below is unchanged. See `COORDINATION.md` → *Session C*.
>
> A fourth, independently built dashboard — every row source-linked, computed projections with formulas
> shown, and a flagged-for-review register — is published from this same Pages deployment at
> **https://wingbangboozle1-lang.github.io/Jack2/session-b4ec6128/** (source in `session-b4ec6128/`,
> working notes in `research/02-demographics.md`–`08-analysis.md`, checker in `scripts/verify.py`).
> The root site below is unchanged. See `COORDINATION.md` → *Session D*.

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
