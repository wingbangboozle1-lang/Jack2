# 06 — Decision Framework, Risk Register and Recommendation

**Bottom line up front (BLUF):** **do not let this lease run to expiry.** Run a **dual track for the next 6–12 months**: (1) attempt an early 10–15 year extension with the franchisor, and (2) prepare to sell into the §1031 market. If the extension can be had on terms that do not give away more than the term premium it creates, take it and sell. If it cannot be had, sell anyway — **now**, not at expiry. "Business as usual" (hold and renew at expiry) is the single most common choice and it is also the worst risk-adjusted outcome in the model.

---

## 6.1 The five courses of action, scored

Model: `model/projection_model.py`, seed `20261106`, 20,000 trials. All figures are **after all taxes**, expressed as the present value to the Owner in 2026 of wealth at a common 2040 horizon, per **$1.00 of current annual NOI**. Multiply by actual NOI for dollars.

| # | Strategy | Mean | Worst-decile (CVaR₁₀) | Risk-adjusted (CE, CRRA=3) | Win rate | Verdict |
|---|---|---|---|---|---|---|
| **A1** | **Sell now via §1031 exchange** | **11.83** | **10.96** | **11.79** | 34.0 % | **Best risk-adjusted** |
| D | Negotiate extension now, sell 2028 | 11.20 | 9.51 | 11.06 | 13.3 % | Best if the franchisor cooperates |
| A | Sell now, pay the tax | 10.31 | 9.66 | 10.29 | 0.0 % | Safe but unnecessarily expensive |
| B | Hold to expiry, sell vacant | 9.90 | 6.21 | 9.34 | 0.1 % | **Dominated — do not do this** |
| C | Renew at expiry, hold to 2040 | 9.62 | 1.88 | 3.97 | 52.6 % | Highest median, catastrophic tail |

### How to read this table — and why it is not a contradiction

Strategy **C wins the most often (52.6 %)** and has the **highest median (12.45)**. It also has the **worst left tail by a factor of five** (worst-decile 1.88 versus 10.96 for A1). That is what a concentrated, undiversified, levered-to-one-parcel, single-tenant bet looks like: usually fine, occasionally ruinous.

That shape is precisely what the Owner asked to avoid. The brief says: *"the best decision for the property and myself as an individual for the preservation of wealth and opportunity for growth, maintaining a balance that outlines risk factors and maintains a manageable level of risk."* Under that stated objective, the risk-adjusted ranking governs, and **A1 wins**.

> **Stated plainly:** if the Owner's only objective were to maximise the most likely outcome, the answer would be *renew and hold*. It is not, because the distribution is barbell-shaped and the downside is a 5× worse tail. **The recommendation is A1 as the default, with D as an upgrade if — and only if — the extension is real.**

## 6.2 Why "hold to expiry, then decide" (B) is the trap

This deserves its own section because it is the intuitive, do-nothing answer and it is measurably the worst.

| Mechanism | What happens |
|---|---|
| **Term decay** | Remaining term falls every month. On the model's cap curve the asset is worth **$12.83 per $1 NOI today** and **$9.64** once the lease is inside its final year — a **−24.9 %** decline from pure passage of time, with no change in rent, tenant or market. |
| **Optionality transfer** | At expiry the Owner holds a **vacant building in a market with flat job growth and falling population**, and the franchisee holds the option to walk. The Owner pays the carry (taxes, insurance, security, code compliance) while the option is exercised against them. |
| **Lost 1031 window** | A §1031 exchange requires identifying replacement property within **45 days** and closing within **180 days** of sale. Selling under time pressure, or after a tenant default, is exactly when an Owner is least able to run a disciplined exchange. |
| **Financing cost** | Buyer financing is priced off a **7.18 %** 30-year mortgage and a **4.90 %** 10-year Treasury. Every quarter of term decay makes the asset harder to finance, which shrinks the buyer pool to all-cash 1031 buyers — who know it. |
| **Measured result** | Mean **9.90**, worst-decile **6.21**, risk-adjusted **9.34** — worse than selling today and paying tax. |

## 6.3 The core quantitative argument

Three numbers do most of the work:

1. **The extension premium is ~23.5 %.** Same NOI, same tenant: moving from ~6.5 years remaining to ~15 years remaining moves the model cap rate from **7.91 % to 6.40 %**, i.e. value from **$12.65 to $15.62 per $1 of NOI**. On a $200,000-NOI asset that is **≈ $595,000** of value created by a signature.
2. **The expiry ambiguity is worth ~$500,000.** Moving the assumed expiry from 2030 to 2035 changes value from **$11.57 to $14.07** per $1 NOI (**+21.6 %**).
3. **Selling costs ~23 % in tax if you sell badly and ~0 % if you sell well.** The illustrative waterfall on a sale at 12.51× NOI: adjusted basis 4.68, total gain 7.83, of which 1.32 is unrecaptured §1250 recapture taxed at 25 %, and **total tax 2.92 (23.3 % of price)**. A §1031 exchange removes it from the sale moment — but it does **not** eliminate the liability, which is why the model deducts it as a contingent liability rather than pretending it is free.

## 6.4 The recommendation, in sequence

### Step 0 — Resolve the unknowns (weeks 0–4, cost ≈ $0)
Nothing else should be decided first. Obtain:
1. The **lease**, redacted. Confirm exact expiry, escalations, options (who holds them, at what rent), guarantor, landlord obligations, and any kick-out right.
2. The **estoppel certificate** from the tenant — this is also what a buyer will demand.
3. The **franchisee's** identity, financial standing, and whether a Jack in the Box Inc. corporate guaranty exists.
4. Current **rent roll, CAM reconciliations, tax bill, insurance binder**.

**Expected value of this step, from the model: ~$500,000 (21.6 % of value) on a $200k-NOI asset.** It is the highest-return action available by an enormous margin.

### Step 1 — Test the extension (months 1–6)
Approach the franchisor with a proposal for a **10–15 year extension**, and expect to pay for it. The model assumes a **4 % rent concession** and a **55 % probability** the franchisor agrees at all — both are assumptions, and both are the swing factors in strategy D.

- If the extension is achievable at **≤ 8 % rent concession**, take it. That is still a large net gain against the 23.5 % term premium.
- If the franchisor demands **> 15 %**, or wants a below-market option, walk. The term premium is being transferred to the tenant, not created for the Owner.

### Step 2 — Sell, in either case (months 6–18)
- With an extension signed: market the asset with **~13–15 years of term**. This is the strategy-D exit and the second-best risk-adjusted outcome (11.06 CE), and it beats selling unextended by **+8.6 %**.
- Without an extension: market the asset **as-is** into the private-capital and §1031 buyer pool, which is the deepest bid for sub-$10 m net-lease product (Boulder Group notes private capital and 1031 buyers "historically represent a significant share of transactions below $10 million").

### Step 3 — Execute the §1031 exchange properly
- Engage a **qualified intermediary before closing**. Under IRC §1031 the Owner cannot touch proceeds and cannot act as their own facilitator.
- **45-day identification / 180-day closing.** Non-extendable except in a presidentially declared disaster.
- **California-specific caution:** California does not allow deferral of California-source gain when replacement property is outside California without an undertaking to file a California return when the replacement is later sold (FTB Form 3840). **Flagged as needing confirmation with a California tax adviser — not verified in this session.** If the plan is to relocate capital out of state, get this opinion *before* identifying replacement property.

### Step 4 — Only consider holding if all of these are true
Holding (C) becomes defensible **only** where *every* one of the following holds:
- [ ] The lease is **absolute net** with a **corporate guaranty**.
- [ ] Escalations are **≥ 2 %/yr** (a flat lease in a 3.72 %-inflation world is a guaranteed real loss).
- [ ] The extension is **≥ 15 years** at market rent with **no tenant-held renewal option**.
- [ ] The Owner has **no concentration need** — this asset is a small fraction of net worth.
- [ ] The Owner can absorb a worst-decile outcome (≈ **1.88× NOI**, versus ≈ 11× if selling) without changing their standard of living.

If even one box is unchecked, the hold case fails on the model's own numbers.

## 6.5 Risk register

Severity is the model's impact on the Owner's wealth; likelihood is judged from the verified evidence in `01`–`05`.

| # | Risk | Category | Likelihood | Severity | Mitigation | Owner action |
|---|---|---|---|---|---|---|
| R1 | **Lease terms unknown** — wrong expiry, below-market option, tenant-held renewal at fixed rent | Structural | **Certain** (document not supplied) | **High** (~21.6 % of value at stake) | Read the lease; get an estoppel | **Blocking — do first** |
| R2 | **Tenant/franchisee default or non-renewal** | Credit | Medium (3.5 %/yr modelled) | **High** — worst-decile collapse to 1.88× NOI | Corporate guaranty; security deposit; personal guaranty; sell before expiry | Due diligence on franchisee |
| R3 | **Term decay** — value falls as lease shortens | Structural | **Certain** | **High** (−24.9 % from 2026 to final year, mechanical) | Extend, or sell before decay compounds | Decision timing |
| R4 | **Cap-rate expansion from rising rates** — 10-yr 4.06 %→4.90 %, Fed hiked to 3.88 %, 30-yr mortgage 7.18 % | Market | **Elevated** | **High** — each +55 bp of cap ≈ −6.5 % of value | Sell into the dislocation rather than after it | Now |
| R5 | **Brand retrenchment** — JACK SSS −4.2 % FY25, −7.4 % in Q4, units 2,168→2,115, Del Taco sold at a ~$470 m loss | Credit | **Observed, ongoing** | Medium–High | Price it in; prefer a corporate guaranty | Now |
| R6 | **Trade-area stagnation** — LA County pop −3.2 % since 2020; metro payrolls +0.10 %/yr over 7 yrs, −1.2 % from the Oct-2024 peak | Market | **Observed** | Medium | Underwrite zero real NOI growth | Now |
| R7 | **Wildfire / smoke / PSPS** — 2025: 8,232 CA wildfires, 16,627 structures lost, 4 LA County incidents ≥ 5,000 ac | Catastrophe | Medium (4 %/yr modelled) | Medium–High | Insurance covenant; exit | Verify FHSZ with address |
| R8 | **Seismic event** | Catastrophe | Low-Medium (3 %/yr modelled) | High (correlated, region-wide) | Retrofit status; insurance; diversification | Verify CGS seismic zone |
| R9 | **Insurance repricing / non-renewal** | Market | Medium (6 %/yr modelled) | Medium | Confirm who bears premium escalation | Verify lease insurance clause |
| R10 | **1031 execution failure** — miss 45/180 days, disqualified intermediary, or touch proceeds | Tax/process | Low–Medium | **Very high** (full tax acceleration) | QI engaged pre-closing; conservative timeline; verified QI | Engage QI early |
| R11 | **California tax on out-of-state replacement** | Tax | Medium if relocating capital | Medium | FTB 3840 undertaking; CA adviser opinion | **Unverified — confirm** |
| R12 | **Concentration** — one parcel, one tenant, one metro | Portfolio | Certain | High | Diversify via exchange into multiple assets | Structure the 1031 for ≥ 2 assets |
| R13 | **Ownership/entity issue** — entity form, step-up basis, estate plan | Legal | Unknown | Medium–High | Counsel | **Unverified** |
| R14 | **Environmental / ADA / entitlement** at re-leasing or redevelopment | Legal | Low | Medium | Phase I ESA; ADA survey | At exit diligence |
| R15 | **Measurement risk in this analysis** — no address, no lease, no rent | Model | **Certain** | Medium | Every assumption published; sensitivities shown | Supply the documents |

## 6.6 Black-swan stress test

Deterministic replay with a severe joint scenario (10-year Treasury to 6.90 %, zero rent growth, 25 % renewal probability, 4.5 % sale costs, land value 6.5× NOI):

| Strategy | Mean | vs sell-and-pay-tax |
|---|---|---|
| A1 · Sell now via §1031 | **11.83** | +14.7 % |
| D · Extend now, sell 2028 | 10.62 | +2.9 % |
| A · Sell now, pay tax | 10.32 | — |
| B · Hold to expiry, sell vacant | 9.89 | −4.2 % |
| C · Renew at expiry, hold to 2040 | **6.78** | **−34.3 %** |

**In the black-swan scenario, holding loses 34 % relative to selling.** The ranking does not flip. This is the robustness test that matters: the recommendation survives the bad state of the world, and it survives it *because* it removes exposure early.

Note also the **no-hazard control**: with catastrophe and default priors switched off, C rises to 11.33 and D to 11.29 — i.e. C's apparent attractiveness comes entirely from the benign half of the distribution. That is not a coincidence; it is the definition of tail risk.

## 6.7 Break-even: what would have to be true for holding to win?

| Terminal 10-yr Treasury | Implied cap-rate shift | Best strategy |
|---|---|---|
| 3.50 % | −77 bp | A1 · Sell now via 1031 |
| 4.00 % | −50 bp | A1 |
| 4.60 % (base) | −16 bp | A1 |
| 5.00 % | +6 bp | A1 |
| 5.50 % | +33 bp | A1 |
| 6.00 % | +60 bp | A1 |
| 6.50 % | +88 bp | A1 |
| 7.00 % | +116 bp | A1 |

**The recommendation is insensitive to the interest-rate path across a 350 bp range.** That is a strong result and it is worth stating plainly: *this is not a rates call.* Even if the 10-year fell back to 3.50 %, selling via §1031 still ranks first on a risk-adjusted basis, because the dominant term is the **term premium capture and the removal of single-asset tail risk**, not the discount rate.

Where the answer *does* flip is the **discount rate**: at 6 % the best strategy becomes D (extend, then sell). That is a coherent result — an Owner with a low opportunity cost of capital should keep the asset long enough to capture the extension premium rather than sell immediately.

## 6.8 What would make this recommendation wrong

Stated so the Owner can falsify it:

1. **The lease is absolute-net, corporate-guaranteed, with 3 % annual bumps and a tenant renewal option at market.** Then the asset is far better than modelled and the extension premium is even larger — which strengthens D, and strengthens "extend then sell", not "hold to expiry".
2. **The true expiry is 2035 and the true basis is much higher than assumed.** A high basis lowers the tax on sale to near zero, which *raises* A relative to A1 and makes selling outright even more attractive.
3. **There is a below-market-basis opportunity the model cannot see** — e.g. an estate-planning reason to hold until death for a basis step-up, or a specific buyer (the franchisee, or an adjacent owner) willing to pay a strategic premium well above market. The model assumes an arm's-length sale at market.
4. **NOI is materially higher than 13× the value implied by the cap curve** — i.e. the Owner bought at a much lower basis and the asset is worth far more than 12.5× current NOI. The model is scale-invariant, so the *ranking* survives, but the dollar stakes change.
5. **There is a genuine redevelopment play.** Central-LA infill drive-thru parcels can be worth more as land for housing under current state law (e.g. SB 6 / AB 2011 by-right ministerial review). **This is flagged unverified** — no parcel-level zoning, general-plan or transit-proximity analysis was possible without an address. If a rezoning or a development buyer is real, holding to expiry to preserve the redevelopment option could dominate everything above. **This is the single largest un-quantified upside in the analysis and it should be tested before executing the sale.**

## 6.9 Sources

- IRS, Topic No. 409 — Capital gains and losses (25 % unrecaptured §1250; 20 % top LTCG; NIIT): https://www.irs.gov/taxtopics/tc409
- IRS, Like-Kind Exchanges Under IRC §1031 (45-day / 180-day rules; QI requirement): https://www.irs.gov/newsroom/like-kind-exchanges-under-irc-code-section-1031
- IRS, Like-kind exchanges — real estate tax tips (current guidance): https://www.irs.gov/businesses/small-businesses-self-employed/like-kind-exchanges-real-estate-tax-tips
- FRED — 10-year Treasury (`DGS10`), 30-year mortgage (`MORTGAGE30US`), fed funds (`DFF`), CPI (`CPIAUCSL`)
- The Boulder Group — Q3 2026 net-lease cap rates and Q2 2026 sector detail (Tier 3)
- CAL FIRE — 2025 incident archive
- Census Bureau — QuickFacts, LA County & city
- FRED — LA metro payrolls, LA County unemployment
- SEC EDGAR — Jack in the Box Inc. FY2025 Form 10-K and FY2026 Q3 results
