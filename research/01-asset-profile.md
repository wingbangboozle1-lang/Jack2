# 01 — Asset Profile (Anonymised)

> **Privacy notice.** Every identifier on this page is a placeholder by design. No personal, entity, or parcel information is collected, stored, or published.

## 1.1 Record

| Field | Value | Status |
|---|---|---|
| Asset ID | `PROP-001` | internal |
| Asset type | Single-tenant retail, freestanding, drive-thru capable | as described |
| Brand | Jack in the Box (QSR, hamburger) | verified — brand exists, see §1.3 |
| Address | `[ADDRESS REDACTED]` | **withheld for privacy** |
| APN | `APN [REDACTED]` | **withheld for privacy** |
| Submarket | Central Los Angeles | as described by Owner |
| County | Los Angeles County, CA (FIPS 06037) | derived from submarket |
| Metro | Los Angeles–Long Beach–Anaheim, CA MSA (CBSA 31080) | derived |
| Lease type | NNN (triple-net) | **as described — unverified** |
| Lease expiry | 2030–2035 range | **as described — unverified, see §1.4** |
| Current rent / NOI | **not supplied** | **unverified** |
| Basis / debt | **not supplied** | **unverified** |
| Owner | `PARTY-OWNER` | withheld |
| Tenant of record | `PARTY-TENANT` | withheld |
| Guarantor | **unknown** | **unverified** |

## 1.2 What "NNN" does and does not mean here

The Owner describes the lease as **NNN**. That is a description, not a verified document. A triple-net retail lease typically obliges the tenant to pay base rent plus its proportionate share of property taxes, insurance and common-area maintenance. What materially changes value, and what this analysis therefore treats as an **open question**, is:

| Question | Why it matters | Status |
|---|---|---|
| Is the tenant **Jack in the Box Inc.** (corporate) or a **franchisee**? | Sets credit quality. Boulder Group prices corporate-QSR and franchisee-QSR paper ~100 bp apart (see `03`). | **unverified** |
| Is there a **corporate guaranty**? | A franchisee-only lease is unrated credit. Franchisee default is the single largest cash-flow risk. | **unverified** |
| Is it **absolute/double-net-in-disguise**? Who pays roof & structure? | Capital-replacement exposure of roughly 0.15–0.30 % of value per year sits with the landlord in a "NNN" lease that carves out roof/structure. | **unverified** |
| **Escalations**: flat, fixed bumps, or CPI? | Drives NOI growth and the value of waiting. Flat rent in a 3.7 %-inflation environment is a real-terms loss of ~3.7 %/yr. | **unverified** |
| **Options**: who holds them, at what rent? | A below-market tenant renewal option caps landlord upside; a landlord option caps tenant security and depresses sale value. | **unverified** |
| **Termination / kick-out rights** | Brand-level closure programmes (JACK closed 86 units in FY2025) make early-exit rights live risk, not boilerplate. | **unverified** |
| **Radius / use restrictions** | Affects re-leasing to a competing QSR after expiry. | **unverified** |

**Action required from Owner (blocking):** a redacted copy of the lease, the estoppel, the most recent rent statement, and the tax bill. Until received, everything downstream is scenario-based.

## 1.3 Why the "2030–2035" expiry range is itself a finding

The Owner gave a *range*, not a date. In single-tenant net lease valuation, remaining term is the single largest pricing variable after credit. A range spanning five years means the analysis cannot know whether the asset has **~3.5 years** or **~8.5 years** of term left (measured from 2026-11-06). Modeled at a 6.4 %–7.8 % cap-rate band that is the difference between roughly **15.6×** and **12.8×** NOI — a spread of about **18 %** of value, before any market move.

The model therefore runs the expiry as a random variable uniform on 2030-01-01 … 2035-12-31 (midpoint 2032-12-31) and reports sensitivity at 2030 and 2035.

## 1.4 Geographic and hazard context that *can* be stated without an address

County- and metro-level facts only (all T1). Parcel-level determinations are flagged, not guessed.

| Item | Value | Source | Tier | Status |
|---|---|---|---|---|
| Metropolitan area | Los Angeles–Long Beach–Anaheim MSA | U.S. Census / FRED | T1 | verified |
| County land area | 4,059.28 sq mi | Census QuickFacts 2020 | T1 | verified |
| City of Los Angeles land area | 469.49 sq mi | Census QuickFacts 2020 | T1 | verified |
| County population density | 2,466.9 persons/sq mi (2020) | Census QuickFacts | T1 | verified |
| City population density | 8,304.2 persons/sq mi (2020) | Census QuickFacts | T1 | verified |
| County wildfire events 2025 | 4 named LA County incidents ≥5,000 ac (Palisades, Eaton, Hughes, Canyon) | CAL FIRE 2025 Incident Archive | T1 | verified |
| State-wide wildfire structures destroyed 2025 | 16,627 | CAL FIRE 2025 Incident Archive | T1 | verified |
| Parcel fire-hazard-severity zone | — | requires address | T1 | **unverified** |
| Parcel FEMA flood zone | — | requires address | T1 | **unverified** |
| Parcel seismic site class | — | requires address | T1 | **unverified** |
| Parcel assessed value | — | requires APN | T1 | **unverified** |

## 1.5 Sources for this file

- Census Bureau, QuickFacts — Los Angeles County & Los Angeles city (V2025 + ACS 2020-2024): https://www.census.gov/quickfacts/fact/table/losangelescountycalifornia,losangelescitycalifornia/PST045224
- CAL FIRE, 2025 Incident Archive: https://www.fire.ca.gov/incidents/2025
- CAL FIRE / OSFM, Fire Hazard Severity Zones programme: https://osfm.fire.ca.gov/what-we-do/community-wildfire-preparedness-and-mitigation/fire-hazard-severity-zones
- FRED, Los Angeles–Long Beach–Anaheim MSA total nonfarm employment (SMU06310800000000001): https://fred.stlouisfed.org/series/SMU06310800000000001
