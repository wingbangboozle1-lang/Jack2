# 05 — Geography, Catastrophe Risk and the "Black Swan" Layer

The Owner asked specifically for business-as-usual risk **and** rare catastrophic events ("wildfires or natural disasters") that could destroy the local economy. This file separates what is **verified** from what **cannot be determined without a parcel identifier**, and it explains the *financial transmission channel* by which each hazard reaches a net-lease landlord.

---

## 5.1 Why a NNN landlord should care about hazards at all

A common error is: *"It's NNN, the tenant pays insurance and taxes, so hazards are the tenant's problem."* That is wrong in four specific ways.

| Transmission channel | How it reaches the landlord | Mitigation available |
|---|---|---|
| **Insurance availability and price** | Even where the tenant pays, a doubling of property-insurance cost is a direct hit to the tenant's P&L and therefore to its willingness and ability to renew at the same rent. In severe cases coverage becomes unobtainable, which can make the site uninsurable and unfinanceable. | Confirm the lease's insurance covenant and who bears premium escalation. |
| **Post-event demand destruction** | A regional fire or earthquake displaces households and closes roads for months. QSR sales fall immediately; a marginal store can go cash-negative. | Trade-area diversification; no single-asset concentration. |
| **Physical asset loss / business interruption** | If the landlord owns roof and structure, rebuild is a landlord cost and rent abatement runs concurrently. | Confirm absolute-net vs modified; confirm landlord insurance. |
| **Buyer pool contraction** | After a visible catastrophe, buyers underwrite the whole submarket wider. Cap rates move even for undamaged buildings. | Sell *before* the repricing, or into a market that has already repriced. |

## 5.2 Wildfire — verified context

**Source: CAL FIRE 2025 Incident Archive (Tier 1).**

| Metric | Value | Period | Status |
|---|---|---|---|
| Wildfires responded to, statewide | **8,232** | 2025 | verified |
| Acres burned, statewide | **507,817** | 2025 | verified |
| Fatalities, statewide | 31 (preliminary, pending coroner confirmation) | 2025 | verified |
| **Structures destroyed, statewide** | **16,627** | 2025 | verified |
| Total emergency responses, statewide | 608,571 | 2025 | verified |

**Los Angeles County incidents ≥ 5,000 acres in 2025:**

| Incident | County | Start | Acres | Containment | Status |
|---|---|---|---|---|---|
| Palisades Fire | Los Angeles | 2025-01-07 | 23,448 | 100 % | verified |
| Eaton Fire | Los Angeles | 2025-01-07 | 14,021 | 100 % | verified |
| Hughes Fire | Los Angeles | 2025-01-22 | 10,425 | 100 % | verified |
| Canyon Fire | Los Angeles / Ventura | 2025-08-07 | 5,370 | 100 % | verified |

**Reading.** Two of the four largest 2025 Southern California fires started on the **same day** (2025-01-07) inside Los Angeles County, and the county accounted for at least **53,264 acres** across four incidents in a single year. The county-level black-swan event the Owner asked about is not hypothetical — it happened nine months before this analysis.

### Fire Hazard Severity Zones — how the classification works (verified) and what is unknown

| Fact | Detail | Source | Status |
|---|---|---|---|
| Classes | Moderate / High / Very High (three levels) | CAL FIRE OSFM | verified |
| Legal basis | Cal. Pub. Res. Code §§ 4201–4204; 14 CCR § 1280; Gov. Code §§ 51175–51189 | CAL FIRE OSFM | verified |
| What a zone measures | **Hazard, not risk** — physical conditions producing likelihood and expected fire behaviour over a **30–50 year** horizon, *ignoring* mitigation | CAL FIRE OSFM | verified |
| Responsibility split | State Responsibility Area (SRA) mapped 2023 / effective 2024-04-01; Local Responsibility Area (LRA) maps rolled out to all counties in four phases, Feb–Mar 2025 | CAL FIRE OSFM | verified |
| **Zone for `PROP-001`** | **—** | requires address | **unverified** |

This distinction matters commercially: a dense, flat, urban central-LA parcel is typically in the **Local Responsibility Area** and usually classified Moderate or unclassified, whereas hillside parcels in the same county are Very High. An urban infill drive-thru is therefore **structurally lower wildfire hazard than its county's headline numbers suggest** — but that is an inference, not a verified fact for this parcel, and it is **not** priced as zero, because smoke, power shut-offs, insurance repricing and buyer sentiment are county-wide.

## 5.3 Earthquake — official source identified, parcel determination not possible

| Item | Status | Authoritative source to consult with the address/APN |
|---|---|---|
| Fault proximity and rupture likelihood | **unverified** | USGS Earthquake Hazards Program — https://earthquake.usgs.gov/hazards/ |
| Seismic design category / site class | **unverified** | California Geological Survey, Seismic Hazards Program — https://www.conservation.ca.gov/cgs/geohazards |
| Liquefaction / landslide zone | **unverified** | CGS Seismic Hazard Zones maps |
| Building retrofit obligations | **unverified** | City of Los Angeles Department of Building and Safety |

**Why this matters disproportionately here.** Southern California's exposure is *regional and correlated*: one event affects the entire buyer pool, the entire tenant's store fleet, and the entire insurance market simultaneously. That is the definition of a risk that **diversification inside the region cannot fix** — which is itself a portfolio argument, independent of the parcel.

## 5.4 Flood, drought, heat, grid — status

| Hazard | Status | Note |
|---|---|---|
| FEMA flood zone for the parcel | **unverified** | To be checked at https://msc.fema.gov/portal/home with the address |
| Drought / water supply | Not quantified in this session | Affects landscaping, cooling, municipal capacity |
| Extreme heat | Not quantified in this session | Direct driver of HVAC capex and patio/drive-thru usability |
| Wildfire-related power shut-offs (PSPS) | Not quantified in this session | Causes multi-day revenue loss and spoilage |
| FEMA National Risk Index county score | **not retrieved** | The NRI API returned HTTP 500 on 2026-11-06; listed as a follow-up (L6) |

No number is asserted in this section. Blank is deliberate.

## 5.5 The financial consequence of catastrophes, modelled explicitly

Rather than assert a loss estimate, the projection engine in `model/projection_model.py` includes a **catastrophe module** with four explicit, adjustable event types. Each is an **assumption (Tier A)** with a stated rationale, and each is reported separately so its effect on the recommendation is visible rather than buried.

| Event | Annual probability (assumption) | Modelled impact |
|---|---|---|
| Regional wildfire / smoke / PSPS event affecting trade area | 4 %/yr | 5–25 % NOI interruption in the event year; +50–150 bp cap rate for 2 years |
| Significant seismic event (M6.5+) felt in metro | 3 %/yr | 20–60 % of gross rent abated for 3–12 months; landlord-borne repair share where the lease does not make it absolute-net |
| Property-insurance shock (premium doubling / non-renewal) | 6 %/yr | +60 bp cap rate for 3 years; upward pressure on tenant occupancy cost |
| Tenant default / franchisee insolvency | 3.5 %/yr while leased | Rent stops; 12–24 months to re-lease; 6 % of new annual rent in leasing costs |

These probabilities are **not** official statistics. They are the model's stated priors and are published so they can be challenged. The site labels them as assumptions and shows the result with the catastrophe module **switched off** as well as on, so the Owner can see exactly what the black-swan layer is worth.

## 5.6 What a catastrophe actually does to the hold-versus-sell decision

Catastrophe risk is not symmetric between the two choices:

| | Sell now | Hold 4–9 years to expiry |
|---|---|---|
| Exposure to a catastrophe | **Transferred to the buyer** at closing | **Retained in full** |
| Who bears the insurance repricing | Buyer | Owner |
| Who bears the demand shock | Buyer | Owner |
| Recovery upside if the event is benign | None | Retained |

The asymmetry is the point: **the hold strategy is a long position in the survival of a single parcel's cash flow through a period in which the historical frequency of severe LA County events is visibly rising.** That is a defensible bet only if it is paid for — i.e. only if the value of waiting, plus the tax deferral from *not* selling, exceeds the option value of de-risking now. Quantifying that trade-off is what the projection engine is for.

## 5.7 Sources

- CAL FIRE, 2025 Fire Season Incident Archive: https://www.fire.ca.gov/incidents/2025
- CAL FIRE, Palisades Fire incident record: https://www.fire.ca.gov/incidents/2025/1/7/palisades-fire
- CAL FIRE, Eaton Fire incident record: https://www.fire.ca.gov/incidents/2025/1/7/eaton-fire
- CAL FIRE / OSFM, Fire Hazard Severity Zones (programme, classes, legal basis, LRA rollout): https://osfm.fire.ca.gov/what-we-do/community-wildfire-preparedness-and-mitigation/fire-hazard-severity-zones
- FHSZ viewer (address lookup): https://experience.arcgis.com/experience/5065c998b4b0462f9ec3c6c226c610a9
- FEMA National Flood Hazard Layer: https://msc.fema.gov/portal/home
- FEMA National Risk Index: https://hazards.fema.gov/nri/
- USGS Earthquake Hazards Program: https://earthquake.usgs.gov/hazards/
- California Geological Survey, Seismic Hazards: https://www.conservation.ca.gov/cgs/geohazards
