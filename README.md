# Central Los Angeles Jack in the Box (NNN) — sell vs renew decision workbook

A verifiable decision workbook for a single-tenant Jack in the Box restaurant on an NNN lease in
Central Los Angeles, with a lease expiration window of 2030–2035.

**Live site:** https://wingbangboozle1-lang.github.io/Jack2/

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
