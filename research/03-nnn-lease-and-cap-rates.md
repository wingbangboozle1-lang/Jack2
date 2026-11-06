# 03 — NNN Lease Mechanics, Cap-Rate Pricing and the Interest-Rate Regime

---

## 3.1 The pricing identity this whole analysis rests on

For a single-tenant net lease, value is a ratio:

```
Value  =  NOI  ÷  Cap Rate
```

Only two things can happen to value: **NOI** moves, or the **cap rate** moves. Everything else in this report is an argument about which of those two is more likely to move, in which direction, and when. That framing is what makes the decision tractable.

Two structural features of *this* asset make the cap rate the dominant variable:

1. **NOI is contractually fixed** (a NNN lease with no landlord capital obligations). The landlord has almost no lever to raise it before expiry.
2. **Remaining term feeds directly into the cap rate.** Net-lease buyers pay for durability of cash flow. A given NOI is worth more with 15 years of contract left than with 4. This is the "term premium," and it decays every month.

## 3.2 Verified capital-markets environment (as of 2026-11-06)

| Metric | Value | As of | Source | Tier | Status |
|---|---|---|---|---|---|
| 10-year U.S. Treasury constant maturity | **4.90 %** | 2026-11-04 | FRED `DGS10` | T1 | verified |
| 10-year Treasury, daily peak in 2026 | 5.31 % | 2026-10-05 | FRED `DGS10` | T1 | verified |
| 10-year Treasury, monthly average | **5.13 %** | Oct 2026 | FRED `GS10` | T1 | verified |
| 10-year Treasury, monthly average | 4.06 % | Oct 2025 | FRED `GS10` | T1 | verified |
| 10-year Treasury, monthly average | 0.62 % | Jul 2020 (cycle low) | FRED `GS10` | T1 | verified |
| 10-year Treasury, monthly average | 2.14 % (2019 average of monthly averages) | CY2019 | FRED `GS10` | T1 / D | verified / derived |
| 30-year fixed mortgage | **7.18 %** | week of 2026-11-05 | FRED `MORTGAGE30US` (Freddie Mac) | T1 | verified |
| 30-year fixed mortgage | 6.16 % | week of 2026-01-08 | FRED `MORTGAGE30US` | T1 | verified |
| Effective federal funds rate | **3.88 %** (raised from 3.64 % on 2026-09-17) | 2026-09-25 | FRED `DFF` | T1 | verified |
| CPI-U, all items, SA | 336.298 | Sep 2026 | FRED `CPIAUCSL` (BLS) | T1 | verified |
| CPI-U, all items, SA | 324.245 | Sep 2025 | FRED `CPIAUCSL` | T1 | verified |
| **CPI inflation, year over year** | **+3.72 %** | Sep 2026 | Derived from `CPIAUCSL` | D | verified/derived |

### What the series say
- The 10-year has risen from **4.06 % → 5.13 %** on a monthly-average basis in twelve months, and printed **5.31 %** on 2026-10-05.
- The Fed **stopped cutting and reversed**: 4.33 % (May 2025) → 3.64 % (Dec 2025) → held for eight months → **hiked to 3.88 % on 2026-09-17**.
- 30-year mortgage rates went **6.16 % → 7.18 %** during 2026.
- Inflation is **re-accelerating** at +3.72 % YoY.

This is not a "wait for rate cuts" environment. It is the opposite. The Boulder Group's Q3 2026 report makes the same call from the transaction side: net-lease pricing is *"resetting to a higher cost of capital rather than waiting for relief,"* with the Fed projecting a **4.1 % federal funds rate by year-end** — i.e. further tightening, from 3.88 % today.

## 3.3 Cap-rate evidence (Tier 3 — industry source, not government)

**Source: The Boulder Group, *Single Tenant Net Lease Research Report*, Q2 2026 and Q3 2026; *Net Lease Tenant Profiles*, Q3 2026.** These are brokerage research publications. They are the best available *market* pricing signal and are **not** official statistics. Every row is badged accordingly on the site.

| Segment | Cap rate | Period | Status |
|---|---|---|---|
| **All single-tenant net lease** | **6.92 %** (up from 6.82 % in Q2 2026) | Q3 2026 | T3 verified |
| Retail STNL | 6.60 % | Q2 2026 | T3 verified |
| Industrial STNL | 7.25 % | Q2 2026 | T3 verified |
| Office STNL | 7.90 % | Q2 2026 | T3 verified |
| Auto STNL | 6.45 % | Q2 2026 | T3 verified |
| Dollar store STNL | 7.49 % | Q2 2026 | T3 verified |
| Drug store STNL | 7.85 % | Q2 2026 | T3 verified |
| **QSR — corporate credit** | **5.85 %** | Q2 2026 | T3 verified |
| **QSR — franchisee credit** | **6.85 %** | Q2 2026 | T3 verified |
| Bid–ask spread, retail | 25 bp (widened from 22 bp) | Q3 2026 | T3 verified |
| McDonald's / Chick-fil-A ground lease (sector tightest) | 4.45 % | Q2 2026 | T3 verified |
| Raising Cane's, 15-year | 4.90 – 5.20 % | Q3 2026 | T3 verified |
| Whataburger, 15-year | 4.85 – 5.25 % | Q3 2026 | T3 verified |
| 7-Eleven, 5-year | 5.90 – 6.20 % | Q3 2026 | T3 verified |
| 7-Eleven, 15-year | 4.80 – 5.15 % | Q3 2026 | T3 verified |
| Burger King, 10-year | 6.30 – 6.60 % | Q3 2026 | T3 verified |
| Applebee's, 15-year | 7.15 – 7.45 % | Q3 2026 | T3 verified |
| Family Dollar, 5-year | 8.50 – 8.90 % | Q3 2026 | T3 verified |
| **Jack in the Box, any term** | **not retrieved** | — | **unverified — flagged** |

### The four facts that matter most from this table

1. **Corporate vs franchisee QSR is a ~100 bp spread** (5.85 % vs 6.85 %). If the Subject Property's tenant is a franchisee without a corporate guaranty, its pricing anchor is the 6.85 % line, not the 5.85 % line.
2. **Term is worth a lot.** 7-Eleven 5-yr prices 5.90–6.20 %; the same credit at 15-yr prices 4.80–5.15 %. That is **~105 bp of pure term premium on identical credit** — roughly **17 %** more value for the same NOI.
3. **Brand weakness is priced brutally and fast.** Burger King at 10-yr (6.30–6.60 %) already sits well inside the franchisee-QSR average despite investment-grade-adjacent scale. Family Dollar moved from investment grade to unrated and repriced instantly to 8.50–8.90 % at 5-yr.
4. **The market is bifurcating, not falling.** Long-term premium credit trades tight; short-term and unrated product trades wide. The Subject Property sits firmly on the **short-term, unrated** side of that line today — and will sit further out on it every year it is not extended.

## 3.4 The term-premium curve used by this model

Because no JACK-specific cap rate was verifiable, the model **derives** a term curve from the Boulder QSR data points and labels the output **D (derived)**. The construction is explicit so it can be challenged:

| Remaining term | Model cap rate | Anchor / reasoning |
|---|---|---|
| 15+ years | **6.40 %** | Boulder franchisee-QSR average 6.85 % less ~45 bp for full-term durability; JACK is not a premium-credit brand (Raising Cane's / Whataburger at 15-yr price 4.85–5.25 %, and JACK is materially weaker than either) |
| 10 years | **6.85 %** | Boulder **franchisee QSR** average, Q2 2026 (direct anchor) |
| 7 years | **7.75 %** | +90 bp short-term premium to the 10-yr anchor |
| ≤3 years | **9.00 %** | "Meaningfully wider" per Boulder; assets near expiry become re-leasing projects |
| Vacant / no lease | **10.50 %** | Assumption A — vacant single-tenant retail is priced on land + re-leasing cost |

*Every number in this table is a **model assumption anchored to a T3 observation**, not a verified market quote for `PROP-001`.*

## 3.5 NNN lease features that are worth real money and are unverified here

| Feature | Value impact | Direction for this asset |
|---|---|---|
| **Escalations** — none / 1 % / 2 % / CPI | A flat lease loses ~3.7 %/yr in real terms at current CPI. A 10-year flat lease has lost ~30 % of purchasing power by the end. | **unknown — critical** |
| **Renewal options held by tenant at fixed rent** | Caps landlord upside; depresses sale value because the buyer cannot mark rent to market | **unknown — critical** |
| **Landlord-held extension option** | Increases value (controlled upside) | **unknown** |
| **Guaranty** (corporate vs franchisee vs personal) | ~100 bp of cap rate; ~15 % of value | **unknown — critical** |
| **Absolute-net vs roof/structure carve-out** | 0.15–0.30 % of value/yr in reserved capex | **unknown** |
| **Early-termination / kick-out right** | Converts a "leased" asset into an option the tenant owns | **unknown** |
| **Co-tenancy / radius restrictions** | Affects re-leasing pool post-expiry | **unknown** |
| **Assignment & subletting consent standard** | Affects liquidity of the tenant's position | **unknown** |

## 3.6 The expiry question, stated as arithmetic

Remaining term on 2026-11-06 depending on the true expiry date:

| Assumed expiry | Remaining term | Model cap rate (§3.4) | Value per $1.00 of NOI | Value vs. 2035 expiry |
|---|---|---|---|---|
| 2030-12-31 | 4.15 yr | 8.64 % (interpolated 3-yr→7-yr) | $11.57 | −17.8 % |
| 2032-12-31 | 6.15 yr | 8.02 % (interpolated) | $12.48 | −11.3 % |
| 2035-12-31 | 9.15 yr | 7.10 % (interpolated 7-yr→10-yr) | $14.07 | — |

**Read this carefully:** the Owner's uncertainty about the expiry date is worth **$2.50 of value per $1.00 of annual NOI** — on a $200,000-NOI asset that is **$500,000**, or **21.6 %** of the 2030-date value. Resolving the expiry date is the highest-return, lowest-cost action available, and it costs nothing but reading the lease.

## 3.7 Sources

- FRED `DGS10` — 10-Year Treasury Constant Maturity: https://fred.stlouisfed.org/series/DGS10
- FRED `GS10` — 10-Year Treasury, monthly average: https://fred.stlouisfed.org/series/GS10
- FRED `MORTGAGE30US` — 30-Year Fixed Rate Mortgage Average (Freddie Mac): https://fred.stlouisfed.org/series/MORTGAGE30US
- FRED `DFF` — Effective Federal Funds Rate: https://fred.stlouisfed.org/series/DFF
- FRED `CPIAUCSL` — CPI-U All Items (BLS): https://fred.stlouisfed.org/series/CPIAUCSL
- The Boulder Group, *Net Lease Report Q2 2026*: https://www.bouldergroup.com/blog/
- The Boulder Group, Q3 2026 net-lease cap rates at 6.92 % (press release, 2026-10-09): https://www.financialcontent.com/article/abnewswire-2026-10-9-the-boulder-group-reports-net-lease-cap-rates-rise-to-692-in-q3-2026
- The Boulder Group, *Q3 2026 Net Lease Tenant Profiles* (88 operators): https://www.openpr.com/news/4629798/the-boulder-group-releases-q3-2026-net-lease-tenant-profiles
