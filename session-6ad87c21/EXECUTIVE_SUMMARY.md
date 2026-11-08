# Executive summary — Session I

**Asset:** a single-tenant Jack in the Box restaurant on a triple-net lease in Central Los Angeles.
**Question:** sell before the lease expires (somewhere in 2030–2035), or renew?
**Prepared:** 2026-11-08. Every published value is linked to an official source read on that date. 114 fact rows:
92 verified, 4 computed from verified figures, 3 supplied by the owner, 15 deliberately blank and flagged.

---

## The decision

Run a **dual track from today**:

1. **Approach the tenant and the brand for a 10–15 year extension at or above in-place rent**, with escalations at
   or above CPI. This costs no transaction tax and converts a decaying lease into a saleable one.
2. **Prepare a Section 1031 exit in parallel** — qualified intermediary engaged, replacement candidates identified
   before listing.
3. **Sell in 2029–2032, with more than ten years of term remaining**, into a diversified net-lease portfolio.
4. If the extension does not materialise at acceptable rent by **31 December 2027, sell in 2028 anyway**. If the
   tenant credit cracks earlier, sell immediately.
5. **Never let the lease expire without a signed commitment.** That is the worst of the six modelled outcomes.

## Why

| # | Reason | Evidence |
|---|---|---|
| 1 | Term *is* the asset. Buyers pay a wider cap rate for shorter leases; the model charges 25 bp per year below ten years of term. | Assumption A4, tested 15–35 BP |
| 2 | The tenant is under pressure and the obligor is probably a franchisee. Same-store sales −1.1% in Q3 FY2026 after −7.1%; 50–60 closures guided; dividend suspended; 93.0% of 2,115 units franchised. | [S07](https://www.sec.gov/Archives/edgar/data/807882/000080788226000090/ex991-q326earningsrelease.htm) |
| 3 | The local economy is stable, not growing. Metro unemployment 4.4%, payrolls +0.5% in a year, information employment −5.7%; the state projects county population *falling* 1.8% by 2040. | [S01](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) · [S04](https://dof.ca.gov/media/docs/forecasting/Demographics/projections/P2A_County_Total.xlsx) |
| 4 | Rates are the swing factor and they just rallied: 10-year Treasury 5.31% on 5 October → **4.86%** on 6 November 2026. | [S09](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value_month=202611) |
| 5 | The tax decides the *mechanism*. A §1031 exchange is worth about **$646,520 more per $100,000 of NOI** than selling and paying the tax — the largest controllable number in the analysis. | [S12](https://www.irs.gov/pub/irs-news/fs-08-18.pdf) |
| 6 | Letting it expire is 23% worse than the leader on the risk-adjusted measure. | Model |

## The six strategies, per $100,000 of in-place NOI, after tax, at 2040

| Rank | Strategy | Certainty equivalent (CRRA 2) | Worst 5% | Mean |
|---:|---|---:|---:|---:|
| 1 | Hold to expiry, renew at market, sell in 2036 | $4,258,340 | $2,875,073 | $4,537,599 |
| 2 | Extend early in 2027, sell in 2030 with 12 years of term | $4,154,212 | $2,828,149 | $4,364,404 |
| 3 | Sell now through a §1031 exchange | $4,000,783 | **$3,466,627** | $4,036,953 |
| 4 | Sell now and pay the tax | $3,354,263 | $2,912,206 | $3,381,729 |
| 5 | Hold through 2040 and never sell | $3,348,066 | $2,610,034 | $3,436,199 |
| 6 | Do not renew: go dark, re-let, sell in 2036 | $3,277,264 | $2,609,097 | $3,342,134 |

The top three are within about 6% of each other — inside the model's error. The bottom three are 20–23% below the
leader. So the robust conclusions are structural, not tactical: **do not sell without term if term can be created,
do not let the lease expire, do not pay tax that a qualified exchange can defer, and do not assume a friendly
renewal.**

## Triggers that change the answer

| Trigger | Action |
|---|---|
| No extension at ≥ in-place rent by 31 Dec 2027 | Sell in 2028 via §1031 |
| Missed rent, franchisee default, unit on a closure list | Sell immediately |
| 10-year Treasury below 4.00% | Bring the sale forward |
| 10-year Treasury above 5.75% | Do not sell into the spike |
| Renewal offer >10% below in-place rent | Reject and sell with remaining term |
| Insurance more than doubles, or quake cover withdrawn | Accelerate the sale |

## Risks that dominate

- **Term decay** — certain, not probable, and avoidable without forecasting anything.
- **Earthquake** — 60% chance of M≥6.7 in the Los Angeles region within 30 years; 46% of M≥7.0; 31% of M≥7.5
  ([USGS](https://www.usgs.gov/faqs/what-probability-earthquake-will-occur-losangeles-area-san-francisco-bay-area)).
  Not diversifiable inside one building; insurable, retrofittable, or transferable by sale.
- **Tenant credit** — 93% franchised, 50–60 closures a year, negative book equity. The exposure is one franchisee's
  balance sheet, which this workbook cannot see.

## What this is not

Not an appraisal. There is no official public cap-rate series, so **every valuation here is conditional on a stated
assumption** — the one number to replace first with a broker opinion of value. The address, rent, basis, loan terms
and the lease itself were not supplied and are not guessed at. Eleven lease facts that must be obtained are listed
on the property page; all 15 unverified items are on the Flagged for Review page with the office that publishes each.

**Privacy:** no name, address, APN, rent, basis or loan figure appears in this workbook or on the site. Every output
is normalised to $100,000 of NOI.

---

Rebuild: `python3 session-6ad87c21/scripts/model.py && python3 session-6ad87c21/scripts/build_site.py &&
python3 session-6ad87c21/scripts/verify.py` — Python 3.11, standard library only, deterministic.
