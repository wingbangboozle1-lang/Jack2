# Executive Summary — Central Los Angeles Jack in the Box (NNN Lease Expiring 2030–2035): Sell Before Expiry vs. Renew

**Session:** `session-18dacdea` (`arena/18dacdea-jack2`) | **Verification Date:** `2026-11-07`  
**Live Dashboard URL:** `https://wingbangboozle1-lang.github.io/Jack2/session-18dacdea/`  
**Subject Asset:** `[REDACTED-PROPERTY-01]` — Single-Tenant Jack in the Box Restaurant, Triple-Net (NNN) Lease (`[REDACTED-LEASE-01]`) expiring in the **2030–2035** window, Central Los Angeles, CA  
**Owner:** `[REDACTED-OWNER-01]`

---

## 1. Personal Information Privacy Mandate (Highest Priority & Urgency)

- **Zero Personal or Parcel Identifiers Published:** Every personal, owner, taxpayer, loan, and parcel-identifying detail is anonymized using strict placeholders (`[REDACTED-PROPERTY-01]`, `[REDACTED-OWNER-01]`, `[REDACTED-LEASE-01]`, `[REDACTED-EMAIL-01]`).
- **Internal-Only Rule Enforced in Code:** Automated build-time and CI regex scanners (`session-18dacdea/scripts/verify.py` and root `tools/check_site.py`) scan 100% of HTML and JSON files for email addresses, phone numbers, street addresses, and Assessor Parcel Numbers (APNs), failing the build on any match.
- **No Unverified Value Inference:** Twelve parcel-specific or private fields (street address/APN, exact lease expiration date, current contract rent/NOI, lease guarantor entity, option schedule, NNN structural carve-outs, unit gross sales, municipal boundary, owner tax basis/debt, and parcel-level FEMA/CAL FIRE/CGS/GeoTracker hazard lookups) cannot be confirmed from public official records without exposing or guessing private data. Every one of those 12 cells is left **strictly blank (`""`)** and published on `flagged.html`.
- **100% Browser-Local Private Simulator:** To allow `[REDACTED-OWNER-01]` to test exact dollar figures safely, `projection-model.html` includes a client-side calculator that runs entirely in browser memory with zero network calls, cookies, or storage.

---

## 2. Executive Recommendation: The Optimal Decision for Wealth Preservation & Growth

**Recommended Strategy — Two-Stage "Early Blend-and-Extend Inquiry (2026–2027) -> Pre-Cliff IRC §1031 Exchange Disposition (2027–2028)":**

1. **Stage 1 (Next 90 Days — Audit & Early Blend-and-Extend Inquiry):** Audit the executed lease (`[REDACTED-LEASE-01]`) for exact expiration date (`M-02`), store gross sales (`M-07`), and guarantor entity (`M-04`). Approach the tenant (`Jack in the Box Inc.` / franchisee) now—while **4 to 9 years of primary term remain**—to offer an early **10-to-15-year Blend-and-Extend** resetting remaining lease term to 12–15 years with CPI-collared step-ups (2.0%–3.5%/yr).
   - *Why:* Per `NNN REIT, Inc.`'s SEC Form 10-K (`S13`), occupied net-lease retail dispositions with ~10.2-year WALT trade at a **6.4% cap rate**, whereas shorter-WALT assets trade ~55–155 bps wider (**6.95%–7.95%**). Extending the lease from ~6 years (2032 midpoint) to 14–15 years compresses the exit cap rate from **6.95% to 6.40%**, generating **+13.3% (+$191,187 per $100k NOI)** in immediate property value before selling.
2. **Stage 2 (Execute Pre-Cliff IRC §1031 Exchange While >=6 Years of Term Remain):** Whether the tenant signs the early extension (Stage 1A) or declines within 90 days (Stage 1B fallback), **sell the property via an IRC §1031 Like-Kind Exchange (`S19`) before remaining lease term drops below 6.0 years** (i.e., sell in 2027–2028 if expiry is 2032–2035, or **sell immediately in Q1 2027 if expiry is 2030–2031**).
   - *Why:* Once remaining primary term falls below ~6 years, commercial lenders restrict 10-year amortizing debt, shrinking the buyer pool to cash/value-add buyers and expanding cap rates by 75–175 bps. Rotating 100% of pre-tax equity via IRC §1031 (avoiding the **~35.5%–37.1%** combined Federal LTCG + NIIT + §1250 Recapture + California 13.3% tax hit, `S19`) into 2–3 diversified net-lease replacement properties yielding **7.10%–7.40%** (`S13`, `S14`) maximizes both **expected 2040 wealth ($3.82M mean per $100k NOI)** and **5th-percentile tail protection ($3.35M P05 floor vs. $2.66M for passive hold)**.
3. **What NOT to Do:**
   - **Never hold passively into the final 1–3 years of the lease (`S4`):** Suffers maximum WALT cap-rate expansion (~8.15%+) and exposes 100% of principal to tenant non-renewal.
   - **Never execute an outright taxable sale without §1031 (`S5`):** Permanently forfeits ~26.5%–37.1% of asset equity to Federal and California taxes on day one.

---

## 3. Quantitative Strategy Comparison (Normalized per $100,000 of Current NNN NOI)

*Source: `session-18dacdea/scripts/model.py` (Deterministic 2026–2040 Base Case + 15,000-Trial Monte Carlo Simulation, `seed = 20261107`).*

| Rank | Strategy | Base 2026 NPV | 2040 Mean Wealth | 2040 Median (P50) | P10 Downside | P05 Tail Floor | Certainty Equiv. (CRRA=2.5) | Verdict |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| **1** | **S2: Early Blend-and-Extend (2026–27) -> §1031 Sale (2027–28)** | **$1,829,012** | **$3,822,165** | **$3,816,743** | **$3,441,517** | **$3,354,931** | **$3,798,208** | **RECOMMENDED PRIMARY** |
| **2** | **S1: Sell Pre-Cliff Now via IRC §1031 Exchange** | **$1,698,668** | **$3,696,913** | **$3,692,002** | **$3,335,286** | **$3,254,006** | **$3,670,763** | **IMMEDIATE FALLBACK** |
| **3** | **S3: Hold Through 2030–35 Expiry & Renew to 2040** | **$1,558,741** | **$3,454,245** | **$3,522,084** | **$2,843,098** | **$2,659,459** | **$3,361,449** | **CONDITIONAL HOLD** |
| **4** | **S4: Hold to Expiry Year (2030–35), Sell Unextended** | **$1,365,302** | **$2,915,215** | **$2,924,557** | **$2,315,786** | **$2,126,708** | **$2,832,395** | **AVOID (TERM DECAY)** |
| **5** | **S5: Sell Now Outright (Taxable Cash Sale)** | **$1,047,853** | **$2,181,680** | **$2,178,434** | **$1,981,731** | **$1,936,340** | **$2,168,195** | **AVOID (TAX EROSION)** |

---

## 4. Key Official Data Findings (Verified Line-by-Line on 2026-11-07)

1. **Fresh November 4, 2026 BLS Los Angeles Economic Summary (`S01`, `S02`):**
   - **Unemployment Improved YoY:** In September 2026, unemployment fell to **4.4%** in the LA Metro (vs 5.5% Sep 2025), **4.5%** in LA County (vs 5.9%), and **4.5%** in LA City (vs 5.9%), outperforming California (**5.1%**) though remaining above the U.S. (**4.0%**).
   - **Modest Payroll Growth (+0.5% YoY) with Sharp Sectoral Divergence:** Total MSA nonfarm employment reached **6,282.1k** in Sep 2026 (**+30.2k / +0.5% YoY** vs +0.3% U.S.). Growth is overwhelmingly driven by **Education & Health Services (+49.1k / +3.8%)** and **Leisure & Hospitality (+11.5k / +1.5%)**, while white-collar **Information (-11.4k / -5.7%)**, **Financial Activities (-5.1k / -1.7%)**, **Manufacturing (-5.4k / -1.2%)**, **Government (-8.4k / -1.1%)**, and **Professional Services (-5.2k / -0.5%)** contracted.
   - **Sticky Inflation (+3.7% CPI) & Energy Spike (+20.3% YoY):** Sep 2026 LA CPI-U rose **+3.7% YoY** (Food **+2.8%**, Energy **+20.3%**), while the LA Employment Cost Index (wages & salaries) accelerated to **+3.9% YoY** (Pacific private employer compensation **$55.49/hr**).
2. **Geography, Demographics, Income & Schools (`S03`–`S08`):**
   - **Dense Urban Core vs. Mild County Outflow:** City of LA population is **3,869,089** (`-0.8%` from 2020 to 2025 vs `-3.2%` across LA County's **9,694,934** residents, `S03`) with **8,304.2 persons/sq mi** (88.5x U.S. density) and a **30.7-minute** average commute supporting 24-hour drive-thru traffic. Official CA DOF P-2A projections (`S04`) model LA County gently declining from **9,853,435 (2025)** to **9,727,305 (2030)**, **9,708,647 (2035)**, and **9,637,524 (2040)** (`-2.2%` over 15 years).
   - **Income & Spending Depth:** Median household income is **$81,939** in LA City and **$90,112** in LA County (`S03`), per capita income is **$47,685** (City) / **$45,792** (County), and LA County ranks **#1 among all 3,116 U.S. counties** with **$818.5 billion** in total personal income (`S06`). Yet **16.5% City poverty** (`S03`) makes value-menu QSR traffic price-sensitive.
   - **School Systems (`S07`, `S08`, `S05`):** LAUSD enrolls **497,105 students** in 2025–26 (#1 in CA; **16.4%** English Learners) with an official CDE DataQuest 2024–25 four-year cohort graduation rate of **86.2%** (`S08`, vs **90.6%** LA County and **91.5%** CA), while CA DOF projects a **-240,800 student** county K-12 decline over 10 years (`S05`).
3. **Tenant Credit & Labor Pressure (`S09`–`S12`):**
   - **Statutory Wage Floor:** California's AB 1228 fast-food minimum wage is **$20.00/hr** (`S09`, +25% over prior base), above the newly verified **$18.42/hr** City of LA minimum wage effective July 1, 2026 (`S10`) and **$16.90/hr** state floor (`S09`).
   - **Jack in the Box (`JACK`) SEC Filings (`S11`, `S12`):** System restaurant count fell to **2,115 units** at Q3 FY2026 (ended July 5, 2026; **93% franchised**; **44.1% in California**). Same-store sales declined **-4.2% in FY2025** and **-4.2% YTD Q3 FY2026** (`-1.1%` in Q3 FY26); franchise AUV fell **-3.8%** to **$1,874k**; company store margins compressed from **21.7% (FY24)** to **19.6% (FY25)**; and management guided **50–100 closures in FY2026** following **86 closures in FY2025** under its `'JACK on Track'` restructuring. Consolidated debt stands at **$1,472.83M** plus **$1,008.79M** in lease liabilities against **$46.32M** cash and **-$901.29M** stockholders' deficit (`S12`). Crucially, the FY2025 10-K notes that leases are renewed *"at then-current market rates"* (`S11`).
4. **Capital Markets, Taxes & Black Swan Hazards (`S13`–`S26`):**
   - **Rates & Cap Rates:** FRED `DGS10` is **4.84%** on `2026-11-05` (**4.90%** on `2026-11-04`, `5.31%` Oct 2026 peak, `S15`) and FOMC upper target is **4.00%** (`S16`), while SEC-audited `NNN REIT` cap rates are **7.4% acquisition / 6.4% disposition** (`S13`) and `Realty Income` cash yield is **7.3%** (`S14`).
   - **Prop 13 & Measure ULA (`S17`, `S18`):** Selling resets the parcel's Prop 13 assessment (1% levy, 2%/yr cap) to 100% FMV, which passes through to the NNN tenant. Inside the City of LA, closings above **$5,400,000** trigger Measure ULA's **4.0% gross surtax** (4.45% total City transfer tax).
   - **Black Swan Exposure (`S21`–`S24`):** USGS UCERF3 places 30-year LA earthquake probabilities at **60% for M>=6.7**, **46% for M>=7.0**, and **31% for M>=7.5** (`S22`). The Jan 2025 Eaton & Palisades fires destroyed **16,251–16,264 structures**, caused **$5.2B–$10.1B** in county output loss (`S21`), and triggered a **$1.0 billion California FAIR Plan emergency assessment** (`S23`).
