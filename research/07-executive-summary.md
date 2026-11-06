# Executive Summary

**Asset:** single-tenant NNN Jack in the Box, central Los Angeles · `PROP-001` · address redacted
**Question:** sell before the 2030–2035 lease expiry, or renew and hold?
**Prepared:** 2026-11-06 · **Data cut-off:** 2026-11-06 · **Model:** `model/projection_model.py` (seed 20261106, 20,000 trials)

---

## The decision

**Do not let this lease run to expiry. Run a dual track for the next 6–12 months: pursue an early 10–15 year extension *and* prepare a §1031 sale at the same time. Sell either way — the only variable is whether you sell with 13–15 years of term or with 4–9.**

| Rank | Strategy | Risk-adjusted score (CE) | Why |
|---|---|---|---|
| **1** | **Sell now via §1031 exchange** | **11.79** | Best risk-adjusted outcome; +14.6 % vs paying the tax; removes tail risk |
| 2 | Negotiate extension, then sell in 2028 | 11.06 | Nearly as good, **if** the franchisor cooperates (55 % modelled) |
| 3 | Sell now, pay the tax | 10.29 | Safe, but unnecessarily expensive |
| 4 | Hold to expiry, sell vacant | 9.34 | **Dominated — the "do nothing" trap** |
| 5 | Renew at expiry, hold to 2040 | 3.97 | Highest median, **5× worse tail** |

Scores are present value of after-tax wealth at a 2040 horizon, per $1.00 of current annual NOI. Multiply by actual NOI.

---

## Five findings that drive the answer

**1. Time is destroying value mechanically — about 25 % of it.**
On the model's cap-rate term curve the asset is worth **$12.48 per $1 of NOI today** (midpoint expiry, 6.15 years remaining) and **$9.64** once the lease is inside its final year. That is **−22.7 %** from the passage of time alone, with no change in rent, tenant or market. Every month the lease runs down, the Owner gives that away for free.

**2. A signature is worth more than a rate cut.**
Moving from 6.15 years remaining to ~15 years moves the model cap rate from **8.02 % to 6.40 %** — the same NOI is suddenly worth **$15.62 instead of $12.48** per $1. That is **+25.2 %**, or **≈ $630,000** on a $200,000-NOI asset. No plausible interest-rate scenario competes with that.

**3. The trade area will not bail the asset out.**
Los Angeles County has **lost 322,480 residents (−3.2 %)** since the 2020 census base. Metro payrolls have grown **+0.10 % per year over seven years** and are **1.2 % below** their October 2024 peak. County median household income is $90,112 against a $834,200 median home value. There is no growth engine here — this is a mature, deep, slowly contracting market. **Underwrite zero real NOI growth.**

**4. The tenant is retrenching, and the market already knows it.**
Jack in the Box system same-store sales fell **−4.2 % in FY2025** and **−7.4 % in Q4 FY2025**. The store base went **2,168 → 2,115** in four quarters, with 51 closures in a branded "JACK on Track" block-closure programme. Del Taco was bought for ~$585 m in 2022 and sold for ~$119 m in December 2025. Cap rates for franchisee-quality QSR sit at **6.85 %** versus **5.85 %** for corporate credit — a 100 bp gap worth roughly 15 % of value. **Whether a corporate guaranty exists is the most valuable single fact not yet known.**

**5. The rate environment is moving against holding, not toward relief.**
The 10-year Treasury went **4.06 % → 5.13 %** in twelve months and printed **5.31 %** on 2026-10-05. The Fed **stopped cutting and hiked to 3.88 % on 2026-09-17**. The 30-year mortgage is **7.18 %**. Net-lease cap rates rose to **6.92 %** in Q3 2026 and the market is "resetting to a higher cost of capital rather than waiting for relief."

---

## The risk answer

The Owner asked for wealth preservation with manageable risk. That is exactly the frame in which the intuitive answer — *renew and hold* — fails.

**Renew-and-hold wins 52.6 % of the time and has the highest median outcome (12.45).** It also has a worst-decile outcome of **1.88× NOI**, against **10.96× NOI** for selling via §1031. That is the signature of a concentrated single-asset, single-tenant, single-metro bet: usually fine, occasionally ruinous.

**The recommendation survives the stress tests:**
- In a severe black-swan replay (10-yr to 6.90 %, zero rent growth, 25 % renewal probability), holding loses **34.3 %** relative to selling. The ranking does not flip.
- Across a **350 bp range** of terminal 10-year Treasury (3.50 %–7.00 %), selling via §1031 ranks first every single time. **This is not a rates call.**
- The one input that changes the answer is the Owner's discount rate: at 6 %, "extend then sell" wins. An Owner with a low opportunity cost of capital should take the extension premium before selling.

**The tail risks that matter:** tenant/franchisee default (3.5 %/yr modelled); wildfire and smoke (California lost **16,627 structures** in 2025, four LA County incidents ≥5,000 acres); seismic (region-wide and correlated, so diversification inside LA cannot fix it); insurance repricing; and — the most under-appreciated — a failed §1031, which converts a deferred gain into a fully taxable one.

---

## What to do first: the $500,000 phone call

The Owner supplied an expiry **range** (2030–2035), not a date, and **no lease document, rent roll or basis**. Moving the assumed expiry from 2030 to 2035 changes value from **$11.57 to $14.07** per $1 of NOI — a **21.6 %** swing, or **$500,000** on a $200,000-NOI asset.

**Reading the lease is worth roughly half a million dollars and costs nothing.** It is, by a wide margin, the highest-return action available and nothing else should be decided before it. Specifically, confirm:
- exact expiry date;
- escalation clause (flat rent during 3.72 % inflation is a guaranteed real-terms loss);
- **who holds the options and at what rent** (a tenant option at fixed rent caps the Owner's upside and depress the sale price);
- **guarantor** — corporate Jack in the Box Inc., franchisee, or personal;
- absolute-net vs roof/structure carve-out;
- any early-termination or kick-out right.

Then confirm the franchisee's financial standing, and whether the site has redevelopment value. **That last point is the largest un-quantified upside in the analysis**: a central-LA infill drive-thru parcel can be worth more as land under current state housing law than as a 6.5 %-cap QSR. Long-term renewal would extinguish that option. It was **not** possible to test without an address — flagged for review.

---

## What could not be verified (all published on the Flagged for Review page)

| Item | Why it is blank |
|---|---|
| Street address, APN, legal description | **Deliberately withheld for privacy** — no personal or parcel data is stored or published |
| Exact lease expiry, escalations, options, guarantor | Lease document not supplied |
| Current rent, NOI, basis, debt terms | Not supplied; the model is normalised per $1 of NOI instead |
| Parcel fire-hazard-severity zone, FEMA flood zone, seismic site class | Requires an address |
| School assignment and school quality | Requires an address |
| Jack in the Box-specific net-lease cap rate | Not retrieved; the model derives a term curve from Boulder Group QSR anchors instead |
| California DOF county population projections | Distributed as `.xlsx`; not machine-verified, so Census V2025 estimates were used |
| FEMA National Risk Index county score | API returned HTTP 500 on 2026-11-06 |
| California tax treatment of out-of-state §1031 replacement (FTB 3840) | Needs a California tax opinion |
| CA top marginal rate of 13.3 % used in the tax module | Used as an assumption; not re-verified this session |

---

## Sources (full list with links on the site's Methodology page)

**Official (Tier 1):** FRED / Federal Reserve Bank of St. Louis (`DGS10`, `GS10`, `MORTGAGE30US`, `DFF`, `CPIAUCSL`, `SMU06310800000000001`, `CALOSA7URN`) · U.S. Census Bureau QuickFacts · U.S. Bureau of Labor Statistics · U.S. Securities and Exchange Commission EDGAR (Jack in the Box FY2025 Form 10-K; FY2026 Q3 results) · Internal Revenue Service Topic 409 and the §1031 guidance · CAL FIRE 2025 Incident Archive and Office of the State Fire Marshal · California Legislative Information (AB 1228, Ch. 262, Statutes of 2023) · Los Angeles County Assessor.

**Industry (Tier 3, explicitly non-government):** The Boulder Group — *Single Tenant Net Lease Research Report* Q2 and Q3 2026; *Net Lease Tenant Profiles* Q3 2026.

**Every row of every table on the site carries its source link and a tier badge. Unconfirmed values are left blank and flagged, never inferred.**

---

## One-paragraph answer

Sell. Specifically: spend four weeks reading the lease and confirming the guarantor, six months trying to buy 10–15 more years of term from the franchisor, and then go to market — with an extension if you got one, without it if you did not. Execute through a §1031 exchange with a qualified intermediary engaged before closing, and plan to spread the proceeds across at least two assets to break the single-parcel concentration. Do not wait for the lease to expire: the passage of time alone costs about a quarter of the asset's value, the trade area is shrinking, the tenant is closing stores, and rates are rising against you. The expected cost of doing nothing is larger than the tax bill you are trying to avoid.
