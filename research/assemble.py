"""Assemble the curated, public-safe evidence register. Run from repository root.
Excerpts were read against issuing-organization pages on 2026-11-06.
This is NOT a live scraper. Dynamic pages must be re-reviewed before reuse.
No property identifiers, owner information, contacts, or account data are included.
"""
import json
from pathlib import Path
CHECKED = '2026-11-06'
sources = {}
def S(id, publisher, url, excerpt, kind='Government primary', note=''):
    sources[id] = dict(id=id, publisher=publisher, url=url, checked=CHECKED, kind=kind, excerpt=excerpt, note=note)
S('census','U.S. Census Bureau · QuickFacts','https://www.census.gov/quickfacts/losangelescountycalifornia',
'''Population estimates, July 1, 2025, (V2025) 9,694,934
Population estimates base, April 1, 2020, (V2025) 10,017,414
Population, percent change - April 1, 2020 (estimates base) to July 1, 2025, (V2025) -3.2%
Median households income (in 2024 dollars), 2020-2024 $90,112
Per capita income in past 12 months (in 2024 dollars), 2020-2024 $45,792
Persons in poverty, percent 13.3%
High school graduate or higher, percent of persons age 25 years+, 2020-2024 80.9%
Bachelor's degree or higher, percent of persons age 25 years+, 2020-2024 36.0%
Households, 2020-2024 3,416,449
Persons per household, 2020-2024 2.81
Median value of owner-occupied housing units, 2020-2024 $834,200
Median gross rent, 2020-2024 $1,954
Building Permits, 2025 22,250
Mean travel time to work (minutes), workers age 16 years+, 2020-2024 30.4
Population per square mile, 2020 2,466.9
Land area in square miles, 2020 4,059.28
Total employer establishments, 2023 304,988
Total accommodation and food services sales, 2022 ($1,000) 44,000,801
Methodology differences may exist between data sources, and so estimates from different sources are not comparable.
Different vintage years of estimates are not comparable.''',note='County proxy only. ACS figures are five-year estimates; population is V2025. Do not compare ACS income with BEA per-capita income as if definitions match.')
S('edd','California Employment Development Department','https://labormarketinfo.edd.ca.gov/file/lfmonth/la$pds.pdf',
'''Los Angeles-Long Beach-Glendale Metropolitan Division (Los Angeles County)
The seasonally adjusted unemployment rate in Los Angeles County decreased over the month to 4.8 percent in September 2026 from a revised rate of 5.0 in August 2026 and was below the rate of 5.6 percent a year ago.
The unadjusted unemployment rate for the county was 4.5 percent in September 2026.
Between August 2026 and September 2026, total nonfarm employment in Los Angeles County decreased by 4,100 to 4,539,800.
Between September 2025 and September 2026, total nonfarm employment in Los Angeles County increased by 20,300 or 0.4 percent.
Leisure and hospitality added 8,900 jobs over the year. Accommodation and food services (up 8,600) boosted the employment levels, with additions mainly centered in restaurants and other eating places (up 7,300).
Leading the year-over industry job losses was information (down 10,200).
Other industries that registered year-over reductions include government (down 7,800), manufacturing (down 4,100), financial activities (down 4,000), and professional and business services (down 3,500).''',note='Release dated October 16, 2026; September preliminary. The PDF distinguishes seasonally adjusted household rates from not-seasonally-adjusted payroll levels. Do not mix them.')
S('dof','California Department of Finance, hosted by Caltrans','https://dot.ca.gov/-/media/dot-media/programs/transportation-planning/documents/division-transportation-planning/transportation-economics/los-angeles-county-presentation-2026-v2-a11y.pdf',
'''Los Angeles County Demographic and Economic Profile and Long-Run Forecast
Los Angeles County Population Forecast
2030 9.87 0.0
2035 9.84 -0.1
Los Angeles County and California Unemployment Rate Forecast
2030 5.7 5.3
2035 5.3 4.9
Los Angeles County Nonfarm Payroll Forecast
2030 4700000 0.4
2035 4850000 0.6
Los Angeles County and California Per Capita Income
2030 85 91
2035 89 97
Starting in 2030, the average growth rate over the five-year period (for example: 2026-2030) is shown
Starting in 2030, the average unemployment rate over the five-year period (for example: 2026-2030) is shown.
Starting in 2030, the average per capita income over the five-year period (for example: 2026-2030) is shown.
Per capita income figures are in 2024 dollars and are deflated using the statewide California Consumer Price Index for All Urban Consumers (CPI-U).
Forecast by the California Department of Finance, Economic Research Unit.''',note='Official 2026 long-run county forecast. Values are rounded as displayed in the PDF, not independently reproduced from the underlying XLSX. Forecast levels are not observations. Payroll-level discontinuity is flagged; only published growth rates enter the contextual model.')
S('forecast-method','Caltrans · Long-Term Socio-Economic Forecasts','https://dot.ca.gov/programs/transportation-planning/division-of-transportation-planning/state-planning/transportation-economics/long-term-socio-economic-forecasts-by-county',
'''Beginning in 2026, Socioeconomic Forecasts are produced by the Department of Finance (DOF) using a revised methodology. Forecasts published prior to 2026 use a different methodology and are not fully comparable.''')
S('bea','U.S. Bureau of Economic Analysis','https://www.bea.gov/news/2026/gross-domestic-product-county-and-personal-income-county-2024',
'''In 2024, the total level of personal income ranged from $818.5 billion in Los Angeles County, CA, to $10.6 million in Loving County, MS.
The estimates for 2024 incorporate the results of BEA's annual updates of GDP and personal income by county that were released today.
BEA released new estimates of per capita personal income for 2024.'''.replace('Loving County, MS','Loving County, TX'),note='Release February 5, 2026. Total personal income is not median household income and is not restaurant revenue.')
S('edd-profile','California EDD · Los Angeles County Profile','https://labormarketinfo.edd.ca.gov/cgi/databrowsing/localareaprofileqsresults.asp?countyname=&geogarea=0604000037&menuchoice=localareapro&selectedarea=Los+Angeles+County&selectedindex=1&state=true',
'''Cooks, Restaurant | 2023 - 2033 | 40,760 | 54,070 | 13,310 | 32.7
Home Health & Personal Care Aides | 2023 - 2033 | 289,930 | 390,820 | 100,890 | 34.8
Data Scientists | 2023 - 2033 | 7,320 | 9,790 | 2,470 | 33.7
Located on the southern coast of the state, Los Angeles County covers over 4,000 square miles''',note='Live profile showed 2023–2033 occupational projections, superseding older 2022–2032 search excerpts. Occupational demand is not a forecast of this restaurant’s sales.')
S('ucla','UCLA Anderson Forecast','https://www.anderson.ucla.edu/news-and-events/ucla-anderson-forecast-says-oil-shock-has-replaced-tariffs-leading-risk-us-economy',
'''June 3, 2026
California continues to outpace the U.S. in output and income growth, but its labor market remains weak
Unemployment Rates (Annual Averages)
2026: 5.5%
2027: 5.1%
2028: 4.2%
Non-Farm Payroll Jobs
2026: 1.2%
2027: 1.5%
2028: 2.0%
Real Personal Income Growth
2026: 2.3%
2027: 2.4%
2028: 2.5%
The baseline forecast does not call for recession, but it does anticipate slower growth, higher inflation and a Federal Reserve with little room to cut interest rates.''',kind='University economic forecast',note='California statewide, not county or property. June assumptions predate the October FOMC decision; not a current rate forecast.')
S('cpi-local','U.S. Bureau of Labor Statistics · Los Angeles area CPI','https://www.bls.gov/regions/west/news-release/consumerpriceindex_losangeles.htm',
'''Consumer Price Index, Los Angeles area — September 2026
The Los Angeles area all items CPI-U increased 3.7 percent for the 12 months ending in September. The index for all items less food and energy increased 2.6 percent over the year. Food prices advanced 2.8 percent. Energy prices advanced 20.3 percent.
Food away from home advanced 2.8 percent.
Gasoline prices increased 30.8 percent.
The Los Angeles-Long Beach-Anaheim, CA Core Based Statistical Area includes Los Angeles and Orange Counties in California.
The October 2025 data values are not available due to the 2025 lapse in appropriations.
The October 2026 Consumer Price Index for the Los Angeles area is scheduled to be released on November 10, 2026.''',note='Released October 14, 2026. Monthly regional CPI; not a county-only index. September is the latest observation checked as of November 6.')
S('cpi-us','U.S. Bureau of Labor Statistics · National CPI','https://www.bls.gov/news.release/cpi.htm',
'''CONSUMER PRICE INDEX - SEPTEMBER 2026
Over the last 12 months, the all items index increased 3.7 percent before seasonal adjustment.
The food away from home index rose 3.5 percent over the last year.
The energy index increased 20.4 percent for the 12 months ending September.''',note='Archived release content checked October 14, 2026; the live URL can roll forward.')
S('fed','Board of Governors of the Federal Reserve System','https://www.federalreserve.gov/newsevents/pressreleases/monetary20261028a.htm',
'''October 28, 2026
The Committee decided to maintain the target range for the federal funds rate at 3-3/4 to 4 percent
Inflation remains elevated.''',note='Policy target, not a commercial-property loan rate or discount rate.')
S('freddie','Freddie Mac · Primary Mortgage Market Survey','https://www.freddiemac.com/pmms',
'''U.S. weekly mortgage rate averages as of 11/05/2026
30-year Fixed-Rate Mortgage 7.18%
15-year Fixed-Rate Mortgage 6.57%
The criteria include weekly conventional, single-family originations with conforming loan limits as set by FHFA.''',kind='Government-sponsored enterprise primary',note='Residential affordability/financing context only; not a quote for NNN commercial financing.')
S('jack-10k','Jack in the Box Inc. · FY2025 Form 10-K, SEC','https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm',
'''FOR THE FISCAL YEAR ENDED SEPTEMBER 28, 2025
As of September 28, 2025, Jack in the Box operated and franchised 2,136 quick-service restaurants
Of those total Jack in the Box restaurants at fiscal year-end, 1,986, or 93%, were franchised.
approximately 70% of our systemwide restaurants are located in the states of California and Texas.
Site selection for all new Jack in the Box and Del Taco restaurants is made after an economic analysis and a review of demographic data and other information relating to population density, traffic, competition, restaurant visibility and access, available parking, surrounding businesses, and opportunities for market penetration.
The franchise agreement generally provides for an initial franchise fee of $50,000 per restaurant for a 20-year term
Our insurance may not provide adequate levels of coverage against claims.
under certain environmental laws, we could be held liable as an owner or operator to address any remaining contamination''',kind='Issuer SEC filing',note='Filed November 19, 2025. Brand-level evidence, not the subject operator’s financial statements. Franchise term is not the real-estate lease term.')
S('jack-q3','Jack in the Box Inc. · Q3 FY2026 Form 10-Q, SEC','https://www.sec.gov/Archives/edgar/data/807882/000080788226000091/jack-20260705.htm',
'''As of July 5, 2026, we operated and franchised 2,115 restaurants
Franchise | (1.2 %) | (7.2 %) | (4.4 %) | (3.3 %)
System | (1.1 %) | (7.1 %) | (4.2 %) | (3.3 %)
Closed | (2) | (38) | (40) | (11) | (28) | (39)
End of period | 149 | 1,966 | 2,115
Franchised restaurant AUVs | $ | 431 | $ | 426 | $ | 1,427 | $ | 1,460
Franchise rental revenues decreased $3.5 million, or 4.6% in the quarter and $17.7 million, or 6.8% year-to-date
The year-to-date increase is due to increases in bad debt expense of $2.4 million
a decrease in cash flows of approximately $11.0 million resulting from delayed payments from franchisees, including amounts subject to payment deferral arrangements, a portion of which we have reserved against.
As of July 5, 2026, the Company had $71.8 million of cash and restricted cash
available borrowings of $54.6 million under its $150.0 million Variable Funding Notes.
issued $500.0 million of its Series 2026-1 7.624% Fixed Rate Senior Secured Notes
The Company has a leverage ratio of greater than 5.0x
As of July 5, 2026, the Senior ABS Leverage Ratio is greater than 5.25x
As of July 5, 2026, we were in compliance with all of our debt covenant requirements and were not subject to any rapid amortization events.
cash flows from operations have been impacted and may continue to be impacted by franchisee payment delays and deferrals.''',kind='Issuer SEC filing',note='Filed August 12, 2026; 12-week quarter and 40-week year-to-date ended July 5, 2026. AUV table is in thousands of dollars. No later 10-K/10-Q appeared in the SEC list checked. Brand credit is not tenant credit.')
S('sec-list','U.S. SEC · Jack in the Box periodic filing list','https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000807882&type=10-&dateb=&owner=include&count=10',
'''10-Q | 2026-08-12
10-K | 2025-11-19''',kind='Government filing index',note='Used to select the latest available annual and quarterly filings; not evidence about the subject lease.')
S('school','California Department of Education · School Dashboard','https://www.caschooldashboard.org/reports/19647330000000/2025/academic-engagement',
'''Los Angeles Unified
86.5% graduated
Four Year = 84.6%
Five Year = 1.8%
5-Year Graduation Rate 86.5%
2019 | 2022 | 2023 | 2024 | 2025
Graduation Rate | 82.1% | 86% | 83.6% | 86.7% | 86.5%''',note='2025 Dashboard report checked. LAUSD is a contextual district, not an asserted assignment for the subject property. School attendance boundaries do not establish restaurant demand.')
S('metro','Los Angeles County Metropolitan Transportation Authority','https://www.metro.net/projects/westside/',
'''Section 1 extends the subway from Koreatown to the Wilshire/La Cienega area
This Opened on May 8, 2026.
Section 2 remains active in Beverly Hills and Century City
Section 3 continues construction in Westwood
Lane reductions and temporary pedestrian detours may occur
Business Interruption Fund''',note='Agency project page checked November 6, 2026. No property-specific travel-time or value uplift inferred; remaining opening dates left blank.')
S('port','Port of Los Angeles','https://portoflosangeles.org/references/2026-news-releases/news_100926_sept_cargo',
'''The Port of Los Angeles handled 1,042,652 Twenty-Foot Equivalent Units (TEUs) in September
Loaded imports reached 545,696 TEUs in September, up 19% compared with last September.
During the first nine months of 2026, the Port handled nearly 8.1 million TEUs, more than 3% ahead of the same period last year.''',note='October 9, 2026 release. Regional trade indicator, not a property catchment or rent forecast.')
S('film','FilmLA Research · Q3 2026 report','https://filmla.com/filmla-q3-report-tax-credit-projects-now-make-up-40-percent-of-scripted-on-location-filming-in-los-angeles-nearly-double-last-years-share/',
'''October 21, 2026
Overall on-location filming totaled 4,171 Shoot Days* from July through September, a 4.8 percent decrease from 4,380 during the same period last year.
Projects participating in California’s Film & Television Tax Credit Program accounted for 40.3 percent of scripted on-location filming in Greater Los Angeles during the third quarter''',kind='Original issuing organization',note='FilmLA is the original research issuer, not a government statistical agency. On-location shoot days exclude significant sound-stage activity.')
S('tourism','Los Angeles Tourism & Convention Board','https://www.discoverlosangeles.com/visitors-to-los-angeles-generated-426-billion-in-business-sales-and-supported-more-than-530000-jobs',
'''Jul 29, 2026
Los Angeles welcomed 49.5 million visitors in 2025, including 43.1 million domestic visitors and 6.4 million international visitors.
visitors generated $42.6 billion in total business sales across the region in 2025, supporting more than 530,000 jobs in the Visitor Industry throughout Los Angeles County.
The 2025 Economic Impact of Visitors to Los Angeles report was compiled by Tourism Economics, an Oxford Economics company, and Los Angeles Tourism.''',kind='Official destination organization / commissioned study',note='Promotional organization’s commissioned economic-impact estimates; business sales are not net value added. No permanent Olympics uplift assumed.')
S('fire-p','CAL FIRE · Palisades incident','https://www.fire.ca.gov/incidents/2025/1/7/palisades-fire',
'''23,448 Acres
Last Updated 04/09/2026 8:20 AM
975 Structures Damaged
6,845 Structures Destroyed
12 Confirmed Civilian Fatalities''',note='Current incident-page counts differ from the County anniversary snapshot; both vintages are disclosed, not averaged.')
S('fire-e','CAL FIRE · Eaton incident','https://www.fire.ca.gov/incidents/2025/1/7/eaton-fire',
'''14,021 Acres
Last Updated 08/06/2026 10:47 AM
1,076 Structures Damaged
9,419 Structures Destroyed
19 Confirmed Civilian Fatalities''',note='Current incident-page counts differ from the County anniversary snapshot; neither establishes the subject property’s hazard exposure.')
S('fire-county','Los Angeles County · fire anniversary fact sheet','https://file.lacounty.gov/SDSInter/lac/1199046_Eaton_Palisades_Fires_Anniversary_Fact_Sheet.pdf',
'''Eaton Fire
Structures destroyed (residential, commercial and other): 9,414
Structures damaged: 1,074
Palisades Fire
Structures destroyed (residential, commercial and other): 6,837
Structures damaged: 973
Economic output lost: $5.2 billion to $10.1 billion
Businesses impacted: ~6,800
Workers impacted: ~47,000''',note='Snapshot publication date not displayed in the extracted PDF; do not treat as current incident counts. Economic estimates are not independently reproduced.')
S('usgs','U.S. Geological Survey · UCERF3, Fact Sheet 2015–3009','https://pubs.usgs.gov/fs/2015/3009/pdf/fs2015-3009.pdf',
'''the likelihood of having one or more such earthquakes in the next 30 years (starting from 2014).
Los Angeles region
6.7 | 40 | (2.1) | 60% (0.8) | 1.1
7 | 61 | (2.0) | 46% (0.7) | 1.2
7.5 | 109 | (1.3) | 31% (0.9) | 1.3
These values include aftershocks.''',note='Regional 2014–2043 model probability, not a fresh 2026–2056 probability, not an earthquake prediction, and not a probability of damage to this building.')
S('osfm','California Office of the State Fire Marshal','https://osfm.fire.ca.gov/what-we-do/community-wildfire-preparedness-and-mitigation/fire-hazard-severity-zones',
'''Fire Hazard Severity Zone maps evaluate “hazard,” not “risk”.
Contact your local jurisdiction for information on a specific area that is located in the Local Responsibility Area.
2025 LRA FHSZ Rollout- All Counties
2026 State Responsibility Area (SRA) Fire Hazard Severity Zone Public Comment Period Is Now Open.''',note='Parcel zone and locally adopted designation remain unknown. Draft SRA updates are not treated as adopted parcel classifications.')
S('fema','FEMA · Flood-map products and tools','https://www.fema.gov/flood-maps/products-tools',
'''The FEMA Flood Map Service Center (MSC) is the official source for National Flood Insurance Program flood hazard information.
The National Flood Hazard Layer is a geospatial database showing effective flood maps.
The Risk Index is an online mapping application that visualizes natural hazard risk metrics based on 18 natural hazards''',note='Method and official lookup only. No flood zone, expected annual loss, or insurance requirement inferred for the unidentified property.')
S('insurance','California Department of Insurance','https://www.insurance.ca.gov/0400-news/0100-press-releases/2026/release005-2026.cfm',
'''For Release: February 2, 2026
$22.4 billion distributed since January 2025
The Make It FAIR Act would improve coverage and claims handling by the insurance company-run FAIR Plan.
extended non-renewal protections for businesses''',note='Regulator announcement about proposed/enacted reform; not confirmation of this property’s coverage, premium, or claim outcome.')
S('wage','California Department of Industrial Relations','https://www.dir.ca.gov/dlse/Fast-Food-Minimum-Wage-FAQ.htm',
'''Starting April 1, 2024, all “fast food restaurant employees” who are covered by the new law must be paid at least $20.00 per hour.
The law applies only to employees of “fast food restaurants.”
The restaurant must be part of a restaurant chain of at least 60 establishments nationwide.
AB 1228 applies to employers of “fast food restaurant employees” regardless of whether the employer is the business entity that owns the national brand, or a franchisee or licensee of that national brand.
The hourly minimum wage established by the Council can increase every year by either 3.5% or the increase in the consumer price index, whichever is smaller.''',note='FAQ explains the initial floor and adjustment authority, not a complete current local wage schedule. Confirm applicable current rate before underwriting tenant payroll.')
S('wage-general','California Department of Industrial Relations','https://www.dir.ca.gov/dlse/faq_minimumwage.htm',
'''Effective January 1, 2026, the minimum wage is $16.90 per hour for all employers, not otherwise covered by a higher minimum wage specific to an industry or a locality.''')
S('boe','California Board of Equalization','https://www.boe.ca.gov/proptaxes/faqs/changeinownership.htm',
'''Proposition 13 requires the county assessor to reassess the property to its current fair market value as of the date ownership changed.
The creation of a leasehold interest in taxable real property for a term of 35 years or more (including written renewal options).''',note='A sale and some long leases/extensions can have assessment consequences. Actual tax impact requires the existing term, options, structure and assessor review.')
S('ula','City of Los Angeles Office of Finance','https://finance.lacity.gov/faq/measure-ula',
'''Effective for transactions closing after June 30, 2026, the new ULA thresholds will be $5,400,000 and $10,900,000.
4% for properties conveyed over $5,400,000, but under $10,900,000
5.5% for properties conveyed at $10,900,000 or more
The present tax (“Base Tax”) is computed based on the consideration or value of the real property interest conveyed at a rate of 0.45%.
The ULA Tax is imposed on all documents that convey real property within the City of Los Angeles''',note='Only if the parcel is in the City of Los Angeles. Central LA was not defined well enough to establish jurisdiction. County charges, exemptions and closing-date thresholds require separate review.')
S('irs','Internal Revenue Service · 2025 Form 8824 instructions','https://www.irs.gov/pub/irs-pdf/i8824.pdf',
'''The replacement property for the exchange must be identified within 45 days after the property being given up is transferred.
The replacement property must be received within 180 days, or by the due date of your tax return (including extensions), whichever is earlier.
section 1031 like-kind exchange treatment applies only to exchanges of real property held for use in a trade or business or for investment, other than real property held primarily for sale.''',note='Federal tax-differral framework only, not personal tax advice; depreciation recapture, state conformity, boot and basis are not calculated.')
S('zoning','City of Los Angeles Department of City Planning','https://zoning.lacity.gov/faq/general-questions/how-do-i-determine-zoning-property',
'''You can find the zoning for a property by using the Zoning Information and Map Access System (ZIMAS)
During this transition period, both the New Zoning Code and the Original Zoning Code will be in effect in different parts of the City.''',note='Official lookup method, not a parcel zoning determination. Applies only within the City.')
S('caltrans','California Department of Transportation','https://dot.ca.gov/programs/traffic-operations/census/traffic-volumes',
'''Annual average daily traffic is the total volume for the year divided by 365 days.
The resulting counts are adjusted to an estimate of annual average daily traffic by compensating for seasonal influence, weekly variation and other variables''',note='State-highway counts; local-road counts require the relevant public-works agency. Passing traffic is not verified site access or customer traffic.')

findings=[]
def F(id, category, metric, value, period, geography, source, quote, implication, status='Source-checked data', note=''):
    findings.append(dict(id=id, category=category, metric=metric, value=value, period=period, geography=geography, source_id=source, quote=quote, implication=implication, status=status, note=note))
F('E01','Demographics','Population estimate','9,694,934','2025-07-01 · V2025','Los Angeles County','census','9,694,934','Large regional market; does not establish a trade-area customer count.')
F('E02','Demographics','Population change from estimates base','−3.2%','2020-04-01 to 2025-07-01','Los Angeles County','census','-3.2%','Do not underwrite rent growth from an assumption of uninterrupted population growth.')
F('E03','Demographics','Households','3,416,449','2020–2024 ACS','Los Angeles County','census','3,416,449','County scale is not a substitute for a site-specific daytime and residential catchment.')
F('E04','Demographics','Persons per household','2.81','2020–2024 ACS','Los Angeles County','census','2.81','Household composition matters, but no customer mix is inferred.')
F('E05','Income & spending','Median household income','$90,112','2020–2024 · 2024 dollars','Los Angeles County','census','$90,112','Assess value-menu affordability; county median hides neighborhood variation.')
F('E06','Income & spending','Per capita income · ACS','$45,792','2020–2024 · 2024 dollars','Los Angeles County','census','$45,792','Different definition from BEA personal income; not directly interchangeable.')
F('E07','Income & spending','Persons in poverty','13.3%','ACS estimate displayed in V2025 QuickFacts','Los Angeles County','census','13.3%','Price sensitivity and disposable-income pressure are relevant to tenant sales.')
F('E08','Income & spending','Total personal income','$818.5 billion','2024 · current dollars','Los Angeles County','bea','$818.5 billion','Economic scale is substantial; aggregate income is not local restaurant sales.')
F('E09','Education','High school graduate or higher','80.9%','2020–2024 ACS · age 25+','Los Angeles County','census','80.9%','Human-capital context; no direct capitalization-rate uplift inferred.')
F('E10','Education','Bachelor’s degree or higher','36.0%','2020–2024 ACS · age 25+','Los Angeles County','census','36.0%','Education can support employability, but does not establish neighborhood demand.')
F('E11','Education','LAUSD five-year graduation rate','86.5%','2025 Dashboard','Los Angeles Unified · context only','school','86.5% graduated','School quality can matter to residential reinvestment; actual assigned schools remain unknown.')
F('E12','Education','LAUSD four-year graduation component','84.6%','2025 Dashboard','Los Angeles Unified · context only','school','Four Year = 84.6%','Do not label the combined 86.5% measure as a four-year rate.')
F('E13','Employment','Unemployment rate · seasonally adjusted','4.8%','September 2026 · preliminary','Los Angeles County','edd','4.8 percent in September 2026','Improvement versus a year earlier, but not a property-level demand guarantee.')
F('E14','Employment','Unemployment rate · not seasonally adjusted','4.5%','September 2026 · preliminary','Los Angeles County','edd','4.5 percent in September 2026','Keep adjustment basis separate from the 4.8% household series.')
F('E15','Employment','Nonfarm employment · seasonally adjusted','4,539,800','September 2026 · preliminary','Los Angeles County','edd','4,539,800','Large employment base; monthly payrolls fell by 4,100.')
F('E16','Employment','Nonfarm job growth · seasonally adjusted','+20,300 / +0.4%','September 2025 to September 2026','Los Angeles County','edd','increased by 20,300 or 0.4 percent','Modest growth argues for conservative, not automatic, rent escalation.')
F('E17','Employment','Restaurants and other eating places jobs','+7,300','September 2025 to September 2026','Los Angeles County','edd','restaurants and other eating places (up 7,300)','Sector employment grew despite brand-level sales pressure; neither proves this site’s health.')
F('E18','Employment','Information sector jobs','−10,200','September 2025 to September 2026','Los Angeles County','edd','information (down 10,200)','Uneven sector activity can affect office-adjacent and daytime food demand.')
F('E19','Employment','Restaurant cooks occupational projection','40,760 → 54,070','2023–2033','Los Angeles County','edd-profile','40,760 | 54,070','Official occupational outlook supports food-service labor demand, not a sales forecast.','Official forecast')
F('E20','Employment','Restaurant cooks projected growth','+32.7%','2023–2033','Los Angeles County','edd-profile','13,310 | 32.7','Occupation growth must not be substituted for tenant revenue or rent growth.','Official forecast')
F('E21','Geography & access','Land area','4,059.28 sq mi','2020','Los Angeles County','census','4,059.28','A broad county proxy cannot identify micro-location, access, frontage, or corner quality.')
F('E22','Geography & access','Population density','2,466.9 / sq mi','2020','Los Angeles County','census','2,466.9','Density is regional context; drive-thru access and pedestrian barriers need site review.')
F('E23','Geography & access','Mean commute','30.4 minutes','2020–2024 ACS','Los Angeles County','census','30.4','Commuting patterns matter; no site traffic count is available.')
F('E24','Housing & development','Median owner-occupied home value','$834,200','2020–2024 ACS','Los Angeles County','census','$834,200','Housing wealth and affordability pressures coexist; not a commercial-property comparable.')
F('E25','Housing & development','Median gross residential rent','$1,954 / month','2020–2024 ACS','Los Angeles County','census','$1,954','Housing cost burden can constrain discretionary spending; not commercial rent.')
F('E26','Housing & development','Building permits · QuickFacts series','22,250','2025','Los Angeles County','census','22,250','Construction activity is a regional driver; series differs from the EDD profile’s permit categories.')
F('E27','Business & trade','Employer establishments','304,988','2023','Los Angeles County','census','304,988','Diversified economic base reduces dependence on one industry, but not single-tenant property risk.')
F('E28','Business & trade','Accommodation and food-services sales','$44,000,801 thousand','2022 Economic Census','Los Angeles County','census','44,000,801','Older sector-sales baseline only; not current restaurant sales.')
F('E29','Business & trade','Port container throughput','1,042,652 TEUs','September 2026','Port of Los Angeles','port','1,042,652','Trade is a support pillar; one record month does not eliminate tariff or shipping-cycle risk.')
F('E30','Business & trade','Port loaded-import growth','+19% year over year','September 2026','Port of Los Angeles','port','up 19% compared with last September','Positive logistics signal, geographically distant from an unspecified central-LA site.')
F('E31','Business & trade','On-location film shoot days','4,171 · −4.8% year over year','Q3 2026','Greater Los Angeles · FilmLA measure','film','4,171 Shoot Days* from July through September, a 4.8 percent decrease','Production-related daytime demand remains a vulnerability; sound stages are not fully captured.')
F('E32','Business & trade','Visitor volume','49.5 million','2025','Los Angeles County tourism measure','tourism','49.5 million visitors in 2025','Tourism supports demand, but benefits depend on location and visitor routes.')
F('E33','Business & trade','Visitor-generated business sales','$42.6 billion','2025','Los Angeles region · study estimate','tourism','$42.6 billion in total business sales','Commissioned gross-sales impact, not net value added or a rent-growth rate.','Official issuer estimate')
F('E34','Infrastructure','D Line Section 1','Open','Opened 2026-05-08','Wilshire corridor','metro','This Opened on May 8, 2026.','Improved regional access; no uplift assigned without the actual site and walking/driving access.')
F('E35','Infrastructure','D Line Sections 2 and 3','Under construction','Checked 2026-11-06','Beverly Hills / Century City / Westwood','metro','Section 2 remains active in Beverly Hills and Century City','Construction can interrupt access; future completion dates are not asserted.')
F('E36','Inflation & rates','All-items CPI change','+3.7% year over year','September 2026','LA–Long Beach–Anaheim MSA','cpi-local','increased 3.7 percent for the 12 months ending in September','Nominal sales growth can reflect prices rather than more customers.')
F('E37','Inflation & rates','Core CPI change','+2.6% year over year','September 2026','LA–Long Beach–Anaheim MSA','cpi-local','less food and energy increased 2.6 percent over the year','Inflation pressure persists; lease bumps may not match landlord replacement costs.')
F('E38','Inflation & rates','Food-away-from-home CPI change','+2.8% year over year','September 2026','LA–Long Beach–Anaheim MSA','cpi-local','Food away from home advanced 2.8 percent.','Menu-price inflation is not equivalent to unit sales or traffic growth.')
F('E39','Inflation & rates','Gasoline CPI change','+30.8% year over year','September 2026','LA–Long Beach–Anaheim MSA','cpi-local','Gasoline prices increased 30.8 percent.','Fuel costs can squeeze customers and deliveries; a severe consumer-pressure signal.')
F('E40','Inflation & rates','Federal funds target range','3.75%–4.00%','2026-10-28','United States','fed','3-3/4 to 4 percent','Policy-rate context only; do not use as the property discount rate.')
F('E41','Inflation & rates','30-year fixed mortgage average','7.18%','2026-11-05','United States · residential survey','freddie','7.18%','Financing and household affordability context; not a commercial loan quote.')
F('E42','Tenant & brand','Jack in the Box system restaurants','2,115','2026-07-05','Brand system · includes non-US locations','jack-q3','2,115 restaurants','Brand scale does not establish the subject tenant’s creditworthiness.')
F('E43','Tenant & brand','Franchise same-store sales','−1.2% quarter / −4.4% YTD','12 / 40 weeks ended 2026-07-05','Brand franchise system','jack-q3','Franchise | (1.2 %) | (7.2 %) | (4.4 %) | (3.3 %)','Franchise demand weakness makes unit-level rent coverage essential.')
F('E44','Tenant & brand','System same-store sales','−1.1% quarter / −4.2% YTD','12 / 40 weeks ended 2026-07-05','Brand system','jack-q3','System | (1.1 %) | (7.1 %) | (4.2 %) | (3.3 %)','Improvement from prior-year declines is not the same as positive growth.')
F('E45','Tenant & brand','Franchise average unit volume','$1.427 million YTD','$1.460 million prior-year YTD; 40 weeks','Brand franchise system','jack-q3','$ | 1,427 | $ | 1,460','AUV is not this store’s sales and is not rent coverage. Table units are thousands.')
F('E46','Tenant & brand','Year-to-date restaurant closures','40 total · 38 franchise','40 weeks ended 2026-07-05','Brand system','jack-q3','Closed | (2) | (38) | (40)','A national brand can remain operating while individual locations close.')
F('E47','Tenant & brand','Franchise rental revenue change','−4.6% quarter / −6.8% YTD','12 / 40 weeks ended 2026-07-05','Brand franchise portfolio','jack-q3','4.6% in the quarter and $17.7 million, or 6.8% year-to-date','Brand landlords are experiencing revenue pressure; review operator payment history.')
F('E48','Tenant & brand','Delayed franchise payments cash-flow effect','Approximately $11.0 million decrease','40 weeks ended 2026-07-05','Brand corporate cash flows','jack-q3','approximately $11.0 million resulting from delayed payments from franchisees','Payment deferrals are a concrete warning against relying only on the brand name.')
F('E49','Tenant & brand','New secured-note coupon','7.624%','Issued 2026-06-23','Brand corporate financing','jack-q3','7.624% Fixed Rate Senior Secured Notes','Issuer-specific financing context, not the owner’s borrowing rate or a cap rate.')
F('E50','Tenant & brand','Covenant status','Compliant; no rapid amortization event','2026-07-05','Brand corporate financing','jack-q3','we were in compliance with all of our debt covenant requirements and were not subject to any rapid amortization events.','Balance the adverse sales evidence against disclosed compliance; do not assert imminent corporate default.')
F('E51','Tenant & brand','Franchised share of restaurants','93% · 1,986 of 2,136','2025-09-28','Jack in the Box brand','jack-10k','1,986, or 93%, were franchised','Identify the actual lease obligor and guarantors; the brand may not guarantee rent.')
F('E52','Tenant & brand','California + Texas system concentration','Approximately 70%','FY2025 disclosure','Brand system','jack-10k','approximately 70% of our systemwide restaurants are located in the states of California and Texas.','California regulatory and economic conditions are material to the brand.')
F('E53','Regulation & tax','Covered fast-food initial wage floor','$20.00 / hour','Effective 2024-04-01','California · covered employers','wage','at least $20.00 per hour','Tenant labor costs affect rent coverage; confirm current applicable council/local rate before underwriting.')
F('E54','Regulation & tax','General state minimum wage','$16.90 / hour','Effective 2026-01-01','California · unless higher rule applies','wage-general','$16.90 per hour','Not the applicable floor for covered fast-food employees.')
F('E55','Regulation & tax','Ownership-change reassessment','Current fair market value','Rule checked 2026-11-06','California','boe','reassess the property to its current fair market value','Buyer underwriting and some extension structures can be affected; model actual tax consequences.')
F('E56','Regulation & tax','Lease term requiring ownership-change review','35 years or more, including written options','Rule checked 2026-11-06','California','boe','35 years or more (including written renewal options)','Do not sign a long extension without property-tax counsel.')
F('E57','Regulation & tax','Measure ULA lower / upper thresholds','$5.4 million / $10.9 million','Closings after 2026-06-30','City of Los Angeles only','ula','$5,400,000 and $10,900,000','Jurisdiction and price unknown. Additional ULA rates are 4% / 5.5%; city base tax is separate.')
F('E58','Regulation & tax','Like-kind exchange deadlines','45 days / 180 days or return due date if earlier','2025 Form 8824 instructions','Federal tax framework','irs','identified within 45 days','An exchange can defer eligible gain but adds timing and replacement-asset risk.')
F('E59','Hazards & resilience','Palisades fire area','23,448 acres','Started 2025-01-07; page updated 2026-04-09','Los Angeles County incident','fire-p','23,448 Acres','Urban-interface wildfire can cause regional displacement and insurance disruption.')
F('E60','Hazards & resilience','Palisades structures destroyed','6,845','Incident page checked 2026-11-06','Incident footprint','fire-p','6,845 Structures Destroyed','Current CAL FIRE count; County snapshot differs and is flagged.')
F('E61','Hazards & resilience','Eaton fire area','14,021 acres','Started 2025-01-07; page updated 2026-08-06','Los Angeles County incident','fire-e','14,021 Acres','A low-rainfall urban area is not immune to catastrophic fire exposure.')
F('E62','Hazards & resilience','Eaton structures destroyed','9,419','Incident page checked 2026-11-06','Incident footprint','fire-e','9,419 Structures Destroyed','Current CAL FIRE count; do not infer subject-site exposure.')
F('E63','Hazards & resilience','Fire economic output lost','$5.2–$10.1 billion','County anniversary snapshot · date not shown','Affected LA County economy','fire-county','$5.2 billion to $10.1 billion','Rare events can affect employment and spending beyond burned parcels; estimate not independently reproduced.','Official issuer estimate')
F('E64','Hazards & resilience','Regional M≥6.7 earthquake likelihood','60%','30-year model beginning 2014','USGS Los Angeles region','usgs','60% (0.8)','Material regional seismic exposure; not a building-loss probability or a fresh 2026 forecast.','Official model estimate')
F('E65','Hazards & resilience','Regional M≥7.5 earthquake likelihood','31%','30-year model beginning 2014','USGS Los Angeles region','usgs','31% (0.9)','Stress long access outages and uninsured losses, not just physical repair costs.','Official model estimate')
F('E66','Hazards & resilience','LA wildfire insurance claims paid','$22.4 billion','Since January 2025, reported 2026-02-02','Los Angeles wildfires','insurance','$22.4 billion distributed since January 2025','Insurance recovery can be substantial but coverage, exclusions, deductibles and timing remain critical.')

# Official regional projection anchors: not observations, not annual interpolation.
F('P01','Projections','County population','9.87 million','2026–2030 average level as displayed','Los Angeles County','dof','2030 9.87 0.0','Broadly flat population is not a strong automatic rent-growth thesis.','Official forecast','Rounded five-year average, not a 2030 year-end count.')
F('P02','Projections','County population','9.84 million','2031–2035 average level as displayed','Los Angeles County','dof','2035 9.84 -0.1','Long-run population does not support aggressive demand assumptions.','Official forecast','Rounded five-year average, not a 2035 year-end count.')
F('P03','Projections','Population growth rate','0.0% / −0.1% per year','2026–2030 / 2031–2035 averages','Los Angeles County','dof','2030 9.87 0.0','Use as a regional demand anchor; no direct elasticity to rent is claimed.','Official forecast','Second period excerpt: 2035 9.84 -0.1. Both lines retained in source excerpt.')
F('P04','Projections','County unemployment rate','5.7% / 5.3%','2026–2030 / 2031–2035 averages','Los Angeles County','dof','2030 5.7 5.3','Official long-run baseline is more conservative than relying on one improved month alone.','Official forecast','Second period excerpt: 2035 5.3 4.9. Not comparable to a single seasonally adjusted month.')
F('P05','Projections','Nonfarm payroll growth rate','0.4% / 0.6% per year','2026–2030 / 2031–2035 averages','Los Angeles County','dof','2030 4700000 0.4','Modest job growth supports a cautious baseline, not a guaranteed rent path.','Official forecast','Second period excerpt: 2035 4850000 0.6. Published job levels excluded due to a flagged discontinuity.')
F('P06','Projections','Real per-capita income','$85,000 / $89,000','2026–2030 / 2031–2035 averages · 2024 dollars','Los Angeles County','dof','2030 85 91','Real income improvement is a supportive counterweight to flat population.','Official forecast','Second period excerpt: 2035 89 97. PDF table units are thousands; not median household income.')
F('P07','Projections','State unemployment','5.5% → 5.1% → 4.2%','2026 → 2027 → 2028 annual averages','California · not county','ucla','2026: 5.5%','Near-term official university baseline; not a 2035 forecast.','Official forecast','Subsequent lines: 2027: 5.1%; 2028: 4.2%. June vintage.')
F('P08','Projections','State nonfarm payroll growth','1.2% → 1.5% → 2.0%','2026 → 2027 → 2028','California · not county','ucla','2026: 1.2%','State recovery assumptions differ from county long-run averages; keep both vintages visible.','Official forecast','Subsequent lines: 2027: 1.5%; 2028: 2.0%.')
F('P09','Projections','State real personal-income growth','2.3% → 2.4% → 2.5%','2026 → 2027 → 2028','California · not county','ucla','2026: 2.3%','Income growth is supportive, but cannot be mapped one-for-one into lease escalations.','Official forecast','Subsequent lines: 2027: 2.4%; 2028: 2.5%.')

property=[]
def P(id, metric, source, need, impact, priority='Critical'):
    property.append(dict(id=id, category='Property & lease', metric=metric, value='', period='', geography='[PROPERTY] · jurisdiction unverified', source_id=source, quote='', implication=impact, status='Unverified', note='Official lookup/topic source only: '+need, priority=priority))
P('U01','Exact location, parcel and governing jurisdiction','zoning','Retain identifiers privately; verify city versus unincorporated jurisdiction without publishing them.','Determines taxes, zoning, hazards and comparable sales.')
P('U02','Executed lease, amendments and side letters','jack-10k','Privately review the complete controlling documents; brand-level SEC filings do not contain the subject lease.','No reliable remaining term or renewal-right conclusion is possible.')
P('U03','Exact expiration date and remaining term','jack-10k','Read the executed lease and amendments; 2030–2035 is only an unverified user-supplied range.','Controls the timing of the rollover cliff.')
P('U04','Tenant renewal options, notice windows and rent-setting method','boe','Verify who controls each option, deadlines, fair-market-rent procedure and any caps/floors.','The landlord may not be able to choose unilateral renewal.')
P('U05','Named tenant, legal obligor and guarantor credit','jack-q3','Review entity documents and private financials; do not substitute JACK corporate credit.','A franchisee, special-purpose entity or brand affiliate may be the actual obligor.')
P('U06','Current base rent, payment status and escalations','jack-q3','Reconcile lease schedule to private bank/rent-roll records.','No actual NOI, yield or sale threshold can be calculated.')
P('U07','Percentage rent, sales reporting and rent coverage','jack-q3','Review unit sales, rent-to-sales and EBITDAR coverage after a normalized manager/market wage.','Brand AUV does not establish this store’s ability to pay rent.')
P('U08','NNN expense allocations and structural/roof responsibilities','jack-10k','Read actual tax, insurance, utilities, repair, roof, structure, parking-lot and capital-replacement clauses.','NNN is a contract, not a guarantee of zero landlord expense.')
P('U09','Landlord reserves, unreimbursed expenses and deferred maintenance','jack-10k','Obtain private ledgers and an independent property-condition assessment.','Replacement obligations can consume cash even during a NNN term.')
P('U10','Current market value, net sale bids and selling costs','ula','Obtain independent private valuation/competitive bids; do not publish the address or offering materials.','No actual sell-versus-hold financial preference can be established.')
P('U11','Mortgage balance, rate, maturity, prepayment terms and covenants','fed','Review private loan documents and lender payoff statement.','Debt can dominate equity proceeds and create refinancing risk.')
P('U12','Tax basis, depreciation recapture, entity structure and exchange eligibility','irs','Keep owner tax records outside the public repository; obtain individualized tax advice.','After-tax proceeds, not headline price, determine preservation of wealth.')
P('U13','Zoning, overlays, legal nonconforming status and alternative-use rights','zoning','Privately verify the parcel and entitlements; confirm drive-thru and replacement-use permissions.','Redevelopment value is not assured by an attractive location.')
P('U14','Lot area, building area, age, frontage, parking, access and easements','jack-10k','Obtain survey, title report, plans and physical inspection; retain identifiers privately.','Physical access and land utility can matter more than county demographics.')
P('U15','Nearby traffic counts, turning movements and construction detours','caltrans','Use the relevant state/local road authority and site access study; no count is inferred.','State-highway passing volume is not the same as accessible customer traffic.')
P('U16','Assigned schools and actual neighborhood catchment','school','Verify attendance boundaries and private trade-area data without publishing the address.','LAUSD statistics are context, not a confirmed local school assignment.')
P('U17','Fire hazard designation and locally adopted map','osfm','Privately check the official viewer and local jurisdiction; distinguish recommendations from adoption.','No parcel wildfire classification can be assigned.')
P('U18','Effective flood zone, drainage and debris-flow exposure','fema','Obtain the effective FIRM panel plus local drainage/debris-flow review.','FEMA mapping alone does not capture every local flood pathway.')
P('U19','Seismic design, site soils, liquefaction and retrofit condition','usgs','Commission a site-specific structural/geotechnical review using official hazard datasets.','Regional earthquake probability is not a building-collapse probability.')
P('U20','Environmental condition and historical site uses','jack-10k','Obtain Phase I ESA and, if indicated, Phase II privately; issuer risk disclosure is not a site finding.','Contamination and prior dry-cleaning/fuel uses can impair value.')
P('U21','Insurance policies, exclusions, deductibles, rent loss and limits','insurance','Review binders and endorsements privately, including earthquake/flood and ordinance-or-law coverage.','A brand-name tenant does not eliminate uninsured owner loss.')
P('U22','Comparable rents, cap rates, downtime, tenant improvements and commissions','jack-10k','Use executed comparable transactions and independent brokerage/appraisal evidence; keep offering identifiers private.','No official regional source confirms the subject’s market rent or cap rate.')
P('U23','Owner liquidity needs, concentration, time horizon and risk tolerance','irs','Keep personal finances outside this repository; use a private fiduciary planning process.','A property-optimal decision may not be owner-optimal.')
P('U24','Tenant consent, assignment, recapture and franchise-transfer restrictions','jack-10k','Review lease and franchise-related consent requirements privately.','An extension or sale can require approvals that change timing and price.')
P('U25','Measure ULA applicability and closing-date rules','ula','Confirm municipal boundary, conveyance structure, exemptions and closing date.','Central Los Angeles is not sufficient to establish City tax liability.')
P('U26','Current applicable fast-food wage and local general wage','wage','Check current DIR/council and local schedules for the actual jurisdiction before tenant underwriting.','$20 is the initial covered floor, not a verified current payroll assumption.')
P('U27','Property-level sales, customer traffic and competing openings/closures','jack-10k','Review private operator reports and a field-verified competitive catchment.','No store-level demand or market-share value is inferred.')
P('U28','Title, liens, access/parking agreements and condemnation history','zoning','Obtain a current private title/preliminary report and public-record review without exposing identifiers.','Encumbrances can undermine redevelopment or financing.')

risks=[]
def R(id, title, kind, exposure, mechanism, action, source, decisions='Hold; sell; extend'):
    risks.append(dict(id=id, category='Risk register', metric=title, value=kind, period=decisions, geography='Property / regional mechanism', source_id=source, quote='', implication=mechanism+' Mitigation: '+action, status='Analysis · likelihood unquantified', note='Qualitative decision analysis, not an official probability or loss estimate.'))
R('R01','Short remaining lease / rollover cliff','Business as usual','Hold; sell near expiry; extend','Buyer financing and pricing can deteriorate as the certain income term shrinks. Renewal is not automatically landlord-controlled.','Map option/notice dates; seek an extension and market bids before the financing window narrows.','jack-10k')
R('R02','Tenant default or rent deferral','Business as usual','Hold; extend','SEC filings disclose franchise payment delays; the actual operator may be weaker than the brand.','Verify obligor/guarantor, rent coverage, arrears and security; size a private carrying-cost reserve.','jack-q3')
R('R03','Brand store rationalization','Business as usual','Hold; extend','Closures can occur even while the overall chain survives; a profitable brand portfolio need not preserve every site.','Obtain unit-level performance and reimage/commitment plans; assess alternative users before conceding rent.','jack-q3')
R('R04','Labor and commodity margin compression','Business as usual','Hold; extend','Wage floors and food/energy inflation can reduce a tenant’s ability to absorb rent increases.','Underwrite normalized labor and food costs; avoid rent resets that make the location uneconomic.','wage')
R('R05','Weak real demand / population decline','Business as usual','Hold; extend','County population decline can restrain transaction growth despite nominal menu-price increases.','Use flat/negative real-demand cases and verify actual catchment, not county averages alone.','census')
R('R06','Sector-specific employment weakness','Business as usual','Hold; extend','Information and film weakness can reduce nearby daytime demand even as healthcare grows.','Diversify demand sources in site underwriting; do not capitalize one strong sector into the entire trade area.','edd')
R('R07','Interest-rate and capitalization-rate shock','Business as usual / market','Sell; refinance; hold','Higher required yields can lower buyer bids independently of tenant performance.','Stress exit pricing and discount rates; verify debt maturity and avoid forced-sale timing.','fed')
R('R08','Inflation versus fixed lease bumps','Business as usual','Hold; extend','Rent escalations below inflation erode real income; replacement costs can rise faster than NNN reimbursements.','Compare real and nominal cash flows; negotiate appropriate bumps without impairing coverage.','cpi-local')
R('R09','NNN reimbursement gaps / capital obligations','Contract / operational','Hold; extend','Roof, structure, parking, insurance gaps and unreimbursed administration can remain with the owner.','Read the lease rather than the marketing label; commission a condition assessment and reserve study.','jack-10k')
R('R10','Re-leasing downtime and concessions','Business as usual','Hold; sell after vacancy; redevelop','Vacancy can require carrying costs, tenant improvements, commissions and free rent before income resumes.','Model zero-rent periods explicitly and obtain alternative-user bids before expiry.','jack-10k')
R('R11','Below-market extension / opportunity cost','Contract / market','Extend','A long fixed-rent extension can protect occupancy while surrendering upside or accepting weak credit.','Compare extension value with current bids and market-rent reset alternatives; reject value-destructive terms.','boe')
R('R12','Long-lease reassessment','Regulatory','Extend; restructure','A lease of 35 years or more including written options can constitute a change in ownership.','Obtain property-tax counsel before executing an extension or restructuring options.','boe')
R('R13','Transfer-tax cliff and jurisdiction error','Regulatory / transaction','Sell; exchange','City ULA can materially reduce net proceeds above thresholds; it does not apply merely because a listing says Los Angeles.','Confirm jurisdiction and closing-date rules; compare after-tax net proceeds, not asking price.','ula')
R('R14','Tax leakage and failed exchange timing','Tax / transaction','Sell; exchange; installment sale','Recapture, boot, state tax and missed exchange deadlines can reduce investable proceeds.','Use private tax basis and a qualified intermediary before closing; evaluate a taxable diversified sale versus replacement-property risk.','irs')
R('R15','Buyer retrading, financing failure and execution risk','Transaction','Sell; extend then sell','Headline offers may not close; diligence can reveal defects and lenders can reprice.','Require evidence of funds/financing, deposits and clear contingencies; maintain a fallback hold plan.','fed')
R('R16','Wildfire, smoke and evacuation','Severe hazard / tail','Hold; extend; sell during disruption','Damage, access loss, customer displacement and smoke can interrupt rent even without building destruction.','Check adopted hazard maps, hardening, insurance and rent-abatement clauses; stress prolonged outage.','fire-p')
R('R17','Earthquake and lifeline interruption','Severe hazard / tail','Hold; extend; redevelop','Regional shaking can damage structures and roads/utilities; repair demand can raise costs.','Obtain seismic/soil review, earthquake and rent-loss coverage quotes, and an engineered repair reserve.','usgs')
R('R18','Flood, debris flow and drainage failure','Severe hazard / tail','Hold; redevelop; sell','Effective flood mapping and post-fire debris pathways are site-specific; county location cannot resolve them.','Review FIRM, local hydrology, elevation and exclusions; do not assume absence of a mapped zone means no risk.','fema')
R('R19','Insurance nonrenewal, exclusions or slow recovery','Financial / hazard','Hold; extend','Insurance proceeds may arrive late or exclude key perils; lender coverage requirements can force expensive replacement.','Review full policies, limits and business-interruption periods; maintain liquidity rather than relying on disaster aid.','insurance')
R('R20','Construction and access disruption','Infrastructure / operational','Hold; sell; redevelop','Lane reductions and pedestrian detours can hurt a drive-thru or walk-up location before transit benefits arrive.','Check agency notices and driveway rights; do not pay for speculative transit uplift today.','metro')
R('R21','Zoning, entitlement and alternative-use risk','Regulatory / physical','Redevelop; change tenant; sell land','A restaurant site may not permit the desired replacement use, density, parking or drive-thru.','Verify zoning, overlays, legal nonconforming rights and entitlement cost before assigning residual land value.','zoning')
R('R22','Environmental liability and remediation','Environmental / tail','Hold; sell; redevelop','Owner/operator liability can arise from current or historical contamination and delay transfer or financing.','Obtain private Phase I/II work and legal allocation of obligations; no environmental clearance is asserted here.','jack-10k')
R('R23','Title, easement, parking or access defect','Legal / physical','Sell; redevelop; refinance','Encumbrances can invalidate assumed access, parking counts or redevelopment capacity.','Review current title, survey, shared-parking agreements and condemnation records privately.','zoning')
R('R24','Pandemic, civil unrest or utility/cyber outage','Rare compound shock','All decisions','Public-health restrictions, unrest or infrastructure failures can combine access loss with tenant cash-flow stress.','Stress 12–24 months of interrupted rent plus carrying costs; review force majeure, abatement and security provisions.','jack-10k')
R('R25','Trade, energy or geopolitical shock','Rare macro shock','Hold; extend; sell','Fuel and supply-chain shocks can affect ports, food costs and household spending at the same time.','Use combined inflation-plus-low-demand scenarios; avoid treating sector indicators as independent guarantees.','ucla')
R('R26','Drought, extreme heat and water restrictions','Climate / operational','Hold; redevelop','Heat raises operating costs and can alter customer behavior; water constraints can affect landscaping and redevelopment.','Review local utility rules, equipment efficiency and climate resilience; no numeric loss is inferred.','osfm')
R('R27','Concentration and personal liquidity mismatch','Owner-level','Hold; extend','One building, one tenant and one region can dominate personal wealth even when property cash flow is stable.','Assess private net-worth concentration and cash needs; diversification may justify selling below a theoretical hold value.','irs')
R('R28','Replacement-asset and diversification execution risk','Owner-level','Sell; exchange; refinance','Sale proceeds can be reinvested into an equally risky asset, held idle, or exposed to exchange deadlines.','Compare after-tax diversified alternatives and fiduciary advice; an exchange is tax deferral, not automatic wealth creation.','irs')
R('R29','Overreliance on temporary global events','Market / forecast','Hold; extend; sell','Tourism and Olympics exposure can be temporary and unevenly distributed; construction costs occur before benefits.','Underwrite recurring local demand first; assign no permanent event premium without site evidence.','tourism')
R('R30','Data-vintage, geography and model error','Information / model','All decisions','County statistics, old comparables and mismatched definitions can create false precision.','Keep blank unknowns, retain source vintages, test assumptions and independently appraise the actual property.','forecast-method')

decisions=[]
def D(id, title, posture, benefit, risk, gate, source):
    decisions.append(dict(id=id, category='Decision alternatives', metric=title, value=posture, period='Owner strategy', geography='[PROPERTY]', source_id=source, quote='', implication=benefit+' Tradeoff: '+risk+' Decision gate: '+gate, status='Analysis · not a valuation', note='No decision is asserted to maximize personal wealth without private after-tax and liquidity analysis.'))
D('D01','Hold under the existing lease','Conditional fallback','Preserves current income and avoids an immediate taxable sale.','Retains tenant, rollover, hazard and concentration risk; a wasting lease term can reduce marketability.','Use when verified net bids do not compensate for conservatively valued remaining cash flows and reserves are adequate.','jack-q3')
D('D02','Competitive sale before the lease gets shorter','Preferred price-discovery track','Can transfer tenant/rollover/hazard risk while remaining term is still financeable.','May sacrifice upside and trigger taxes, transfer charges and prepayment costs.','Compare executable net proceeds with conservative hold value and the owner’s diversification/liquidity needs.','ula')
D('D03','Wait until immediately before expiry','Generally avoid as a default','May collect more rent if the tenant performs.','Concentrates negotiation, vacancy and financing risk into a narrow window.','Only justify with strong unit coverage, credible renewal intent, ample liquidity and a funded re-leasing plan.','jack-10k')
D('D04','Negotiate an extension now','Parallel value-enhancement track','Can lengthen marketable income without changing ownership.','Weak rent, concessions, options or guarantors can destroy value; long terms can trigger reassessment.','Execute only if the risk-adjusted extension premium exceeds concessions and retained risk.','boe')
D('D05','Extend, then sell','Conditional alternative','A stronger lease may broaden the buyer/lender pool.','Extension negotiations consume time and may not improve net price enough to cover costs.','Use a value-before/value-after analysis and confirm transfer/consent requirements.','boe')
D('D06','Wait for tenant renewal, then sell','Conditional alternative','Avoids landlord concessions if the tenant exercises a valuable option.','The tenant may decline, demand a reduction or control timing.','Track notice deadlines and maintain a sale/hold fallback rather than assuming exercise.','jack-10k')
D('D07','Short extension with market resets','Worth evaluating','Balances a longer income term with inflation protection and flexibility.','Reset disputes, caps and tenant affordability can limit protection.','Model fair-market-rent procedures, notice timing and realistic coverage.','cpi-local')
D('D08','Blend-and-extend / rent concession','Only with coverage evidence','May preserve a viable operator and avoid downtime.','A permanent rent cut can outweigh the value of added term.','Require unit financials and compare the net present value against replacement tenant and sale paths.','jack-q3')
D('D09','Tenant replacement after vacancy','Fallback, not base-case certainty','Could improve rent, credit or use if the location supports another operator.','Downtime, improvements, commissions and entitlement risk can be substantial.','Obtain credible replacement-user demand and a funded lease-up budget before relying on this path.','zoning')
D('D10','Redevelop or change use','Separate feasibility project','May unlock higher-value land use where legally and physically feasible.','Construction, entitlement, environmental, leasehold and market risk can overwhelm residual land value.','Require title/zoning/environmental clearance, costed plans and preleasing/exit evidence.','zoning')
D('D11','Sell through a like-kind exchange','Tax tool, not a standalone answer','May defer eligible federal gain and preserve investable capital.','Strict timing, boot, state rules and replacement-asset concentration can reduce benefits.','Use only after private tax analysis and replacement-asset underwriting; arrange intermediary before closing.','irs')
D('D12','Taxable sale and diversification','Wealth-preservation alternative','Can reduce single-asset exposure and improve liquidity.','Tax drag and reinvestment risk are real; diversification is not a return guarantee.','Compare after-tax risk-adjusted outcomes against continued concentration; obtain fiduciary advice.','irs')
D('D13','Refinance or cash-out refinance','Liquidity tool, not an exit','May fund reserves without an immediate sale.','Adds leverage, debt service, maturity and prepayment risk.','Stress vacancy cash flow and lender covenants; do not use debt to disguise weak property economics.','fed')
D('D14','Installment sale / seller financing','Special-case alternative','May broaden buyers or spread eligible tax recognition.','Creates buyer credit exposure and delays full liquidity; tax treatment is fact-specific.','Require collateral, underwriting and tax/legal review; not assumed available or beneficial.','irs')
D('D15','Partial-interest sale or joint venture','Special-case alternative','Can release some capital while retaining upside.','Governance, control, transfer restrictions and reassessment can be complex.','Value the retained interest and minority discount; obtain legal/tax advice before marketing.','boe')
D('D16','Donate / estate-transfer strategy','Private planning alternative','May align with philanthropic or intergenerational goals.','Irreversibility, liquidity and complex valuation/tax rules make this unsuitable as a default.','Only evaluate privately with qualified fiduciary and tax professionals; no personal facts are assumed.','irs')

flags=[]
def Q(id, title, detail, source, severity='Needs review'):
    flags.append(dict(id=id, category='Flagged for review', metric=title, value=severity, period='Checked '+CHECKED, geography='Public research / [PROPERTY]', source_id=source, quote='', implication=detail, status='Flagged · nonblocking', note='No personal or identifying property information is included.'))
for p in property:
    Q('F-'+p['id'],p['metric']+' — unverified',p['note']+' '+p['implication'],p['source_id'],p['priority'])
Q('F01','Fire-count vintage discrepancy','CAL FIRE shows Palisades 6,845 destroyed / 975 damaged and Eaton 9,419 / 1,076; the County anniversary sheet shows 6,837 / 973 and 9,414 / 1,074. Use each attributed snapshot separately; do not average or silently overwrite.','fire-p')
Q('F02','Official forecast payroll-level discontinuity','The extracted 2026 DOF PDF payroll series shows 4,200,000 in 2024, 4,600,000 in 2025 and only 0.2% growth. This does not reconcile cleanly with the displayed levels or the EDD series. Job levels are excluded from the model; published growth rates remain labeled official forecasts pending raw-workbook review.','dof')
Q('F03','Population vintage differences','Census V2025 reports 9,694,934 in 2025; the DOF forecast PDF uses a different population basis and displays 9.86 million for 2025. Do not splice these into a single growth series.','census')
Q('F04','Permit series definitions differ','Census QuickFacts reports 22,250 permits in 2025; the EDD live profile displays 20,192 total all-types construction permits. Categories/source tables are not reconciled; no combined trend is calculated.','census')
Q('F05','Earthquake forecast start date','The 60% and 31% figures are UCERF3 regional 30-year probabilities starting in 2014. They are not a new 2026 forecast and must not be converted into a building-loss probability.','usgs')
Q('F06','September labor estimates are preliminary and revised','The official EDD release distinguishes adjusted and unadjusted rates and revises August. Future releases can change the numbers; preserve observation and adjustment labels.','edd')
Q('F07','Missing October 2025 regional CPI','BLS states October 2025 data are unavailable because of the appropriations lapse. Do not fill the month by interpolation. October 2026 CPI is scheduled after this research cutoff.','cpi-local')
Q('F08','Live-source rollover risk','Census, EDD, Freddie Mac, BLS, SEC indexes and agency project pages can change after the checked date. Source excerpts and observation periods are frozen in this release; links are for manual review, not a promise of identical future content.','sec-list')
Q('F09','Original-issuer estimates are not government statistics','FilmLA, Los Angeles Tourism and UCLA are original issuing organizations, not federal statistical agencies. Tourism sales are commissioned impact estimates; forecasts and shoot-day measures retain their own definitions.','tourism')
Q('F10','Brand credit is not tenant credit','JACK SEC filings describe the public company and its franchise system. They do not identify the subject operator, prove a corporate guaranty, or disclose this store’s rent coverage.','jack-q3')
Q('F11','No calibrated event probabilities or cap rates','Official sources checked do not establish a parcel-specific default probability, market cap rate, rent, downtime or re-leasing cost. Scenario values are explicit hypotheses, not verified market data.','jack-10k')
Q('F12','Wage FAQ is an initial-floor source','DIR explains the $20 floor effective April 2024 and annual adjustment authority. It is not a full current local/council wage schedule; actual underwriting must confirm the applicable rate.','wage')
Q('F13','UCLA forecast vintage predates latest policy decision','The June 2026 state outlook is not updated here to the October FOMC decision. Its rate commentary is historical context; only labeled economic forecast rows are retained.','ucla')
Q('F14','Repository history and coordination','The initial repository contained only a two-line README and no evidence files. The coordination claim was committed and pushed before research. Arena fixes the working branch, so the requested alternate session-branch naming was not used.','repo','Review note')
Q('F15','No individualized investment or tax conclusion','Owner finances, basis, liquidity needs and risk tolerance are absent. The recommendation is a reversible decision process, not a claim that a particular sale price or allocation is personally optimal.','irs')
Q('F16','Scenario controls are hypotheses, not verified property inputs','The model uses dimensionless test points to demonstrate mechanics. Rent growth, discount rates, cap rates, downtime, costs and residual multiples are not market observations. Actual property fields remain blank; replace test controls only with independently verified evidence in a private analysis.','repo')

requirements = [
 ('Q01','Privacy first; anonymize owner and property','Implemented','Public outputs use placeholders; no owner/property identifiers were supplied or collected. Static site has no forms, analytics, cookies or external runtime scripts.','boe'),
 ('Q02','Executive summary and clear decision','Implemented','Landing page leads with a conditional dual-track recommendation and separates facts from missing inputs.','jack-q3'),
 ('Q03','Sell versus renew/extend before 2030–2035 expiry','Implemented with limitation','Both endpoints are stress-tested; actual expiration and renewal rights remain blank and flagged.','boe'),
 ('Q04','Geography, income, schools, population and jobs','Implemented','County/MSA/district proxies are labeled; no neighborhood values are invented.','census'),
 ('Q05','Business-as-usual and rare severe events','Implemented','Decision-risk register covers ordinary cycles and compound tail shocks without invented probabilities.','usgs'),
 ('Q06','Reliable projection system','Implemented as conditional framework','Official county/state forecasts plus transparent normalized cash-flow sensitivities; no unsupported property valuation.','dof'),
 ('Q07','Official-source links on every table row','Implemented','Renderer requires a registered source and emits a visible official-source link in every data-table row.','repo'),
 ('Q08','Blank unknowns; flag unverified values','Implemented','All property-specific unknown values are empty strings with source-supported review topics and nonblocking flags.','repo'),
 ('Q09','Review repository line by line','Implemented','Initial README line 1 and blank line 2 reviewed; generated code, data and pages receive schema, source-excerpt, privacy and link checks.','repo'),
 ('Q10','Clean landing page and category subpages','Implemented','Static accessible dashboard with overview, evidence, property, projections, decisions, risks, tax, requirements, sources and review pages.','repo'),
 ('Q11','No manual input required','Implemented','Research, build, validation, PR and deployment are automated in-session. Missing facts are not requested through a form.','repo'),
 ('Q12','Shared coordination board','Implemented','Claims, branch constraint, verification log, sources and final integration outcome recorded in COORDINATION.md.','repo'),
 ('Q13','Build and link validation before merge','Pending integration','Static build, internal link/anchor checks, model tests, source checks and privacy scans run before the PR is merged.','repo'),
 ('Q14','PR, merge and live GitHub Pages','Pending integration','Create and merge the integration PR, then verify the deployed site and record actual links/results.','repo'),
 ('Q15','Flagged items visible after publication','Implemented','Dedicated Flagged for Review page includes every missing property input and source/data irregularity with official links.','repo'),
]
requirement_rows=[dict(id=id,category='Requirements',metric=title,value=status,period='This release',geography='Project',source_id=src,quote='',implication=detail,status='Project record',note='Project implementation record; official link provides topical support where applicable.') for id,title,status,detail,src in requirements]
S('repo','Project repository · official source record','https://github.com/wingbangboozle1-lang/Jack2','Initial repository inspection: README.md line 1 was # Jack2; line 2 was blank. No other files existed.',kind='Project source-control record',note='Used only for project implementation facts, never as external economic evidence.')
out=dict(as_of=CHECKED,scope='Anonymous NNN restaurant property described by the owner as around central Los Angeles; exact location and lease unverified.',sources=list(sources.values()),findings=findings,property=property,projections=[f for f in findings if f['id'].startswith('P')],risks=risks,decisions=decisions,flags=flags,requirements=requirement_rows)
Path('data').mkdir(exist_ok=True)
Path('data/research.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print(f'Wrote {len(findings)} evidence/forecast rows, {len(property)} blank property fields, {len(risks)} risks, {len(decisions)} decisions, {len(flags)} flags, {len(sources)} sources.')
