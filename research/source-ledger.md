# Verification ledger - manual review copy

Access date: **2026-11-06**. Generated from `data/metrics.json` by `tools/export_ledger.py`; identical to what the website publishes.

Rule applied: a value appears only if it was read from the official source below on the access date. Rows with no confirmed value are blank and marked UNVERIFIED.

## Sources

| ID | Tier | Publisher | Document | URL |
|---|---|---|---|---|
| S1 | A | U.S. Bureau of Labor Statistics (BLS), Western Information Office | Los Angeles Area Economic Summary (updated October 05, 2026) | <https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf> |
| S2 | A | U.S. Census Bureau | QuickFacts: Los Angeles city, California (V2025 population estimates; 2020-2024 ACS 5-year) | <https://www.census.gov/quickfacts/fact/table/losangelescitycalifornia,lacountycalifornia/PST045224> |
| S3 | A | California Department of Finance, Demographic Research Unit | Report P-2A: Total Population Projections, California Counties, 2020-2070 (Baseline 2024; Vintage 2026 Release, March 2026) | <https://dof.ca.gov/media/docs/forecasting/Demographics/projections/P2A_County_Total.xlsx> |
| S4 | A | California Department of Industrial Relations (DIR), Labor Commissioner's Office | Minimum Wage Frequently Asked Questions | <https://www.dir.ca.gov/dlse/faq_minimumwage.htm> |
| S5 | A | California Department of Industrial Relations (DIR), Labor Commissioner's Office | Fast Food Minimum Wage Frequently Asked Questions (AB 1228 / Labor Code 1474-1476) | <https://www.dir.ca.gov/dlse/Fast-Food-Minimum-Wage-FAQ.htm> |
| S6 | A | Los Angeles County Office of the Assessor | Real Property Assessment - An Overview of Property Taxes / Proposition 13 | <https://assessor.lacounty.gov/homeowners/realproperty> |
| S7 | A | Los Angeles County Registrar-Recorder/County Clerk | Documentary Transfer Tax | <https://www.lavote.gov/home/recorder/property-document-recording/documentary-transfer-taxes> |
| S8 | A | City of Los Angeles Office of Finance | Real Property Transfer Tax and Measure ULA FAQ | <https://finance.lacity.gov/faq/measure-ula> |
| S9 | B | Jack in the Box Inc. (NASDAQ: JACK), SEC EDGAR | Form 10-K for fiscal year ended September 28, 2025 (filed November 2025) | <https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm> |
| S10 | C | Realty Income Corporation (NYSE: O) | Q4 2025 Earnings Release & Supplemental Information (investor relations) | <https://www.realtyincome.com/sites/realty-income/files/2026-02/q4-2025-supplemental-report.pdf> |
| S11 | A | Board of Governors of the Federal Reserve System via FRED (St. Louis Fed) | Market Yield on U.S. Treasury Securities at 10-Year Constant Maturity (DGS10) | <https://fred.stlouisfed.org/series/DGS10> |
| S12 | A | Board of Governors of the Federal Reserve System via FRED (St. Louis Fed) | Federal Funds Target Range - Upper Limit (DFEDTARU) | <https://fred.stlouisfed.org/series/DFEDTARU> |
| S13 | A | County of Los Angeles | Key Facts About the Eaton and Palisades Fires (anniversary fact sheet) | <https://file.lacounty.gov/SDSInter/lac/1199046_Eaton_Palisades_Fires_Anniversary_Fact_Sheet.pdf> |
| S14 | A | California Department of Education (CDE) | District Profile: Los Angeles Unified (school year 2025-26) | <https://www.cde.ca.gov/sdprofile/details.aspx?cds=19647330000000> |
| S15 | A | California Department of Education (CDE) | Largest & Smallest Public School Districts (2025-26) | <https://www.cde.ca.gov/ds/ad/ceflargesmalldist.asp> |
| S16 | A | Internal Revenue Service | Instructions for Form 8824, Like-Kind Exchanges (rev. December 2025) | <https://www.irs.gov/pub/irs-pdf/i8824.pdf> |
| S17 | A | CAL FIRE - Office of the State Fire Marshal | Fire Hazard Severity Zones (FHSZ) maps and program | <https://osfm.fire.ca.gov/what-we-do/community-wildfire-preparedness-and-mitigation/fire-hazard-severity-zones/fire-hazard-severity-zones-maps-2022> |
| S18 | A | U.S. Geological Survey, Earthquake Hazards Program | Earthquake Hazards Program - hazards, maps and data | <https://www.usgs.gov/programs/earthquake-hazards> |
| S19 | A | Federal Emergency Management Agency (FEMA) | Flood Map Service Center / National Flood Hazard Layer | <https://msc.fema.gov/portal/home> |
| S20 | A | California Department of Insurance (CDI) | California FAIR Plan - consumers and agents | <https://www.insurance.ca.gov/01-consumers/105-type/95-guides/01-resi/FAIR-Plan.cfm> |
| S21 | A | City of Los Angeles Economic and Workforce Development Department (EWDD) | Annual Economic Report FY2025-26, Tab 5: Los Angeles - People, Industry and Jobs (Economic Forecast) | <https://ewdd.lacity.gov/images/reports/ap25/APy25_Tab5-EconomicForecast.pdf> |
| S22 | A | Los Angeles County Auditor-Controller | Property Tax FAQs | <https://auditor.lacounty.gov/faqs/> |
| S23 | A | U.S. Bureau of Economic Analysis (BEA) | Gross Domestic Product by County and Personal Income by County, 2024 (BEA 26-08, released February 5, 2026) | <https://www.bea.gov/news/2026/gross-domestic-product-county-and-personal-income-county-2024> |

## Population

| ID | Metric | Value | Unit | Period | Geography | Status | Source | Note |
|---|---|---|---|---|---|---|---|---|
| M01 | Los Angeles city population (July 1, 2025 estimate) | 3,869,089 | persons | 2025 | City of Los Angeles | VERIFIED | [S2](https://www.census.gov/quickfacts/fact/table/losangelescitycalifornia,lacountycalifornia/PST045224) | Census Bureau Vintage 2025 estimate. |
| M02 | Los Angeles city population change, April 1, 2020 base to July 1, 2025 | -0.8% | percent | 2020-2025 | City of Los Angeles | VERIFIED | [S2](https://www.census.gov/quickfacts/fact/table/losangelescitycalifornia,lacountycalifornia/PST045224) | Population estimates base 3,899,342; 2020 Census 3,898,747. |
| M03 | Los Angeles County population (state projection) | 9,853,435 | persons | 2025 | Los Angeles County | VERIFIED | [S3](https://dof.ca.gov/media/docs/forecasting/Demographics/projections/P2A_County_Total.xlsx) | CA DOF P-2A Vintage 2026, FIPS 6037. |
| M04 | Los Angeles County population projection | 9,727,305 | persons | 2030 | Los Angeles County | VERIFIED | [S3](https://dof.ca.gov/media/docs/forecasting/Demographics/projections/P2A_County_Total.xlsx) | Official state projection. Direction: mild decline. |
| M05 | Los Angeles County population projection | 9,708,647 | persons | 2035 | Los Angeles County | VERIFIED | [S3](https://dof.ca.gov/media/docs/forecasting/Demographics/projections/P2A_County_Total.xlsx) | Official state projection - coincident with the lease expiration window. |
| M06 | Los Angeles County population projection | 9,637,524 | persons | 2040 | Los Angeles County | VERIFIED | [S3](https://dof.ca.gov/media/docs/forecasting/Demographics/projections/P2A_County_Total.xlsx) | Official state projection. 2020 actual in same series: 10,012,050. |
| M07 | Los Angeles County population change, 2020 to 2040 (same DOF series) | -3.7% | percent | 2020-2040 | Los Angeles County | VERIFIED | [S3](https://dof.ca.gov/media/docs/forecasting/Demographics/projections/P2A_County_Total.xlsx) | Computed as (9,637,524 - 10,012,050) / 10,012,050 from the official series. Arithmetic on cited values only. |
| M08 | Households | 1,439,097 | households | 2020-2024 ACS 5-yr | City of Los Angeles | VERIFIED | [S2](https://www.census.gov/quickfacts/fact/table/losangelescitycalifornia,lacountycalifornia/PST045224) |  |
| M09 | Persons per household | 2.61 | persons | 2020-2024 ACS 5-yr | City of Los Angeles | VERIFIED | [S2](https://www.census.gov/quickfacts/fact/table/losangelescitycalifornia,lacountycalifornia/PST045224) |  |
| M10 | Foreign-born share of population | 35.7% | percent | 2020-2024 ACS 5-yr | City of Los Angeles | VERIFIED | [S2](https://www.census.gov/quickfacts/fact/table/losangelescitycalifornia,lacountycalifornia/PST045224) | Relevant to trade-area stability and labor supply. |
| M11 | Population under 18 | 19.2% | percent | 2025 estimate | City of Los Angeles | VERIFIED | [S2](https://www.census.gov/quickfacts/fact/table/losangelescitycalifornia,lacountycalifornia/PST045224) |  |
| M12 | Population 65 and over | 14.2% | percent | 2025 estimate | City of Los Angeles | VERIFIED | [S2](https://www.census.gov/quickfacts/fact/table/losangelescitycalifornia,lacountycalifornia/PST045224) |  |

## Income

| ID | Metric | Value | Unit | Period | Geography | Status | Source | Note |
|---|---|---|---|---|---|---|---|---|
| M13 | Median household income | $81,939 | USD (2024 dollars) | 2020-2024 ACS 5-yr | City of Los Angeles | VERIFIED | [S2](https://www.census.gov/quickfacts/fact/table/losangelescitycalifornia,lacountycalifornia/PST045224) |  |
| M14 | Median value of owner-occupied housing units | $921,200 | USD | 2020-2024 ACS 5-yr | City of Los Angeles | VERIFIED | [S2](https://www.census.gov/quickfacts/fact/table/losangelescitycalifornia,lacountycalifornia/PST045224) | Owner-occupied rate 36.0%. |
| M15 | Median gross rent | $1,933 | USD/month | 2020-2024 ACS 5-yr | City of Los Angeles | VERIFIED | [S2](https://www.census.gov/quickfacts/fact/table/losangelescitycalifornia,lacountycalifornia/PST045224) |  |
| M16 | Poverty rate | **(blank - unverified)** | percent | 2020-2024 ACS 5-yr | City of Los Angeles | UNVERIFIED | [S2](https://www.census.gov/quickfacts/fact/table/losangelescitycalifornia,lacountycalifornia/PST045224) | Not present in the QuickFacts extract captured. Left blank rather than taken from a secondary aggregator. |
| M17 | Per capita income | **(blank - unverified)** | USD | 2020-2024 ACS 5-yr | City of Los Angeles | UNVERIFIED | [S2](https://www.census.gov/quickfacts/fact/table/losangelescitycalifornia,lacountycalifornia/PST045224) | Not present in the QuickFacts extract captured (B19301). Left blank. |
| M86 | Los Angeles County total personal income (highest of any US county) | $818.5 billion | USD | 2024 | Los Angeles County | VERIFIED | [S23](https://www.bea.gov/news/2026/gross-domestic-product-county-and-personal-income-county-2024) | BEA 26-08. Confirms the size of the county's consumer base even while population declines. |
| M87 | Los Angeles County real GDP level | **(blank - unverified)** | USD | 2024 | Los Angeles County | UNVERIFIED | [S23](https://www.bea.gov/news/2026/gross-domestic-product-county-and-personal-income-county-2024) | The BEA news release quantifies county personal income ($818.5B for Los Angeles County) but publishes the GDP level only in its interactive tables, which were not machine-readable in this session. Left blank rather than inferred from personal income. |

## Employment

| ID | Metric | Value | Unit | Period | Geography | Status | Source | Note |
|---|---|---|---|---|---|---|---|---|
| M18 | Total nonfarm employment (not seasonally adjusted) | 6,289.1 | thousands of jobs | Aug 2026 | Los Angeles-Long Beach-Anaheim MSA | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | Prior year Aug 2025 comparison is embedded in S1 (12-month change below). |
| M19 | Total nonfarm employment, 12-month change | +38.2 thousand (+0.6%) | jobs / percent | Aug 2025 to Aug 2026 | Los Angeles-Long Beach-Anaheim MSA | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | Growth is positive but below US trend in the same release (+0.3% US). |
| M20 | Unemployment rate | 4.8% | percent | Aug 2026 | Los Angeles metro area | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | Aug 2025: 5.8%. Clear improvement year over year. |
| M21 | Unemployment rate | 4.9% | percent | Aug 2026 | Los Angeles County | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | Aug 2025: 6.2%. |
| M22 | Unemployment rate | 5.0% | percent | Aug 2026 | City of Los Angeles | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | Aug 2025: 6.2%. |
| M23 | Unemployment rate - benchmarks | California 5.4%; United States 4.3% | percent | Aug 2026 | State of California / US | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | Local area still above the national rate. |
| M24 | Leisure and hospitality employment, 12-month change | +16.8 thousand (+2.2%) | jobs / percent | Aug 2025 to Aug 2026 | Los Angeles-Long Beach-Anaheim MSA | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | Underlying demand for restaurant space and drive-thru trade areas. |
| M25 | Education and health services employment, 12-month change | +42.7 thousand (+3.3%) | jobs / percent | Aug 2025 to Aug 2026 | Los Angeles-Long Beach-Anaheim MSA | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | Largest single contributor to net job growth in the metro. |
| M26 | Information sector employment, 12-month change | -12.3 thousand (-6.1%) | jobs / percent | Aug 2025 to Aug 2026 | Los Angeles-Long Beach-Anaheim MSA | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | Largest percentage decline of any sector; office-adjacent lunch demand risk. |
| M27 | Professional and business services employment, 12-month change | -9.2 thousand (-0.9%) | jobs / percent | Aug 2025 to Aug 2026 | Los Angeles-Long Beach-Anaheim MSA | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | White-collar contraction. |
| M28 | Manufacturing employment, 12-month change | -5.2 thousand (-1.1%) | jobs / percent | Aug 2025 to Aug 2026 | Los Angeles-Long Beach-Anaheim MSA | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) |  |
| M29 | Trade, transportation and utilities employment, 12-month change | -2.3 thousand (-0.2%) | jobs / percent | Aug 2025 to Aug 2026 | Los Angeles-Long Beach-Anaheim MSA | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | Includes the port/logistics complex. |
| M30 | Financial activities employment, 12-month change | -4.7 thousand (-1.5%) | jobs / percent | Aug 2025 to Aug 2026 | Los Angeles-Long Beach-Anaheim MSA | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) |  |
| M31 | Construction employment, 12-month change | -1.9 thousand (-0.7%) | jobs / percent | Aug 2025 to Aug 2026 | Los Angeles-Long Beach-Anaheim MSA | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | Rebuild demand after the 2025 fires is not yet visible as construction job growth in this release. |
| M32 | Government employment, 12-month change | +10.7 thousand (+1.5%) | jobs / percent | Aug 2025 to Aug 2026 | Los Angeles-Long Beach-Anaheim MSA | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) |  |

## Wages

| ID | Metric | Value | Unit | Period | Geography | Status | Source | Note |
|---|---|---|---|---|---|---|---|---|
| M33 | Average weekly wage, all industries | $1,704 | USD/week | Q1 2026 | Los Angeles County | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | US average $1,654; metro area $1,721; Orange County $1,766 (QCEW). |
| M34 | Employment Cost Index, 12-month change | +2.8% | percent | Jun 2026 | Los Angeles-Long Beach CSA | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | US +3.1%. Wage pressure is cooling versus 2023 (+5.3%). |

## Prices

| ID | Metric | Value | Unit | Period | Geography | Status | Source | Note |
|---|---|---|---|---|---|---|---|---|
| M35 | CPI-U, all items, 12-month change | +3.6% | percent | Aug 2026 | Los Angeles metro area | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | US +3.4%. This is the reference rate for CPI-linked rent escalators. |
| M36 | CPI-U, food, 12-month change | +2.8% | percent | Aug 2026 | Los Angeles metro area | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) |  |
| M37 | CPI-U, energy, 12-month change | +17.6% | percent | Aug 2026 | Los Angeles metro area | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | Relevant to operating cost pass-throughs in a NNN structure. |

## Consumer demand

| ID | Metric | Value | Unit | Period | Geography | Status | Source | Note |
|---|---|---|---|---|---|---|---|---|
| M38 | Total accommodation and food services sales | $17,366,966 thousand | USD | 2022 (Economic Census) | City of Los Angeles | VERIFIED | [S2](https://www.census.gov/quickfacts/fact/table/losangelescitycalifornia,lacountycalifornia/PST045224) | Latest Economic Census year available in QuickFacts. |
| M39 | Average annual household expenditures - shelter/housing | $33,126 | USD/year | 2023-2024 | Los Angeles metro area | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | US $25,853. High housing cost share compresses discretionary food spending. |
| M40 | Average annual household expenditures - food | $11,858 | USD/year | 2023-2024 | Los Angeles metro area | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | US $10,077. |
| M41 | Average annual household expenditures - transportation | $14,497 | USD/year | 2023-2024 | Los Angeles metro area | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | US $13,278. Car dependency supports drive-thru formats. |
| M42 | Median household income (county comparison) | **(blank - unverified)** | USD | 2020-2024 ACS 5-yr | Los Angeles County | UNVERIFIED | [S2](https://www.census.gov/quickfacts/fact/table/losangelescitycalifornia,lacountycalifornia/PST045224) | County column was not captured in the QuickFacts extract. Blank by rule; do not substitute an aggregator value. |

## Education

| ID | Metric | Value | Unit | Period | Geography | Status | Source | Note |
|---|---|---|---|---|---|---|---|---|
| M43 | Los Angeles Unified enrollment (Census Day) | 497,105 | students | 2025-26 | LAUSD | VERIFIED | [S14](https://www.cde.ca.gov/sdprofile/details.aspx?cds=19647330000000) | Corroborated by S15 (same figure). |
| M44 | English learner share of LAUSD enrollment | 16.4% (81,328 students) | percent | 2025-26 | LAUSD | VERIFIED | [S14](https://www.cde.ca.gov/sdprofile/details.aspx?cds=19647330000000) |  |
| M45 | Statewide public school enrollment | 5,731,260 | students | 2025-26 | State of California | VERIFIED | [S15](https://www.cde.ca.gov/ds/ad/ceflargesmalldist.asp) | LAUSD is ~8.7% of the state total (computed from cited values). |
| M46 | LAUSD four-year cohort graduation rate | **(blank - unverified)** | percent | 2024-25 | LAUSD | UNVERIFIED | [S14](https://www.cde.ca.gov/sdprofile/details.aspx?cds=19647330000000) | Two candidate figures circulate (four-year vs five-year). Neither was confirmed directly on the CDE DataQuest page in this session; left blank and flagged. |
| M47 | Postsecondary attainment, bachelor's degree or higher | 38.5% | percent of persons 25+ | 2020-2024 ACS 5-yr | City of Los Angeles | VERIFIED | [S2](https://www.census.gov/quickfacts/fact/table/losangelescitycalifornia,lacountycalifornia/PST045224) | High school graduate or higher: 79.6%. |

## Capital markets

| ID | Metric | Value | Unit | Period | Geography | Status | Source | Note |
|---|---|---|---|---|---|---|---|---|
| M48 | 10-year Treasury constant maturity yield | 4.90% | percent | 2026-11-04 | United States | VERIFIED | [S11](https://fred.stlouisfed.org/series/DGS10) | Five prior observations in the same series range 4.91%-4.98% - no rate relief in the recent window. |
| M49 | FOMC target range, upper limit | 4.00% | percent | 2026-11-05 | United States | VERIFIED | [S12](https://fred.stlouisfed.org/series/DFEDTARU) |  |
| M50 | Net-lease acquisition pricing benchmark - initial weighted average cash yield on 2025 real estate acquisitions | 7.3% | percent | FY2025 | United States and Europe (Realty Income) | VERIFIED | [S10](https://www.realtyincome.com/sites/realty-income/files/2026-02/q4-2025-supplemental-report.pdf) | Includes European and industrial/other assets, not a single-asset QSR cap rate. Used only as a directional anchor; see the flagged list. |
| M51 | Single-tenant QSR cap rate for a Central LA asset | **(blank - unverified)** | percent | 2026 | Subject property | UNVERIFIED | [S10](https://www.realtyincome.com/sites/realty-income/files/2026-02/q4-2025-supplemental-report.pdf) | No official government series publishes asset-level cap rates. A broker opinion of value or appraisal is required. Model uses sensitivity, not a point estimate. |

## Taxes and transaction costs

| ID | Metric | Value | Unit | Period | Geography | Status | Source | Note |
|---|---|---|---|---|---|---|---|---|
| M52 | Proposition 13 general levy cap | 1% | percent of assessed value | current | Los Angeles County | VERIFIED | [S6](https://assessor.lacounty.gov/homeowners/realproperty) | Plus voter-approved bonded indebtedness and direct assessments (S22). |
| M53 | Annual assessed value increase cap | 2% | percent per year | current | Los Angeles County | VERIFIED | [S6](https://assessor.lacounty.gov/homeowners/realproperty) | Below current CPI in the metro (M35) - a real holding-cost advantage for a long-held asset. |
| M54 | Reassessment trigger | Change of ownership or new construction | event | current | Los Angeles County | VERIFIED | [S6](https://assessor.lacounty.gov/homeowners/realproperty) | A sale resets the buyer's base year value; the seller's low Prop 13 basis is not transferable. |
| M55 | Los Angeles County documentary transfer tax | $1.10 per $1,000 (0.11%) | rate | current | Los Angeles County | VERIFIED | [S7](https://www.lavote.gov/home/recorder/property-document-recording/documentary-transfer-taxes) | Statutory basis: Revenue and Taxation Code 11911. |
| M56 | City of Los Angeles documentary transfer tax | $4.50 per $1,000 (0.45%) | rate | current | City of Los Angeles | VERIFIED | [S7](https://www.lavote.gov/home/recorder/property-document-recording/documentary-transfer-taxes) | Also stated as $2.25 per $500 by S8. |
| M57 | Measure ULA surtax - tier 1 | 4.0% | percent of gross sale price | closings on/after 2026-07-01 | City of Los Angeles | VERIFIED | [S8](https://finance.lacity.gov/faq/measure-ula) | Applies above $5,400,000 and below $10,900,000 (S7 table, effective 7/1/26). |
| M58 | Measure ULA surtax - tier 2 | 5.5% | percent of gross sale price | closings on/after 2026-07-01 | City of Los Angeles | VERIFIED | [S8](https://finance.lacity.gov/faq/measure-ula) | Applies at $10,900,000 and above. |
| M59 | Measure ULA threshold indexation | Adjusted annually by chained CPI | mechanism | current | City of Los Angeles | VERIFIED | [S8](https://finance.lacity.gov/faq/measure-ula) | Thresholds must be re-checked at the time of any sale. |
| M60 | Section 1031 like-kind exchange deferral | Available for real property held for business or investment | tax treatment | current law (post-TCJA) | United States | VERIFIED | [S16](https://www.irs.gov/pub/irs-pdf/i8824.pdf) | Deferred exchange requires a qualified intermediary and the 45/180-day rules; basis carries over. California conforms to IRC 1031 for state purposes - state conformity not independently verified here (see flagged list). |

## Labor regulation

| ID | Metric | Value | Unit | Period | Geography | Status | Source | Note |
|---|---|---|---|---|---|---|---|---|
| M61 | California statewide minimum wage | $16.90 | USD/hour | effective 2026-01-01 | State of California | VERIFIED | [S4](https://www.dir.ca.gov/dlse/faq_minimumwage.htm) | Indexed annually to CPI-W, capped at 3.5% per year. |
| M62 | California fast food minimum wage (AB 1228) | $20.00 | USD/hour | in force since 2024-04-01 | State of California | VERIFIED | [S5](https://www.dir.ca.gov/dlse/Fast-Food-Minimum-Wage-FAQ.htm) | Applies to limited-service chains with 60+ US locations - Jack in the Box franchisees are covered. Fast Food Council may raise it; no later council-set rate was displayed on the DIR page on the access date. |
| M63 | City of Los Angeles local minimum wage | **(blank - unverified)** | USD/hour | 2026 | City of Los Angeles | UNVERIFIED | [S4](https://www.dir.ca.gov/dlse/faq_minimumwage.htm) | DIR states a local rate may exceed the state rate but the city rate itself was not confirmed on an official city page in this session. Blank by rule. |

## Tenant and brand

| ID | Metric | Value | Unit | Period | Geography | Status | Source | Note |
|---|---|---|---|---|---|---|---|---|
| M64 | Jack in the Box system restaurants | 2,136 | restaurants | fiscal year-end 2025-09-28 | System | VERIFIED | [S9](https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm) | 1,986 (93%) franchised; 150 company-operated. |
| M65 | Jack in the Box system count at start of fiscal 2025 | 2,191 | restaurants | 2024-09-29 | System | VERIFIED | [S9](https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm) | Net change over FY2025: -55 units. The company attributes part of this to a deliberate block-closure program under 'Jack on Track'. |
| M66 | Franchise agreement term and fee | 20-year term; $50,000 initial fee; 5.0% royalty | terms | current form | System | VERIFIED | [S9](https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm) | Franchise term is longer than the 2030-2035 lease window - the operator has economic incentive to renew the site. |
| M67 | Prototype building size | ~1,372 sq ft | square feet | current | System | VERIFIED | [S9](https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm) | Relevant to replacement-cost and re-tenanting math. |
| M68 | Franchise restaurant average unit volume | $1,874 thousand | USD per unit per year | FY2025 | System | VERIFIED | [S9](https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm) | FY2024: $1,949 thousand - a 3.8% decline. Rent at 8-10% of sales implies roughly $150k-$187k per unit per year of occupancy cost. |
| M69 | Share of restaurants in California and Texas | ~70% | percent of system | FY2025 | System | VERIFIED | [S9](https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm) | Company names this concentration explicitly as a severe-weather and natural-disaster risk factor. |
| M70 | Leases with contingent rent | ~13% of Jack in the Box leases, 1%-10% of gross sales above thresholds | percent of leases | FY2025 | System | VERIFIED | [S9](https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm) | Confirms a hybrid rent structure is normal in this chain - the subject lease should be checked for a percentage-rent clause. |
| M71 | Company statement on lease renewals | 'We have generally been able to renew our restaurant leases as they expire at then-current market rates.' | quotation | FY2025 10-K | System | VERIFIED | [S9](https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm) | Direct quotation. Implies renewals are repriced to market - the 2030-2035 expiry is a repricing event, not an automatic rollover. |
| M72 | Restaurant properties structure (Jack in the Box) | 729 company-owned buildings (565 on leased land); 1,020 company-leased buildings on leased land; 387 franchise-owned/leased buildings | buildings | FY2025 | System | VERIFIED | [S9](https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm) | Signals that the brand routinely operates on third-party land - a landlord's renewal leverage is real but the tenant has alternatives. |
| M73 | Del Taco divestiture | $115 million to Yadav Enterprises, Inc. | USD | sale agreement 2025-10-15 | System | VERIFIED | [S9](https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm) | Subsequent event. Reduces brand complexity; proceeds earmarked for debt paydown. |
| M74 | Securitized debt outstanding (Master Issuer) | ~$1.7 billion | USD | 2025-09-28 | System | VERIFIED | [S9](https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm) | Covenants include DSCR and gross-sales triggers - a stressed franchisee system can accelerate amortization. |
| M75 | Dividend | Discontinued | corporate action | FY2025 | System | VERIFIED | [S9](https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm) | 'Jack on Track' reallocates cash to debt paydown. Signals balance-sheet priority over distribution. |

## Hazard

| ID | Metric | Value | Unit | Period | Geography | Status | Source | Note |
|---|---|---|---|---|---|---|---|---|
| M76 | Eaton Fire - area burned | 14,021 | acres | Jan 2025 | Los Angeles County | VERIFIED | [S13](https://file.lacounty.gov/SDSInter/lac/1199046_Eaton_Palisades_Fires_Anniversary_Fact_Sheet.pdf) | Structures destroyed 9,414; damaged 1,074; 19 confirmed fatalities. |
| M77 | Palisades Fire - area burned | 23,448 | acres | Jan 2025 | Los Angeles County | VERIFIED | [S13](https://file.lacounty.gov/SDSInter/lac/1199046_Eaton_Palisades_Fires_Anniversary_Fact_Sheet.pdf) | Structures destroyed 6,837; damaged 973; 12 confirmed fatalities. |
| M78 | Estimated economic output lost - 2025 fire pair | $5.2 billion to $10.1 billion | USD | 2025 | Los Angeles County | VERIFIED | [S13](https://file.lacounty.gov/SDSInter/lac/1199046_Eaton_Palisades_Fires_Anniversary_Fact_Sheet.pdf) | County-published estimate range. |
| M79 | Businesses impacted - 2025 fire pair | ~6,800 | businesses | 2025 | Los Angeles County | VERIFIED | [S13](https://file.lacounty.gov/SDSInter/lac/1199046_Eaton_Palisades_Fires_Anniversary_Fact_Sheet.pdf) | Workers impacted ~47,000. |
| M80 | Labor income lost - 2025 fire pair | $2.2 billion to $4.2 billion | USD | 2025 | Los Angeles County | VERIFIED | [S13](https://file.lacounty.gov/SDSInter/lac/1199046_Eaton_Palisades_Fires_Anniversary_Fact_Sheet.pdf) |  |
| M81 | Tax revenue losses - 2025 fire pair | $900 million to $1.6 billion | USD | 2025 | Los Angeles County | VERIFIED | [S13](https://file.lacounty.gov/SDSInter/lac/1199046_Eaton_Palisades_Fires_Anniversary_Fact_Sheet.pdf) | Directly relevant to municipal service capacity and to future parcel-tax and assessment pressure. |
| M82 | Fire Hazard Severity Zone classification of the subject parcel | **(blank - unverified)** | zone | 2026 | Subject property | UNVERIFIED | [S17](https://osfm.fire.ca.gov/what-we-do/community-wildfire-preparedness-and-mitigation/fire-hazard-severity-zones/fire-hazard-severity-zones-maps-2022) | Requires parcel-level lookup in the CAL FIRE FHSZ viewer plus LAFD/LACoFD local maps. Central Los Angeles flatland is generally outside SRA very-high zones, but this is NOT asserted here. |
| M83 | Seismic site classification and fault-rupture zone | **(blank - unverified)** | classification | 2026 | Subject property | UNVERIFIED | [S18](https://www.usgs.gov/programs/earthquake-hazards) | Requires the CGS EQ Zapp / Alquist-Priolo maps and a geotechnical report. Blank by rule. |
| M84 | FEMA flood zone | **(blank - unverified)** | zone | effective FIRM | Subject property | UNVERIFIED | [S19](https://msc.fema.gov/portal/home) | Requires a parcel-level NFHL lookup. Blank by rule. |
| M85 | Property insurance availability and premium | **(blank - unverified)** | USD / terms | 2026 | Subject property | UNVERIFIED | [S20](https://www.insurance.ca.gov/01-consumers/105-type/95-guides/01-resi/FAIR-Plan.cfm) | No official published rate for a commercial parcel. Must be quoted by a broker; FAIR Plan is residential-oriented and does not solve commercial wildfire capacity. |

## Totals

- Rows: 87
- Verified: 76
- Blank / unverified: 11
- Sources: 23

