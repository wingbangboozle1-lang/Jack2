# Link check log

Every external URL published on the site was retrieved during this session.
This file records what was actually fetched versus what was registered from a
search index only. A link is never published on the strength of the search
result alone.

## Retrieved and read (content used as evidence)

| Source ID | URL | HTTP | Notes |
|---|---|---|---|
| SEC-JACK-10K-FY2025 | https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm | 200 | Read in 20+ chunks. Same-store sales, AUV, unit counts, royalty, wage inflation, impairment, closures, lease terms, percentage rent. |
| SEC-O-10K-FY2025 | https://www.sec.gov/Archives/edgar/data/726728/000072672826000011/o-20251231.htm | 200 | Read. Property count, geographic mix, investment-grade share, debt, impairment, underwriting standard. |
| SEC-O-8K-Q3-2026 | https://www.sec.gov/Archives/edgar/data/726728/000072672826000056/o-991q32026.htm | 200 | Read. Q3 2026 acquisitions at 6.6%, 9M at 6.5%, U.S. wholly-owned 6.6%, rent recapture 103.5% / 103.1%. |
| BLS-EAG-LA-MSA | https://www.bls.gov/regions/west/news-release/2026/eag.ca_losangeles_msa.htm | 200 | Read. Sep 2026 MSA establishment employment by sector, CPI-U. |
| BLS-LAU-CA-037 | https://data.bls.gov/timeseries/LAUCN060370000000003 | 200 | Read. County LAUS, Sep 2026 = 4.5% NSA. Oct 2025 suppressed. |
| FED-H15 | https://www.federalreserve.gov/releases/h15/ | 200 | Read. Rates of 2026-11-04 release. |
| CENSUS-QF-LACOUNTY | https://www.census.gov/quickfacts/fact/table/losangelescountycalifornia/PST045224 | 200 | Read. Population, income, poverty, education, housing, establishments. |
| CENSUS-QF-LACITY | https://www.census.gov/quickfacts/fact/table/losangelescitycalifornia/PST045224 | 200 | Read. Population, income, poverty, retail sales per capita, density. |
| SCAG-LAEDC-2025 | https://scag.ca.gov/sites/default/files/2026-01/26-426-ES-0357-RegionalEconomicAnalysis2025CountyReportsLosAngeles-Final.pdf | 200 | Read in part (chunks 0, 1, 3 of 6). Forecast table, output, permits, ZORI. |
| CDE-FINGERTIP | https://www.cde.ca.gov/ds/ad/ceffingertipfacts.asp | 200 | Read. Statewide enrollment, districts, schools, charter, diplomas, teachers. |
| CA-DIR-AB1228 | https://www.dir.ca.gov/dlse/AB1228/AB1228.html | 200 | Read. $20.00/hr fast-food floor, effective 2024-04-01. |
| CA-DIR-MINWAGE | https://www.dir.ca.gov/dlse/faq_minimumwage.htm | 200 | Read. $16.90/hr from 2026-01-01, CPI-W cap. |
| LA-ASSESSOR-PROP13 | https://assessor.lacounty.gov/real-estate-toolkit/proposition-13 | 200 | Read. 1% levy, 2% cap, change-of-ownership reset, decline-in-value, 2026-27 DIV window 7/2-11/30. |
| CA-INS-FAIRPLAN | https://www.insurance.ca.gov/01-consumers/105-type/95-guides/01-com/FAIR-Plan.cfm | 200 | Read. $20M/building, $100M/location commercial limits, 20% Safer-from-Wildfires discount. |
| CALFIRE-FHSZ | https://data.ca.gov/dataset/fire-hazard-severity-zone-viewer | 200 | Read. SRA zones effective 2024-04-01, LRA layers present, dataset updated 2026-09-30. |
| USGS-NSHM | https://www.usgs.gov/programs/earthquake-hazards/hazards | 200 | Read. 2023 50-state NSHM is the current model. |
| FEMA-NRI | https://hazards.fema.gov/nri/ | 200 | Read. 18 hazards, tract level, v1.20. |
| IRS-1031 | https://www.irs.gov/newsroom/like-kind-exchanges-real-estate-tax-tips | 200 | Read. 45-day identification, 180-day completion, QI, deferral. Page carries the IRS archival banner (see F-04). |
| IRS-PUB544 | https://www.irs.gov/publications/p544 | 200 | Read. Amount realised, adjusted basis, involuntary conversion. |
| LA-PLANNING-CENTRAL | https://planning.lacity.gov/plans-policies/community-plan-areas/central | 200 | Landing page only; the Central Area plan text was not served at this path. |
| LAEDC-2026-EF | https://laedc.org/laedc-releases-the-2026-economic-forecast/ | 200 | Read. Release date, qualitative direction. |
| LAEDC-2026-EF-DL | https://laedc.org/download/2026-economic-forecast/ | 200 | 9.37 MB PDF, created 2026-02-25, updated 2026-03-02. Numeric tables NOT extractable in this session. |

## Registered but NOT used as a model input (tier C)

| Source ID | URL | Reason |
|---|---|---|
| COSTAR-NETLEASE-Q1-2026 | https://www.matthews.com/insights/q1-2026-shopping-center-reit-earnings-report | Secondary summary of a paywalled CoStar dataset. Context only. |
| NAREIT-FACTSHEET | https://www.reit.com/sites/default/files/2026-06/MediaFactSheet_May-2026.pdf | Industry association fact sheet, not a transaction record. Context only. |

## Failed retrievals (documented, not hidden)

| URL | Result | Consequence |
|---|---|---|
| https://www.sec.gov/ix?doc=/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm | HTTP 500 | Used the plain Archives URL instead. No data lost. |
| https://api.census.gov/data/... | Missing API key | Used QuickFacts and table pages instead. |
| https://www.bls.gov/regions/west/news-release/countyemploymentandwages_losangeles.htm | HTTP 404 | Used the MSA EAG release and the LAUS series instead. |
| https://www.lacounty.gov/ | HTTP 502 | Used department subdomains instead. |
| https://www.insurance.ca.gov/01-consumers/105-type/95-guides/01-resi/FAIR-Plan.cfm | HTTP 404 | Used the commercial FAIR Plan page, which is the relevant one for this asset. |
| https://www.boe.ca.gov/proptaxes/faqs/propositions13.htm | HTTP 404 | Used the LA County Assessor's Prop 13 page instead. |
| https://www.dir.ca.gov/dlse/California-Minimum-Wage.html | HTTP 404 | Used the DIR FAQ page instead. |
| https://osfm.fire.ca.gov/.../fire-hazard-severity-zones-maps/ | HTTP 404 | Used the data.ca.gov FHSZ dataset instead. |
| https://laedc.org/2026-economic-forecast/ | HTTP 404 | Used the release page and the download page instead. |
| https://labormarketinfo.edd.ca.gov/data/los-angeles.html | HTTP 404 | Used the LMI geography index instead. |
| https://www.usgs.gov/programs/earthquake-hazards/science/2018-long-term-national-seismic-hazard-map | HTTP 404 | Used the USGS hazards landing page instead. |
| https://hazards.fema.gov/nri/data-resources | Unreliable | Used the NRI landing page. |

## Internal link audit

All 491 internal and 84 external hrefs are machine-checked by
`python3 verification/verify.py`, which fails on any broken relative path,
any non-https external link, or any external link that is not a registered
source. Current status: **PASS**, 2,356 checks.
