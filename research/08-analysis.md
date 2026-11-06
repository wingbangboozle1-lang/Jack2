# Research Notes — T8: Analysis: decision framework, risk matrix, projection system

All factual inputs are sourced in research notes 02–07. Everything below that is derived (computed, weighted,
or recommended) is labeled ANALYSIS. Cap-rate assumptions are illustrative sensitivity bands, NOT official data —
no official source publishes cap rates; they are flagged accordingly on the site.

## 1. Decision options considered
| Option | Description |
|---|---|
| A. Sell now (2026–2027) | Market the property with the remaining ~4–9 years of NNN lease term. |
| B. Renew/extend first, then hold or sell | Negotiate an early extension (target ≥10 years, CPI-banded escalations) while the tenant still has renewal incentive; then either keep the income stream or sell with a long WALT (weighted-average lease term). |
| C. Hold through expiry without renewal | Collect rent until 2030–2035 expiry; accept vacancy/rollover risk at expiration. |
| D. Sell via §1031 exchange | Variant of A or B: exchange into another investment property to defer federal gain and CA gain (CA taxes capital gains as ordinary income — FTB). |
| E. Redevelop/reposition | Redeem central-LA land value via redevelopment (as-of-right depends on zoning — unverified pending parcel data). |

## 2. Verified factual drivers (with sources in other notes)
1. Tenant system is contracting: 86 JIB closures FY2025 vs 25 in FY2024; "JACK on Track" targets ~150–200
   closures (company IR 2025-04-23; SEC 10-K FY2025). Same-store sales −3.7% FY2025.
2. Tenant financial stress: net losses FY2024 (−$36.7M) and FY2025 (−$80.7M); stockholders' deficit −$938.3M;
   dividend eliminated; Del Taco sold (closed 2025-12-22) to pay debt (SEC filings).
3. But the lease is contractual NNN: fixed rent with cost-of-living adjustments plus taxes/insurance (10-K Item 2),
   and JACK states it has "generally been able to renew our restaurant leases as they expire at then-current
   market rates." 93% of JIB restaurants are franchised; CA is the brand's core (941 units; ~70% of system in CA+TX).
4. Area demand is stable-to-growing long-term: SCAG projects LA County households +22.5% by 2050 (+1.0%/yr to 2030),
   employment +8.6%, population +7.4%. Near-term Census PEP shows LA city population −0.8% (2020–2025).
5. Inflation supports CPI-linked rent escalations: LA CPI +3.7% YoY (Sept 2026); 12-mo prints 2.9–3.7% through 2026.
6. Labor-cost pressure on the tenant's unit economics: $20/hr fast-food wage (AB 1228) drove ~7.6% wage inflation
   in JACK's CA-exposed company restaurants in FY2025 (10-K).
7. Hazard tail risks are material and quantified: 60% chance of M≥6.7 quake in LA region within 30 years (USGS);
   January 2025 fires destroyed ~16,264 structures and triggered a $1B FAIR Plan assessment, the first in 30+ years
   (CAL FIRE; CDI Bulletin 2025-4) — insurance cost hardening is a statewide carry-cost risk.
8. Education (LAUSD) is mid-tier but improving (Dashboard 2024) — neutral-to-positive for area residential stability.

## 3. Projection system (transparent model)
- NOI_t = Current annual rent × Π(1+escalation), escalation scenarios = CPI bands: Low 2.0% / Base 3.0% / High 3.7%
  (anchored to LA CPI range; BLS).
- Value_t = NOI_t ÷ exit cap rate. Sensitivity grid 4.50%–7.25%. (Illustrative band; flagged non-official.)
- Growth offsets: +3%/yr rent for 5 years = +15.9% value at constant cap; a cap move 5.25%→6.25% = −16.0%.
  → Cap-rate risk dominates rent growth over short horizons.
- Computed multiples: 4.50%→22.22x NOI; 5.00%→20.00x; 5.75%→17.39x; 6.50%→15.38x; 7.25%→13.79x.
- Scenario per $100k NOI (illustrative caps only): Sell now @5.75% = $1.739M; Renew now, sell yr-3 @5.25% = $2.081M;
  hold to expiry, sell vacant yr-5 @7.25% = $1.599M.
- Area-demand projections: SCAG LA County households +1.0%/yr to 2030; employment +0.27%/yr to 2050.

## 4. Risk matrix (ANALYSIS; likelihood × impact rated qualitatively from the verified facts above)
| Risk | A. Sell now | B. Renew then hold/sell | C. Hold to expiry | D. 1031 variant | E. Redevelop |
|---|---|---|---|---|---|
| Tenant non-renewal / closure program reaches this site | Eliminated at closing | Low (extension locked; but renewed tenant credit risk persists) | HIGH at expiry | Eliminated (if exchanged) | Eliminated |
| Cap-rate / interest-rate expansion | Low-moderate (immediate pricing) | Moderate at later exit | High (short WALT pricing) | Low-moderate | High |
| Rent-growth capture | Forgone | Full (CPI-banded) | Partial (fixed escalations to expiry) | Depends on replacement | N/A |
| Tax friction (fed LTCG + CA ordinary-income treatment) | Immediate | Deferred until later sale | Deferred | Deferred (§1031; CA clawback via FTB 3840 if moving out of state) | Deferred via development |
| Vacancy/downtime & re-lease costs | None | None | High (downtime, TI/LC, dark-value discount) | None | Construction/lease-up risk |
| Earthquake damage (60% M≥6.7 / 30 yr) | Transfers to buyer | Retained (insurance review critical; NNN shifts property insurance to tenant but gap/QUAKE coverage decision remains) | Retained | Retained on replacement | Retained |
| Insurance-market hardening (post-2025 fires) | Largely transfers | Shared (NNN pass-through as leases allow) | Retained | Shared | Retained |
| Liquidity / buyer pool | Broad now (NNN fast-food with term) | Broadest with long WALT + decent credit | Narrow (short WALT) | Broad | Narrow (developer/spec) |
| Execution complexity | Low | Moderate (negotiation) | None | Moderate (45/180-day rules, QI) | High (entitlement risk) |
| Black swan exposure window | Minimal | Extended by choice | Longest | Extended by choice | Longest |

Black-swan register (business-as-usual vs tail): earthquake (quantified: 60%/30yr M≥6.7 — USGS), wildfire/insurance
cascade (2025 precedent: $1B FAIR Plan assessment; ~$4B FAIR Plan losses from Palisades+Eaton; ~$40B industry-wide
per NAIC CIPR estimate), pandemic-style demand shock (COVID precedent: region lost 1.9M jobs Feb–May 2020, L&H
employment fell ~54% then recovered — SCAG), civil unrest (1992 precedent, unquantified), severe recession
(SCAG unemployment series: 12.5% in 2010, 17.3% pandemic peak).

## 5. Decision logic (recommendation — ANALYSIS)
Primary recommendation: **Option B first (renew/extend), with a hard fallback to Option A/D (sell via §1031)
if renewal cannot be secured on market-competitive terms by the decision deadlines below.** Reasoning:
1. Value driver hierarchy for single-tenant NNN: WALT × tenant credit × cap rate. The verified tenant-credit
   trajectory is deteriorating (closures, losses, negative equity) while the area's long-run demand is stable
   (SCAG). The cheapest way to restore value is an early renewal — it extends WALT without waiting, and JACK's
   own 10-K says it generally renews at market rates.
2. Rent is CPI-linked; LA CPI is running ~3-3.7% — holding captures escalation compounding that a sale forfeits,
   but only while the tenant pays; hence pair the extension with a credit-quality check of WHO signs (corporate
   JACK vs franchisee — placeholder pending lease abstract).
3. If renewal is refused or terms are below-market: sell while ≥5–7 years of term remain (before the market
   starts pricing rollover risk), structured as a §1031 exchange to defer federal + California gain
   (CA has no preferential capital-gains rate — FTB).
4. Never hold through expiry without a renewal plan (Option C): a vacant single-tenant fast-food box in a
   high-rate environment is the worst combination of the risk matrix (short WALT pricing + downtime + re-lease
   cost + tenant-credit backdrop).
5. Risk balance for the owner as an individual: concentrate no more than necessary in one tenant/one asset
   whose credit is deteriorating; if risk tolerance is low or estate/liquidity needs are near, the sell-now
   (A/D) branch dominates; if comfortable with contractual income, B-then-hold with an earthquake-insurance
   review and an exit checkpoint at each 5-year WALT threshold is the balanced path.

Decision deadlines by expiry year (placeholder expiry window 2030–2035):
- If expiry 2030–2031: begin renewal talks immediately; if no signed extension within 12–18 months, list for
  sale with ≥4–5 years remaining (2026–2027 window).
- If expiry 2032–2033: renewal talks by 2027; sale fallback window ~2028–2029.
- If expiry 2034–2035: renewal talks by 2028–2029; sale fallback window ~2030–2031; reassess annually.

Watch-list triggers that should accelerate the sell branch (any two): (a) this location enters a closure
announcement or goes dark; (b) tenant/franchisee financial deterioration (bankruptcy filings, rent delinquency);
(c) same-store sales trend remains negative >8 quarters; (d) LA CPI-linked escalations capped/frozen in renewal
offer; (e) insurance/property-tax pass-through disputes; (f) cap-rate environment >6.5% for comparable NNN assets
(non-official market observation — verify with broker opinions at decision time).

## 6. Preservation-of-wealth & growth balance (ANALYSIS)
- Preservation levers: §1031 deferral (IRS), Prop 13 tax basis is retained while holding (BOE), NNN pass-through
  structure (tenant bears taxes/insurance/maintenance per 10-K lease description), earthquake insurance decision
  (USGS probabilities justify explicit decision, not default).
- Growth levers: CPI-banded escalations (~3%/yr base case), long-run area household growth (+1.0%/yr to 2030 —
  SCAG), optionality of redevelopment (central LA zoning pending verification), LA28 Olympics demand catalyst 2028
  (official Games in LA — noted qualitatively; SCAG plans regionally for LA28).
- Manageable-risk profile = extended WALT + explicit quake/insurance review + staged exit checkpoints + no
  over-concentration (exchange into diversified multi-tenant if selling).
