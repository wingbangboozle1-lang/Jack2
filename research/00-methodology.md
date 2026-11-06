# 00 — Methodology, Source Standards & Privacy Protocol

**Project:** Jack2 — Hold / Renew / Sell analysis for a single-tenant NNN Jack in the Box in central Los Angeles
**Prepared:** 2026-11-06 · **Session:** `session-230fe704` · **Data cut-off:** 2026-11-06

---

## 1. Privacy protocol (highest priority)

This is the binding rule set for every artefact in this repository and on the published site.

| Rule | Implementation |
|---|---|
| No owner identity | Owner is referred to only as **"the Owner"** or `PARTY-OWNER`. No name, entity name, address, phone, or email appears anywhere. |
| No tenant-contact identity | Franchisee/operator is **"the Tenant"** or `PARTY-TENANT`. Corporate contacts are not named. |
| No parcel identity | Address is **`[ADDRESS REDACTED]`**; Assessor's Parcel Number is **`APN [REDACTED]`**; legal description is **`[LEGAL DESC REDACTED]`**. |
| No financial identifiers | Loan numbers, account numbers, tax IDs: **`[REDACTED]`**. |
| No personal financials | The Owner's income, net worth, tax bracket and basis are **not stored**. All tax modelling is expressed as rates and formulas applied to hypothetical inputs. |
| No geolocation | The site does **not** state a street address, cross-streets, or a coordinate. Trade-area analysis is done at **county / city / metro** level, which is the finest geography for which official statistics were verified. |
| Research hygiene | Raw page captures are never committed. `.gitignore` blocks `private/`, `*.private`, `*.pii`, `*.csv.raw`. |
| Right to delete | If any personal data is discovered in this repo, delete the file, purge history, and log the event in `COORDINATION.md` → Incident log. |

**Consequence, stated plainly:** because the address was deliberately not retained, the property cannot be geocoded, so parcel-level facts (fire-hazard-severity zone, flood zone, seismic site class, assessed value, school attendance area) **cannot be verified** in this session. They are reported as **UNVERIFIED — requires address** on the Flagged for Review page rather than being guessed.

---

## 2. Source tiers

Every table row on the site carries a tier badge and a link.

| Tier | Meaning | Examples used here |
|---|---|---|
| **T1 — Official** | A government or central-bank primary source. | FRED (Federal Reserve Bank of St. Louis), U.S. Census Bureau, U.S. Bureau of Labor Statistics, U.S. SEC EDGAR, IRS, CAL FIRE / Office of the State Fire Marshal, California Legislative Information, LA County Assessor |
| **T2 — Official-adjacent** | Primary-source data published by the issuing institution's own site where the underlying series originates with T1. | FRED series pages (each cites BLS/BEA/Census as source) |
| **T3 — Industry** | A named commercial research house. Not government. Directional, not authoritative. **Always labelled as such.** | The Boulder Group net-lease research reports |
| **T4 — Secondary press** | Trade press / news. Used only to *locate* a T1 filing, never as the final authority. | NRN, Restaurant Business, Verdict Foodservice |
| **A — Assumption** | An analytical input chosen by this model. **Never presented as fact.** | rent escalations, sale costs, renewal probability |
| **D — Derived** | Arithmetic performed by this model on T1/T2 inputs, with the formula shown. | YoY growth rates, per-capita figures, cap-rate term premiums |

A row is **only** marked *verified* when a T1/T2 link resolves and the number matches. Everything else is blank + flagged.

---

## 3. Verification procedure actually performed

1. Each metric was retrieved from a resolving official page or CSV endpoint on 2026-11-06.
2. The **period/vintage** is recorded per row (e.g. "Sep 2026", "V2025", "FY2025", "ACS 2020-2024"). Rows are never compared across incompatible vintages without saying so.
3. Percentages were recomputed from the raw series, not copied from commentary:
   - CPI YoY = 336.298 / 324.245 − 1 = **+3.72 %**
   - LA-metro payrolls, Sep 2019 → Sep 2026 = 6,282.1 / 6,236.7 − 1 = **+0.73 %** over 7 years
   - LA-metro payrolls, Oct 2024 peak → Sep 2026 = 6,282.1 / 6,359.6 − 1 = **−1.22 %**
   - LA County population, 2020 base → Jul 2025 = from Census QuickFacts V2025, **−3.2 %** (published, not recomputed)
4. Endpoint pattern for reproducible pulls:
   - `https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIES>&cosd=YYYY-MM-DD&coed=YYYY-MM-DD`
   - `https://www.census.gov/quickfacts/fact/table/<geography>/PST045224`
   - `https://www.sec.gov/Archives/edgar/data/<cik>/<accession>/<doc>.htm`
   - `https://efts.sec.gov/LATEST/search-index?q=...&forms=10-K` (full-text filing locator)

## 4. Known limitations (flagged, not hidden)

| # | Limitation | Consequence |
|---|---|---|
| L1 | No street address or APN supplied. | Parcel-level hazard, zoning, assessed value, and school assignment are **unverified**. |
| L2 | The lease document was not supplied. "NNN" and "expires 2030–2035" are **as described by the Owner**, not verified. Exact expiry, escalation clause, option structure, guarantor, and landlord obligations are **unverified**. | The model parameterises these and shows sensitivity rather than asserting them. |
| L3 | Current rent, NOI, and basis were not supplied. | The model is **normalised per $1.00 of current NOI** so results do not depend on unknown dollars. A dollar illustration is shown separately and labelled **ASSUMPTION**. |
| L4 | `api.census.gov` required a key that was not available. | ACS data were taken from Census **QuickFacts** (Tableau UI, same source data) instead of the raw API. Equivalent source, different access path. |
| L5 | California DOF county population *projections* are distributed as `.xlsx`. | Projections were **not** machine-verified; the DOF series is listed as a follow-up and the population rows use Census Vintage 2025 estimates instead. |
| L6 | FEMA National Risk Index API returned HTTP 500 during this session. | County hazard scores are **not** reported; only CAL FIRE and other T1 figures that resolved are used. NRI is listed as a follow-up. |
| L7 | Cap-rate data are T3 (Boulder Group, a brokerage). | Treated as directional. Every cap-rate row is badged **Industry (non-government)**. No cap rate is asserted as fact. |

## 5. Reproducibility

The projection engine is `model/projection_model.py` (Python 3, standard library only, fixed RNG seed = `20261106`). Its outputs are written to `docs/data/` as JSON and are what the website renders. Re-running the script reproduces every number on the Projection page exactly.
