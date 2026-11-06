# Jack2 — Anonymous NNN Property Decision Dashboard

Source-linked, public-safe research and conditional decision support for a Jack in the Box NNN property described only as “around central Los Angeles,” with a user-reported lease expiry range of 2030–2035.

**Live dashboard:** https://wingbangboozle1-lang.github.io/Jack2/

> This is not an appraisal, legal opinion, tax opinion or personalized investment recommendation. No property address, owner identity, rent, executable sale price, executed lease option or parcel hazard record was supplied. Missing property values remain blank and are flagged for review. The current recommendation is a conditional dual-track process: obtain market bids while reviewing the lease and negotiating a tenant-supported extension; do not blindly hold to expiry or assume renewal.

## What is included

- Executive overview and explicit sell / hold / extension decision gates.
- 66 regional and tenant evidence rows, 9 official forecast rows, 28 blank property inputs, 30 risk pathways, 16 decision alternatives and 44 review flags.
- Category subpages for demographics, income, education, employment, geography, housing, business/trade, infrastructure, inflation/rates, tenant/brand, regulation/tax and hazards.
- A deterministic normalized cash-flow model: 16 scenario/tail paths and 15 one-way sensitivity points. All numeric controls are flagged hypotheses, not verified property inputs.
- Source library with curated issuing-source excerpts and visible source links on every data row.
- Searchable tables and CSV downloads. No analytics, cookies, forms, external runtime scripts or CDN assets.

## Reproduce locally

Requires Node 22+ and Python 3.11+ (standard library only).

```bash
python research/assemble.py   # regenerate curated public-safe research JSON
npm ci
npm run check                 # build + model/verification tests + deterministic/source/link/privacy checks
npm run preview               # static preview on 0.0.0.0:4173
```

Generated directories `site/` and `reports/` are intentionally not committed. GitHub Actions rebuilds, verifies and deploys `site/` to GitHub Pages on `main`.

## Repository map

| Path | Purpose |
|---|---|
| `COORDINATION.md` | Session claims, branch-policy note, audit and integration log |
| `data/research.json` | Curated evidence, blank property fields, risks, decisions, flags and sources |
| `data/analysis.json` | Executive recommendation, methodology, assumptions and limitations |
| `research/assemble.py` | Reproducible assembler for the curated research register |
| `scripts/model.mjs` | Normalized monthly cash-flow and same-basis sale comparison |
| `scripts/build.mjs` | Static dashboard generator |
| `scripts/verify.mjs` | Schema, source-excerpt, row-link, internal-link, privacy and determinism checks |
| `tests/` | Node built-in test suites |
| `.github/workflows/pages.yml` | Verify and deploy workflow |

## Evidence and privacy boundaries

Official-government, official-company SEC, and original issuing-organization sources are distinguished. County, metropolitan and school-district figures are proxies, not parcel evidence. Forecasts are not observations. Scenario values are mathematical stress controls, not market estimates. Automated checks validate internal consistency and citation structure; they do not independently appraise the property or re-fetch live sources at build time.

Public outputs use placeholders such as `[PROPERTY]`. Do not add addresses, parcel numbers, owner/tenant personal identifiers, contacts, account data or identifying financial documents to this repository or website.
