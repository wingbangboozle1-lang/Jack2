# Executive Summary — Central Los Angeles Single-Tenant Jack in the Box NNN Asset (`2030–2035` Expiry)

**Workspace:** `session-7663f9db` · **Verification Date:** `2026-11-12` · **Privacy Status:** Strict Zero-PII (subject address, APN, and owner identity withheld; all unverified owner terms left blank and calculations normalized per `$1.00` NOI).

## 1. Bottom-Line Decision Verdict
**Do not make an unexamined hold or rush into an unpriced sale today.** Live primary filings verified on November 12, 2026 materially alter prior repository conclusions:
1. **Tighter NNN Reinvestment Spreads:** The 10-Year U.S. Treasury par yield jumped to **4.98%** (Nov 10, 2026), while institutional benchmark **Realty Income (NYSE: O)** deployed $2.6B in Q3 2026 at a **6.80%** initial weighted-average cash yield (Nov 2, 2026 Form 8-K)—down **50 bps** from FY2025's 7.30% assumption hardcoded in older repo models.
2. **Tighter Breakeven Cap Rates:** Switching via IRC §1031 is immediately Year-1 cash-accretive only if the Central LA pad sells at or below **6.59%** (Sub-$5.4M / 0.56% DTT), **6.32%** (Measure ULA Tier 1 / 4.56% DTT), or **6.22%** (ULA Tier 2 / 6.06% DTT)—though multi-year **6-year NPV breakevens widen to 8.06% / 7.27% / 6.98%** once short-WALT cap expansion (+85 bps) and re-leasing downtime are priced in.
3. **Optimal Two-Track Action:** Execute a 30-day Confidential Data Pack (exact expiry, tenant guarantor entity, City vs. County ULA check, tax basis, dual BOVs), then follow the quantitative split:
   - **Track A (High-Sales Infill / Measure ULA Parcel):** Pursue a **confidential 10–15 year Blend-and-Extend** first (median normalized NPV **17.88x**, lifting valuation +12% to +22% without triggering immediate 4.56%–6.06% transfer tax) before deciding to hold or sell.
   - **Track B (Short WALT <= 5.5 yrs, Sub-AUV Store, Weak Franchisee, or Non-ULA Sale <= 6.25% Cap):** Execute a **targeted IRC §1031 exchange** into diversified investment-grade NNN or Treasuries/balanced index if gain ratio <= 25% (outperforms Hold **98.7%** in BAU and **99.8%** in Black Swan stress at Sub-$5.4M).

## 2. Live 2026-11-12 Verified Market & Regional Scorecard
- **Capital Markets:** 10Y Treasury **4.98%** (Nov 10); 30Y **5.35%**; Fed funds upper **4.00%**; Realty Income Q3-26 cash yield **6.80%** (182 bps spread).
- **Tenant (JACK Q3 FY26 & Sep 21, 2026 8-K):** **2,115 units** (93.0% franchised, FY26 guide ~2,100 with 50–60 closures), Q3 SSS **-1.1%**, Q3 Adj. EBITDA **$61.2M**, total debt **$1,472.83M** ($500M May 2031 ARD notes), stockholders' deficit **($901.29M)**, dividend/buybacks suspended, Del Taco sold Dec 2025 ($115M), Board/GreenWood agreement & CEO succession announced Sep 21, 2026.
- **LA Macro & Demographics:** Census V2025 City **3,869,089 (-0.8%)** / County **9,694,934 (-3.2%)**; CA DOF P-2A projects LA County **9,811,358 (2026) -> 9,637,524 (2040, -1.77%)**; BEA 2024 personal income **$818.5B (#1 US)**; City **57.3% rent-burdened**; BLS Sep 2026 LA Metro nonfarm **+0.5% YoY**, County SA unemp **4.8%**; Sep CPI **+3.7%**; AB 1228 fast food floor **$20.00/hr**; Metro D Line Section 1 **opened May 8, 2026**; Port of LA Sep record **1,042,652 TEUs**.
- **Schools (Newly Resolved):** LAUSD **497,105 enrollment (#1 CA)** achieved **87.6% graduation (+1.1%)** and **58.0% C/C prepared** on the **2026 California School Dashboard** (`86.9% SED`).
- **Taxes & Elections:** Measure ULA post-6/30/2026 **4.45% (>$5.4M) / 5.95% (>=$10.9M)** + **0.11% County DTT**; Federal LTCG 20% + Sec. 1250 25% + NIIT 3.8% + CA **13.30%**; Nov 11 SOS canvas shows **Prop 3 (60.7% Yes)** locking top CA brackets & **Prop 43 (57.4% No)** preserving majority-vote local transfer-tax initiatives.
- **Hazards:** Jan 2025 Eaton/Palisades fires caused **$5.2B–$10.1B** lost output and a **$1.0B** CDI FAIR Plan assessment; USGS UCERF3 estimates **60% M>=6.7 (3.01%/yr)** and **46% M>=7.0** 30-year quake odds.

## 3. Repository Audit Highlights (`flagged.html`)
- Caught **HTTP 404** on legacy CAL FIRE `-2022` FHSZ URL in root `data/sources.json (S17)`, `origin/main:suggestions.html`, and 3 legacy folders (`session-6d8f5d05`, `18dacdea`, `d9c94ed0`); replaced with live OSFM FHSZ portal `[S28]`.
- Caught Sep 2026 BLS unemployment misprints (`5.1/4.3/5.6/5.9%` vs. actual `4.4/4.0/5.1/4.5%`) and CI omission in `session-6d8f5d05`.
- Caught stale `7.3%` yield in root `tools/model.py` and `data/valuation.json`.
- Caught street-address regex match in `research/04-education.md:11` (LAUSD HQ) and CI cross-PR contention in `session-f4f700c0/scripts/audit.py`.
