# Verification ledger - manual review copy

Access date: **2026-11-07**. Generated from `data/metrics.json` by `tools/export_ledger.py`; identical to what the website publishes.

Rule applied: a value appears only if it was read from the official source below on the access date. Rows with no confirmed value are blank and marked UNVERIFIED.

## Sources

| ID | Tier | Publisher | Document | URL |
|---|---|---|---|---|
| S1 | A | U.S. Bureau of Labor Statistics (BLS), Western Information Office | Los Angeles Area Economic Summary (updated November 04, 2026; data through September 2026) | <https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf> |
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
| S16 | A | Internal Revenue Service | Instructions for Form 8824, Like-Kind Exchanges (2025 revision) | <https://www.irs.gov/pub/irs-pdf/i8824.pdf> |
| S17 | A | CAL FIRE - Office of the State Fire Marshal | Fire Hazard Severity Zones (FHSZ) - programme page, 2026 SRA update and 2025 LRA rollout | <https://osfm.fire.ca.gov/what-we-do/community-wildfire-preparedness-and-mitigation/fire-hazard-severity-zones> |
| S18 | A | U.S. Geological Survey, Earthquake Hazards Program | Earthquake Hazards Program - hazards, maps and data | <https://www.usgs.gov/programs/earthquake-hazards> |
| S19 | A | Federal Emergency Management Agency (FEMA) | Flood Map Service Center / National Flood Hazard Layer | <https://msc.fema.gov/portal/home> |
| S20 | A | California Department of Insurance (CDI) | California FAIR Plan (CDI consumer page) | <https://www.insurance.ca.gov/01-consumers/200-wrr/California-FAIR-Plan.cfm> |
| S21 | C | Los Angeles County Economic Development Corporation (LAEDC), Institute for Applied Economics - commissioned by the City of LA Workforce Development Board, hosted on ewdd.lacity.gov | Los Angeles: People, Industry and Jobs 2022-2028 (LAEDC, May 2024) - Annual Economic Report Tab 5 | <https://ewdd.lacity.gov/images/reports/ap25/APy25_Tab5-EconomicForecast.pdf> |
| S22 | A | Los Angeles County Auditor-Controller | Property Tax FAQs | <https://auditor.lacounty.gov/faqs/> |
| S23 | A | U.S. Bureau of Economic Analysis (BEA) | Gross Domestic Product by County and Personal Income by County, 2024 (BEA 26-08, released February 5, 2026) | <https://www.bea.gov/news/2026/gross-domestic-product-county-and-personal-income-county-2024> |
| S24 | B | Jack in the Box Inc. (NASDAQ: JACK), SEC EDGAR | Form 10-Q for the quarterly period ended July 5, 2026 (filed August 2026) | <https://www.sec.gov/Archives/edgar/data/807882/000080788226000091/jack-20260705.htm> |
| S25 | A | City of Los Angeles, Office of Wage Standards (EWDD) | Minimum Wage and Paid Sick Leave - 2026 Minimum Wage rate | <https://wagesla.lacity.gov/> |

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
| M16 | Poverty rate | 16.5% | percent | 2020-2024 ACS 5-yr | City of Los Angeles | VERIFIED | [S2](https://www.census.gov/quickfacts/fact/table/losangelescitycalifornia,lacountycalifornia/PST045224) | City of Los Angeles, Census QuickFacts (INC110224/IPE120225). Los Angeles County 13.3%. |
| M17 | Per capita income | $47,685 | USD | 2020-2024 ACS 5-yr | City of Los Angeles | VERIFIED | [S2](https://www.census.gov/quickfacts/fact/table/losangelescitycalifornia,lacountycalifornia/PST045224) | City of Los Angeles, per capita income in past 12 months (2024 dollars). Los Angeles County $45,792. |
| M86 | Los Angeles County total personal income (highest of any US county) | $818.5 billion | USD | 2024 | Los Angeles County | VERIFIED | [S23](https://www.bea.gov/news/2026/gross-domestic-product-county-and-personal-income-county-2024) | BEA 26-08. Confirms the size of the county's consumer base even while population declines. |
| M87 | Los Angeles County real GDP level | **(blank - unverified)** | USD | 2024 | Los Angeles County | UNVERIFIED | [S23](https://www.bea.gov/news/2026/gross-domestic-product-county-and-personal-income-county-2024) | BEA confirms Los Angeles County had the highest total personal income of any US county in 2024 ($818.5 billion). The release table does not print the county real-GDP level, only the top and bottom of each population-size band, so the value stays blank rather than being read off an interactive query that is not reproducible from the URL. |

## Employment

| ID | Metric | Value | Unit | Period | Geography | Status | Source | Note |
|---|---|---|---|---|---|---|---|---|
| M18 | Total nonfarm employment (not seasonally adjusted) | 6,282.1 | thousands of jobs | Sep 2026 | Los Angeles-Long Beach-Anaheim MSA | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | Los Angeles metro, total nonfarm, not seasonally adjusted. Updated from the superseded Aug 2026 figure (6,289.1). |
| M19 | Total nonfarm employment, 12-month change | +30.2 thousand (+0.5%) | jobs / percent | Sep 2025 to Sep 2026 | Los Angeles-Long Beach-Anaheim MSA | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | Positive but below the US trend in the same release (+0.3%). Updated from the superseded Aug 2026 figure. |
| M20 | Unemployment rate | 4.4% | percent | Sep 2026 | Los Angeles metro area | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | Los Angeles metro area. Sep 2025: 5.5%. Updated from the superseded Aug 2026 reading (4.8%). |
| M21 | Unemployment rate | 4.5% | percent | Sep 2026 | Los Angeles County | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | Los Angeles County. Sep 2025: 5.9%. |
| M22 | Unemployment rate | 4.5% | percent | Sep 2026 | City of Los Angeles | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | City of Los Angeles. Sep 2025: 5.9%. |
| M23 | Unemployment rate - benchmarks | California 5.1%; United States 4.0% | percent | Sep 2026 | State of California / US | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | County and city (4.5%) remain above the national rate (4.0%). |
| M24 | Leisure and hospitality employment, 12-month change | +11.5 thousand (+1.5%) | jobs / percent | Sep 2025 to Sep 2026 | Los Angeles-Long Beach-Anaheim MSA | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | Underlying demand for restaurant space and drive-thru trade areas. |
| M25 | Education and health services employment, 12-month change | +49.1 thousand (+3.8%) | jobs / percent | Sep 2025 to Sep 2026 | Los Angeles-Long Beach-Anaheim MSA | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | Largest single contributor to net job growth in the metro. |
| M26 | Information sector employment, 12-month change | -11.4 thousand (-5.7%) | jobs / percent | Sep 2025 to Sep 2026 | Los Angeles-Long Beach-Anaheim MSA | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | Largest percentage decline of any sector; office-adjacent lunch demand risk. |
| M27 | Professional and business services employment, 12-month change | -5.2 thousand (-0.5%) | jobs / percent | Sep 2025 to Sep 2026 | Los Angeles-Long Beach-Anaheim MSA | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | White-collar contraction, smaller than the prior vintage reported. |
| M28 | Manufacturing employment, 12-month change | -5.4 thousand (-1.2%) | jobs / percent | Sep 2025 to Sep 2026 | Los Angeles-Long Beach-Anaheim MSA | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) |  |
| M29 | Trade, transportation and utilities employment, 12-month change | +2.9 thousand (+0.3%) | jobs / percent | Sep 2025 to Sep 2026 | Los Angeles-Long Beach-Anaheim MSA | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | Includes the port/logistics complex. Sign flipped from the superseded vintage. |
| M30 | Financial activities employment, 12-month change | -5.1 thousand (-1.7%) | jobs / percent | Sep 2025 to Sep 2026 | Los Angeles-Long Beach-Anaheim MSA | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) |  |
| M31 | Construction employment, 12-month change | +0.1 thousand (0.0%) | jobs / percent | Sep 2025 to Sep 2026 | Los Angeles-Long Beach-Anaheim MSA | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | Flat. Rebuild demand after the 2025 fires is not visible as construction job growth in this release. |
| M32 | Government employment, 12-month change | -8.4 thousand (-1.1%) | jobs / percent | Sep 2025 to Sep 2026 | Los Angeles-Long Beach-Anaheim MSA | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | Sign flipped from the superseded vintage. |

## Wages

| ID | Metric | Value | Unit | Period | Geography | Status | Source | Note |
|---|---|---|---|---|---|---|---|---|
| M33 | Average weekly wage, all industries | $1,704 | USD/week | Q1 2026 | Los Angeles County | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | Los Angeles County, QCEW. US average $1,654; metro area $1,721; Orange County $1,766. |
| M34 | Employment Cost Index, 12-month change | +3.9% | percent | Sep 2026 | Los Angeles-Long Beach CSA | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | Los Angeles-Long Beach CSA, ECI. US +3.1%. Updated from the superseded Jun 2026 figure (+2.8%). |

## Prices

| ID | Metric | Value | Unit | Period | Geography | Status | Source | Note |
|---|---|---|---|---|---|---|---|---|
| M35 | CPI-U, all items, 12-month change | +3.7% | percent | Sep 2026 | Los Angeles metro area | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | Los Angeles metro CPI-U, all items. US +3.7%. Reference rate for CPI-linked rent escalators. Updated from the superseded Aug 2026 figure (+3.6%). |
| M36 | CPI-U, food, 12-month change | +2.8% | percent | Sep 2026 | Los Angeles metro area | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | Los Angeles metro CPI-U, food. US +2.5%. |
| M37 | CPI-U, energy, 12-month change | +20.3% | percent | Sep 2026 | Los Angeles metro area | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | Los Angeles metro CPI-U, energy. US +20.4%. Relevant to NNN operating-cost pass-throughs. |

## Consumer demand

| ID | Metric | Value | Unit | Period | Geography | Status | Source | Note |
|---|---|---|---|---|---|---|---|---|
| M38 | Total accommodation and food services sales | $17,366,966 thousand | USD | 2022 (Economic Census) | City of Los Angeles | VERIFIED | [S2](https://www.census.gov/quickfacts/fact/table/losangelescitycalifornia,lacountycalifornia/PST045224) | Latest Economic Census year available in QuickFacts. |
| M39 | Average annual household expenditures - shelter/housing | $33,016 | USD/year | 2025 | West region (Census West) | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | West region, Consumer Expenditure Survey. US $27,790. Updated from the superseded 2023-24 table. |
| M40 | Average annual household expenditures - food | $12,447 | USD/year | 2025 | West region (Census West) | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | West region, Consumer Expenditure Survey. US $10,633. Updated from the superseded 2023-24 table. |
| M41 | Average annual household expenditures - transportation | $14,110 | USD/year | 2025 | West region (Census West) | VERIFIED | [S1](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf) | West region, Consumer Expenditure Survey. US $13,492. Car dependency supports drive-thru formats. |
| M42 | Median household income (county comparison) | $90,112 | USD | 2020-2024 ACS 5-yr | Los Angeles County | VERIFIED | [S2](https://www.census.gov/quickfacts/fact/table/losangelescitycalifornia,lacountycalifornia/PST045224) | Los Angeles County median household income (2024 dollars); city is $81,939. Geography field updated. |

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
| M63 | City of Los Angeles local minimum wage | $18.42 | USD/hour | effective 2026-07-01 | City of Los Angeles | VERIFIED | [S25](https://wagesla.lacity.gov/) | City of Los Angeles minimum wage, Office of Wage Standards. Indexed annually to CPI-W; higher than the $20.00 fast-food minimum applies only if the local rate exceeds it. |

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
| M88 | Net loss attributable to Jack in the Box Inc. (FY2025) | -$80.7 million | USD | FY ended 2025-09-28 | Company | VERIFIED | [S9](https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm) | Consolidated statements of operations, FY2025. FY2024 was a $36.7M net loss. |
| M89 | Total stockholders' deficit | -$938.3 million | USD | 2025-09-28 | Company | VERIFIED | [S9](https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm) | Balance sheet: total liabilities exceed total assets. This is the tenant-credit fact that matters most to a landlord. |
| M90 | Total stockholders' deficit (updated) | -$901.3 million | USD | 2026-07-05 | Company | VERIFIED | [S24](https://www.sec.gov/Archives/edgar/data/807882/000080788226000091/jack-20260705.htm) | Q3 FY2026 10-Q. Deficit narrowed after the Del Taco sale closed, but remains negative. |
| M91 | Long-term debt, net of current maturities | $1,428.7 million | USD | 2026-07-05 | Company | VERIFIED | [S24](https://www.sec.gov/Archives/edgar/data/807882/000080788226000091/jack-20260705.htm) | Down from $1,674.5M at 2025-09-28; the Del Taco proceeds and cash flow went to debt paydown. |
| M92 | Systemwide sales, Jack in the Box | $4,208.9 million | USD | FY2025 | Company | VERIFIED | [S9](https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm) | Down from $4,396.3M in FY2024. System same-store sales -4.2% in FY2025, -7.4% in Q4 FY2025. |
| M93 | Net (loss) earnings, three quarters to 2026-07-05 | $27.9 million | USD | FY2026 YTD to 2026-07-05 | Company | VERIFIED | [S24](https://www.sec.gov/Archives/edgar/data/807882/000080788226000091/jack-20260705.htm) | Returned to profit after the Del Taco loss on sale and discontinued operations were separated out. |
| M94 | Jack in the Box restaurants in California | 941 | restaurants | 2025-09-28 | California | VERIFIED | [S9](https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm) | Company-operated 96; franchise 845. California is the largest single state for the brand. |

## Hazard

| ID | Metric | Value | Unit | Period | Geography | Status | Source | Note |
|---|---|---|---|---|---|---|---|---|
| M76 | Eaton Fire - area burned | 14,021 | acres | Jan 2025 | Los Angeles County | VERIFIED | [S13](https://file.lacounty.gov/SDSInter/lac/1199046_Eaton_Palisades_Fires_Anniversary_Fact_Sheet.pdf) | Structures destroyed 9,414; damaged 1,074; 19 confirmed fatalities. |
| M77 | Palisades Fire - area burned | 23,448 | acres | Jan 2025 | Los Angeles County | VERIFIED | [S13](https://file.lacounty.gov/SDSInter/lac/1199046_Eaton_Palisades_Fires_Anniversary_Fact_Sheet.pdf) | Structures destroyed 6,837; damaged 973; 12 confirmed fatalities. |
| M78 | Estimated economic output lost - 2025 fire pair | $5.2 billion to $10.1 billion | USD | 2025 | Los Angeles County | VERIFIED | [S13](https://file.lacounty.gov/SDSInter/lac/1199046_Eaton_Palisades_Fires_Anniversary_Fact_Sheet.pdf) | County-published estimate range. |
| M79 | Businesses impacted - 2025 fire pair | ~6,800 | businesses | 2025 | Los Angeles County | VERIFIED | [S13](https://file.lacounty.gov/SDSInter/lac/1199046_Eaton_Palisades_Fires_Anniversary_Fact_Sheet.pdf) | Workers impacted ~47,000. |
| M80 | Labor income lost - 2025 fire pair | $2.2 billion to $4.2 billion | USD | 2025 | Los Angeles County | VERIFIED | [S13](https://file.lacounty.gov/SDSInter/lac/1199046_Eaton_Palisades_Fires_Anniversary_Fact_Sheet.pdf) |  |
| M81 | Tax revenue losses - 2025 fire pair | $900 million to $1.6 billion | USD | 2025 | Los Angeles County | VERIFIED | [S13](https://file.lacounty.gov/SDSInter/lac/1199046_Eaton_Palisades_Fires_Anniversary_Fact_Sheet.pdf) | Directly relevant to municipal service capacity and to future parcel-tax and assessment pressure. |
| M82 | Fire Hazard Severity Zone classification of the subject parcel | **(blank - unverified)** | zone | 2026 | Subject property | UNVERIFIED | [S17](https://osfm.fire.ca.gov/what-we-do/community-wildfire-preparedness-and-mitigation/fire-hazard-severity-zones) | Requires parcel-level lookup in the CAL FIRE FHSZ viewer plus LAFD/LACoFD local maps. Central Los Angeles flatland is generally outside SRA very-high zones, but this is NOT asserted here. |
| M83 | Seismic site classification and fault-rupture zone | **(blank - unverified)** | classification | 2026 | Subject property | UNVERIFIED | [S18](https://www.usgs.gov/programs/earthquake-hazards) | Requires the CGS EQ Zapp / Alquist-Priolo maps and a geotechnical report. Blank by rule. |
| M84 | FEMA flood zone | **(blank - unverified)** | zone | effective FIRM | Subject property | UNVERIFIED | [S19](https://msc.fema.gov/portal/home) | Requires a parcel-level NFHL lookup. Blank by rule. |
| M85 | Property insurance availability and premium | **(blank - unverified)** | USD / terms | 2026 | Subject property | UNVERIFIED | [S20](https://www.insurance.ca.gov/01-consumers/200-wrr/California-FAIR-Plan.cfm) | No official published rate for a commercial parcel. Must be quoted by a broker; FAIR Plan is residential-oriented and does not solve commercial wildfire capacity. |

## Totals

- Rows: 94
- Verified: 87
- Blank / unverified: 7
- Sources: 25

