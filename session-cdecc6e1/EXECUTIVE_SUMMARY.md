# Jack 2 — Executive Summary (Session I)

**Subject:** anonymized Central Los Angeles Jack in the Box property, NNN lease, expiry 2030–2035.
**Branch:** `arena/cdecc6e1-jack2` · **Access date:** 2026-11-08 · **Status:** complete workbook, 14-page static site, all checks pass.
**Privacy:** no personal information appears anywhere in this directory or on the site; owner, entity, address, APN, rents and financials are replaced by placeholders.

## Recommendation (preliminary, pre-tax, not an appraisal)

**Extend the lease now to create a 10+ year WALT, then sell in 2027–2028** — ahead of the 2030–2035 expiry and its rent re-pricing, tenant-credit, cap-rate, insurance and population-decline risks. If a buyer will not pay roughly a 6.3% cap or better, selling now (preferably via a Section 1031 exchange) is the alternative; holding to expiry is the lowest-scoring option.

Ranked options: (1) extend → sell; (2) hybrid 5-year extension with years 3–5 sale window; (3) sell now via 1031/outright; (4) hold to expiry.

## What the model shows (verified inputs + labelled assumptions)

Modelled rent $150,000/yr (placeholder = 8% of the verified franchise AUV of $1,874k; replace with contract rent), expiry 2032 (midpoint placeholder), discount 8%, 10-year Treasury 4.84% (2026-11-05, FRED T12):

| Exit cap | Sell now, net proceeds (4.06% base stack) | Hold & renew, PV to 2040 | Hold minus sell |
|---|---:|---:|---:|
| 5.50% | $2,616,545 | $2,298,789 | −$317,756 |
| 6.00% | $2,398,500 | $2,298,789 | −$99,711 |
| 6.50% | $2,214,000 | $2,298,789 | +$84,789 |
| 7.00% | $2,055,857 | $2,298,789 | +$242,932 |
| 7.50% | $1,918,800 | $2,298,789 | +$379,989 |

Hold wins if the exit cap is ≳6.3%; sell wins below that. All figures pre-tax; owner basis unknown (P05), so a CPA tax model and an appraisal (P11) are preconditions to any binding offer. California conformity to IRC 1031 for state tax purposes was not independently re-confirmed this session (flagged X-06).

## Local economy (all verified this session)

- LA city population 3,869,089 (Jul 2025, −0.8% since 2020); LA County projected 9,853,435 (2025) → 9,727,305 (2030) → 9,708,647 (2035) → 9,637,524 (2040) (−3.7% vs 2020; CA DOF P-2A T03)
- Median household income $81,939; per capita $47,685; poverty 16.5%; median home $921,200; median gross rent $1,933/mo (Census QuickFacts T02)
- Sep 2026 unemployment: US 4.0%, CA 5.1%, LA metro 4.4%, LA County 4.5%, LA city 4.5%; nonfarm jobs 6,282.1k, +0.5% YoY (BLS T01); white-collar sectors contracting (information −5.7%, prof & biz −0.5%, financial −1.7%)
- CPI-U LA metro +3.7% (Sep 2026); Q1 2026 LA County average weekly wage $1,704 (T01)
- LAUSD enrollment 497,105 (2025-26; English learners 16.4%; CDE T15)
- LA County personal income $818.5B (2024, largest US county; BEA T16)

## Tenant credit (SEC EDGAR, verified)

- 2,136 system units (93% franchised); −55 units in FY2025; franchise AUV $1,874k FY2025 (−3.8% vs FY2024); ~70% of units in CA + TX; company names severe weather/natural disasters as a risk factor
- "We have generally been able to renew our restaurant leases as they expire at then-current market rates" (FY2025 10-K T09)
- Q3 FY2026 10-Q filed 2026-08-12 (period ended 2026-07-05, T10): figures intentionally not quoted — pull at decision time

## Taxes & transaction costs (verified)

- Prop 13: 1% levy cap, 2% annual AV cap, reassessment on change of ownership (T06)
- County DTT 0.11%; City of LA DTT 0.45%; Measure ULA 4.0% ($5.4M–$10.9M) / 5.5% (≥$10.9M) for closings on/after 2026-07-01, thresholds chained-CPI indexed (T07/T08)
- Section 1031 available for real property held for business/investment; 45/180-day rules; qualified intermediary (T14)

## Risks (full register: 24 risks)

Top risks: tenant non-renewal (R-01), franchisee credit/shrink (R-02), cap-rate expansion (R-03), tax cost of sale (R-04), Measure ULA surtax (R-10, high), wildfire (R-12), earthquake on Central LA blind-thrust systems (R-13, black swan R-22), insurance capacity/premium shock (R-15, high), metropolitan-scale wildfire (R-21, black swan), brand-level shock (R-19). Parcel-level FHSZ, seismic, flood and insurance premium determinations were not performed (APN withheld) and are flagged M88–M91.

## Flagged items (published non-blocking, 7 items)

X-01 CAL FIRE FHSZ URL 404 → replaced with current page (T17). X-02 CDI FAIR Plan URL 404 → replaced with live page (T20). X-03 Census county-income slug broken → county income blank. X-04 UCERF3 page 404 → seismic probabilities not re-verified. X-05 data-vintage differences documented side by side. X-06 CA 1031 conformity unconfirmed. X-07 poverty/per-capita income were blank in root build; confirmed this session.

## Immediate next steps (P-list)

P01–P13 fields required from the owner before a binding decision (lease, expiration date, rent roll, expenses, basis, debt, APN, condition report, insurance, franchisee financials, appraisal, zoning, Q3 FY2026 10-Q figures). All are listed in `data/property_lease.json` and on the Property & Lease page; none contain personal information.

Site: 14 pages under this directory, generated by `scripts/build_site.py` and checked by `scripts/verify.py` (0 failures). Integration into the root GitHub Pages site and the pull request to `main` are tracked in `COORDINATION.md`.
