#!/usr/bin/env python3
"""Build the anonymized, source-linked evidence ledger. No network access at build time."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
AS_OF = "2026-11-08"
SOURCES = []
METRICS = []
REQUIREMENTS = []
RISKS = []
DECISIONS = []
FLAGS = []

def src(i, publisher, title, url, kind="government", status="read", locator="", note=""):
    SOURCES.append(dict(id=i, publisher=publisher, title=title, url=url, kind=kind,
                        status=status, locator=locator, accessed=AS_OF, note=note))

def m(i, cat, metric, value, unit, period, geo, source, note="", locator="", status="verified", kind="observation", extra=None):
    METRICS.append(dict(id=i, category=cat, metric=metric, value=value, unit=unit,
                        period=period, geography=geo, source=source, locator=locator,
                        status=status, kind=kind, note=note, extra_sources=extra or []))

def unknown(i, cat, metric, unit, geo, source, note, locator="", extra=None):
    m(i, cat, metric, "", unit, "", geo, source, note, locator, "unverified", "unknown", extra)

def req(i, cat, name, source, why, action, locator=""):
    REQUIREMENTS.append(dict(id=i, category=cat, requirement=name, value="", source=source,
                             locator=locator, status="unverified", why=why, action=action))

def risk(i, typ, name, mechanism, mitigation, source, extra=None):
    RISKS.append(dict(id=i, type=typ, name=name, mechanism=mechanism, mitigation=mitigation,
                      source=source, extra_sources=extra or [], status="analysis",
                      probability="", severity="Not quantified", note="Analyst risk pathway; no parcel-specific probability or loss estimate."))

def decision(i, name, when, benefits, costs, verdict, source, extra=None):
    DECISIONS.append(dict(id=i, strategy=name, when=when, benefits=benefits, costs=costs,
                          verdict=verdict, source=source, extra_sources=extra or [], status="analysis"))

def flag(i, severity, area, finding, evidence, action, source, status="open", extra=None):
    FLAGS.append(dict(id=i, severity=severity, area=area, finding=finding, evidence=evidence,
                      action=action, source=source, extra_sources=extra or [], status=status))

# Official primary sources. Short locators/paraphrases only; no source-page contact details are copied.
src("S01", "U.S. Census Bureau", "QuickFacts: Los Angeles city and county", "https://www.census.gov/quickfacts/fact/table/losangelescitycalifornia,losangelescountycalifornia/PST045225", locator="V2025 population; 2020-2024 ACS 5-year tables", note="City and county columns are distinct; ACS and population estimates have different vintages.")
src("S02", "U.S. Bureau of Labor Statistics", "Los Angeles area economic summary, November 2026", "https://www.bls.gov/regions/west/summary/BLSSummary_LosAngeles.pdf", locator="Updated 2026-11-04; September 2026 employment/CPI tables", note="Metropolitan division, county and city measures are labeled separately.")
src("S03", "California Employment Development Department", "Los Angeles County monthly labor force and industry employment", "https://labormarketinfo.edd.ca.gov/file/lfmonth/la$pds.pdf", locator="September 2026 preliminary release", note="Seasonally adjusted and unadjusted series are not interchangeable.")
src("S04", "U.S. Bureau of Economic Analysis", "County GDP and personal income, 2024", "https://www.bea.gov/news/2026/gross-domestic-product-county-and-personal-income-county-2024", locator="Released 2026-02-05; Los Angeles County personal income", note="County GDP was not independently extracted; no county GDP value is asserted.")
src("S05", "California Department of Finance", "P-2A county population projections, Vintage 2026 / Baseline 2024", "https://dof.ca.gov/media/docs/forecasting/Demographics/projections/P2A_County_Total.xlsx", locator="FIPS 6037 row; 2025, 2030, 2035, 2040, 2050 columns", note="Official demographic projection, not an observation or a rent forecast.")
src("S06", "California Department of Finance", "Projections release page", "https://dof.ca.gov/forecasting/demographics/projections/", locator="Vintage 2026 release notes; P-4 household projection link", note="Vintage 2026 released 2026-03-13; baseline assumptions unchanged from 2024.")
src("S07", "Southern California Association of Governments", "Connect SoCal 2024 demographics and growth forecast technical report", "https://scag.ca.gov/sites/default/files/2024-05/23-2987-tr-demographics-growth-forecast-final-040424.pdf", locator="Adopted 2024-04-04; sections 4.1-4.3", note="Policy-driven regional planning forecast; not directly comparable to DOF demographic projections.")
src("S08", "Southern California Association of Governments", "Connect SoCal 2024 final PEIR Appendix I, updated tables", "https://scag.ca.gov/sites/default/files/2024-05/appendix_i_updated_tables_508_final.pdf", locator="Tables ES-1/2-1 and 3.14-8/9/10, Los Angeles County rows", note="Rounded to nearest thousand; reproduces Table 12 county forecasts.")
src("S09", "California Department of Education", "Los Angeles Unified district profile", "https://www.cde.ca.gov/sdprofile/details.aspx?cds=19647330000000", locator="2025-26 enrollment and English learner counts", note="District-wide proxy; the subject school attendance area is unknown.")
src("S10", "California Department of Education", "DataQuest four-year adjusted cohort graduation rate, LAUSD", "https://dq.cde.ca.gov/dataquest/dqcensus/CohRate.aspx?agglevel=district&year=2024-25&cds=1964733", locator="2024-25 Report Totals; default Non-Charter filter", note="86.2% is the default non-charter report total, not the Dashboard combined four/five-year measure.")
src("S11", "California Department of Education", "California School Dashboard: LAUSD academic engagement", "https://www.caschooldashboard.org/reports/19647330000000/2025/academic-engagement", locator="2025 graduation and chronic absenteeism indicators", note="Combined four/five-year graduation measure differs from DataQuest four-year ACGR.")
src("S12", "California Department of Education", "California School Dashboard: LAUSD academic performance", "https://www.caschooldashboard.org/reports/19647330000000/2025/academic-performance", locator="2025 all-student ELA and mathematics distance from standard", note="Distance from standard is not a proficiency percentage.")
src("S13", "California Department of Industrial Relations", "California minimum wage FAQ", "https://www.dir.ca.gov/dlse/faq_minimumwage.htm", locator="Statewide minimum wage effective January 1, 2026")
src("S14", "California Department of Industrial Relations", "Fast food minimum wage FAQ", "https://www.dir.ca.gov/dlse/Fast-Food-Minimum-Wage-FAQ.htm", locator="Covered fast food employees; AB 1228 coverage rules")
src("S15", "City of Los Angeles", "Minimum wage ordinance", "https://wagesla.lacity.org/", locator="Rates effective July 1, 2026", note="General city ordinance and fast-food coverage must be analyzed separately.")
src("S16", "U.S. Securities and Exchange Commission", "Jack in the Box Inc. Form 10-Q, quarter ended July 5, 2026", "https://www.sec.gov/Archives/edgar/data/807882/000080788226000091/jack-20260705.htm", locator="Filed 2026-08-12; MD&A and liquidity sections", kind="issuer filing", note="Corporate franchisor data; not the subject operator's financial statements.")
src("S17", "U.S. Securities and Exchange Commission", "JACK Q3 FY2026 XBRL balance sheet", "https://www.sec.gov/Archives/edgar/data/807882/000080788226000091/R2.htm", locator="July 5, 2026 column", kind="issuer filing")
src("S18", "U.S. Securities and Exchange Commission", "JACK Q3 FY2026 XBRL statements of earnings", "https://www.sec.gov/Archives/edgar/data/807882/000080788226000091/R4.htm", locator="12-week and 40-week periods ended July 5, 2026", kind="issuer filing")
src("S19", "U.S. Securities and Exchange Commission", "JACK Q3 FY2026 restaurant counts", "https://www.sec.gov/Archives/edgar/data/807882/000080788226000091/R36.htm", locator="Restaurant count note, July 5, 2026", kind="issuer filing")
src("S20", "U.S. Securities and Exchange Commission", "Jack in the Box Inc. FY2025 Form 10-K", "https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm", locator="Business, risk factors and lease notes", kind="issuer filing", note="AUV and lease-renewal quotation were located in official filing text via search; filing identity and surrounding sections were retrieved.")
src("S21", "U.S. Securities and Exchange Commission", "NNN REIT FY2025 Form 10-K", "https://www.sec.gov/Archives/edgar/data/751364/000119312526045617/nnn-20251231.htm", locator="Item 7, Property Analysis, printed pages 28-30", kind="issuer filing", note="Diversified net-lease portfolio benchmark, not a Los Angeles QSR appraisal.")
src("S22", "U.S. Department of the Treasury", "Daily Treasury yield curve rates, November 2026", "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value_month=202611", locator="November 6, 2026 row", note="Indicative constant-maturity yields, not executable retail reinvestment offers.")
src("S23", "Federal Reserve Board", "FOMC statement, October 28, 2026", "https://www.federalreserve.gov/newsevents/pressreleases/monetary20261028a.htm", locator="Target range decision")
src("S24", "Los Angeles Office of Finance", "Real property transfer tax and Measure ULA FAQ", "https://finance.lacity.gov/faq/measure-ula", locator="Thresholds for transactions closing after June 30, 2026", note="Applies only to conveyances within City of Los Angeles boundaries; exemptions and allocation rules matter.")
src("S25", "Los Angeles County Assessor", "Real property assessments and Proposition 13", "https://assessor.lacounty.gov/homeowners/realproperty", locator="General levy and assessed-value growth explanation")
src("S26", "Internal Revenue Service", "Instructions for Form 8824 (2025)", "https://www.irs.gov/instructions/i8824", locator="Deferred Exchanges; Definition of Real Property")
src("S27", "Internal Revenue Service", "Topic 409: Capital gains and losses", "https://www.irs.gov/taxtopics/tc409", locator="2025 taxable-year rates and unrecaptured section 1250 gain")
src("S28", "Internal Revenue Service", "Topic 559: Net investment income tax", "https://www.irs.gov/taxtopics/tc559", locator="Individual thresholds and definition of net investment income")
src("S29", "California Franchise Tax Board", "2025 Instructions for Form FTB 3840", "https://www.ftb.ca.gov/forms/2025/2025-3840-instructions.html", locator="Who Must File; California-source deferred gain")
src("S30", "U.S. Geological Survey", "Earthquake probability FAQ: Los Angeles and San Francisco Bay areas", "https://www.usgs.gov/faqs/what-probability-earthquake-will-occur-los-angeles-area-san-francisco-bay-area", locator="UCERF3 regional 30-year probabilities", note="Regional event probabilities, not parcel damage probabilities or a fresh 2026-2056 forecast.")
src("S31", "U.S. Geological Survey", "Overview of the ARkStorm scenario (2011)", "https://www.usgs.gov/publications/overview-arkstorm-scenario", locator="Scenario losses and lifeline disruption", note="Historical hypothetical statewide scenario in then-current dollars; not an annual expected loss.")
src("S32", "County of Los Angeles", "Eaton and Palisades fires anniversary fact sheet", "https://file.lacounty.gov/SDSInter/lac/1199046_Eaton_Palisades_Fires_Anniversary_Fact_Sheet.pdf", locator="January 2025 incident totals and estimated economic impacts")
src("S33", "California Department of Insurance", "Bulletin 2025-4: FAIR Plan assessment recoupment", "https://www.insurance.ca.gov/0250-insurers/0300-insurers/0200-bulletins/bulletin-notices-commiss-opinion/upload/Bulletin-2025-4-Updated-Guidance-regarding-Insurer-Recoupment-Procedures-in-Response-to-Assessment-by-the-FAIR-Plan.pdf", locator="Issued 2025-02-11; assessment and recoupment rules", note="Approval-dependent insurer surcharges; not a quote for this property.")
src("S34", "Federal Emergency Management Agency", "National Risk Index for Natural Hazards", "https://www.fema.gov/flood-maps/products-tools/national-risk-index", locator="December 2025 v1.20; county and Census-tract baseline", note="Legacy NRI viewer retired; data now in RAPT. County score not independently extracted.")
src("S35", "Federal Emergency Management Agency", "National Risk Index data downloads", "https://www.fema.gov/about/openfema/data-sets/national-risk-index-data", status="partial", locator="v1.20 county table download", note="Documentation retrieved; county ZIP download failed in this environment. No county score is asserted.")
src("S36", "Los Angeles County Metropolitan Transportation Authority", "D Line subway extension", "https://www.metro.net/projects/westside/", locator="Section 1 opened May 8, 2026; Sections 2-3 under construction")
src("S37", "Port of Los Angeles", "September 2026 cargo record", "https://portoflosangeles.org/references/2026-news-releases/news_100926_sept_cargo", locator="Released 2026-10-09")
src("S38", "Los Angeles Tourism & Convention Board", "2025 economic impact of visitors, released July 29, 2026", "https://www.discoverlosangeles.com/visitors-to-los-angeles-generated-426-billion-in-business-sales-and-supported-more-than-530000-jobs", kind="official destination organization", locator="2025 visitor counts and modeled business sales", note="Official tourism organization; economic impact estimates prepared with Tourism Economics, not a government census.")
src("S39", "U.S. Department of Housing and Urban Development", "Annual Homelessness Assessment Reports (AHAR)", "https://www.huduser.gov/portal/datasets/ahar.html", locator="PIT/HIC methodology and report index", note="Official federal fallback after LAHSA 2026 release endpoint returned a runtime error. No 2026 local count is asserted.")
src("S40", "Federal Emergency Management Agency", "Flood Map Service Center", "https://msc.fema.gov/portal/home", locator="Official NFIP flood hazard maps", note="Parcel lookup not possible without location.")
src("S41", "California Geological Survey", "Alquist-Priolo earthquake fault zones", "https://www.conservation.ca.gov/cgs/alquist-priolo", locator="Surface rupture, disclosure and investigation requirements")
src("S42", "State Water Resources Control Board", "GeoTracker", "https://geotracker.waterboards.ca.gov/", locator="Cleanup sites and permitted underground storage tanks")
src("S43", "Los Angeles City Planning", "Zone Information and Map Access System (ZIMAS)", "https://zimas.lacity.org/", locator="Parcel zoning and planning information", note="Interactive map shell retrieved; no parcel queried.")
src("S44", "Internal Revenue Service", "Like-kind exchanges: real estate tax tips", "https://www.irs.gov/businesses/small-businesses-self-employed/like-kind-exchanges-real-estate-tax-tips", locator="Real-property limitation and boot recognition")
src("S45", "Los Angeles City Council", "Revised FY 2026-27 budget release", "https://councildistrict5.lacity.gov/release-los-angeles-city-council-passes-revised-fy-2026-27-budget", locator="May 22, 2026; reserve fund and service priorities")
src("S46", "Los Angeles Police Department / City Open Data", "Crime data from 2020 to 2024", "https://data.lacity.org/Public-Safety/Crime-Data-from-2020-to-2024/2nrs-mtv8/about_data", locator="Dataset notice: legacy UCR series no longer updated; NIBRS replacement", note="Historical dataset only; current neighborhood crime rate not computed.")
src("S47", "California Department of Finance", "P-4 county household projections, Vintage 2025 / Baseline 2024", "https://dof.ca.gov/media/docs/forecasting/Demographics/projections/P4_HHProjections_B2024.xlsx", locator="FIPS 6037 row; January 1 household counts", note="Los Angeles County 2026-2030 values revised 2025-11-17. Different concept from Census ACS households.")
src("S48", "U.S. Geological Survey", "UCERF3 long-term time-dependent probabilities (2015)", "https://www.usgs.gov/publications/long-term-time-dependent-probabilities-third-uniform-california-earthquake-rupture", locator="2014 Working Group; model limitations", note="Use with S30; magnitude probabilities are not a loss proxy.")
src("S49", "U.S. Securities and Exchange Commission", "JACK December 2025 preliminary proxy statement", "https://www.sec.gov/Archives/edgar/data/807882/000080788225000076/jack-20251216.htm", kind="issuer filing", locator="Cover retrieved; FY2025 unit openings/closures located in official filing text via search", note="Document is PREC14A, not an 8-K. Excerpt is historical unit activity, not current guidance.")
src("S50", "California Geological Survey", "Seismic Hazards Mapping Act program", "https://www.conservation.ca.gov/cgs/shma", locator="Liquefaction and landslide zoning program")
src("S51", "California State Fire Marshal / CAL FIRE", "Fire Hazard Severity Zones", "https://osfm.fire.ca.gov/what-we-do/community-wildfire-preparedness-and-mitigation/fire-hazard-severity-zones", locator="Hazard vs risk explanation; SRA/LRA map links; 2026 SRA comment notice", note="Replacement for legacy egis.fire.ca.gov/FHSZ, which returned 404. Parcel zone not queried.")

# Demographics and income. Values are transcribed from the cited tables, not inferred.
for i, metric, city, county, unit, period in [
 ("D01","Population estimate",3869089,9694934,"people","Vintage 2025; July 1, 2024 base"),
 ("D02","Households",1439097,3416449,"households","2020-2024 ACS 5-year"),
 ("D03","Median household income",81939,90112,"2024 dollars","2020-2024 ACS 5-year"),
 ("D04","Per capita income",47685,45792,"2024 dollars","2020-2024 ACS 5-year"),
 ("D05","Poverty rate",16.5,13.3,"percent","2020-2024 ACS 5-year"),
 ("D06","Owner-occupied housing unit rate",36.0,45.9,"percent","2020-2024 ACS 5-year"),
 ("D07","Median value of owner-occupied housing units",921200,834200,"2024 dollars","2020-2024 ACS 5-year"),
 ("D08","Median gross rent",1933,1954,"2024 dollars/month","2020-2024 ACS 5-year"),
 ("D09","High school graduate or higher, age 25+",79.6,80.9,"percent","2020-2024 ACS 5-year"),
 ("D10","Bachelor's degree or higher, age 25+",38.5,36.0,"percent","2020-2024 ACS 5-year"),
 ("D11","Mean travel time to work",30.7,30.4,"minutes","2020-2024 ACS 5-year"),
]:
    m(i+"C","Demographics" if i in ("D01","D02") else "Income & housing",metric+" - city",city,unit,period,"City of Los Angeles","S01","QuickFacts city column; area proxy, not a trade-area estimate.")
    m(i+"K","Demographics" if i in ("D01","D02") else "Income & housing",metric+" - county",county,unit,period,"Los Angeles County","S01","QuickFacts county column; area proxy, not a trade-area estimate.")
m("D12","Income & housing","Accommodation and food services sales - city",17366966,"USD thousands","2022 Economic Census","City of Los Angeles","S01","Sector sales are not restaurant rent or landlord NOI.")
m("D13","Income & housing","Accommodation and food services sales - county",44000801,"USD thousands","2022 Economic Census","Los Angeles County","S01","Sector sales are not restaurant rent or landlord NOI.")
for year, val in [(2025,9853435),(2030,9727305),(2035,9708647),(2040,9637524),(2050,9390823)]:
    m(f"DP{year}","Area projections","DOF county population projection",val,"people",str(year),"Los Angeles County","S05","Official projection, Vintage 2026 / Baseline 2024. Not an observed count or rent forecast.","FIPS 6037",kind="projection")
for year, val in [(2025,3546497),(2030,3635392),(2035,3711086),(2040,3779507)]:
    m(f"DH{year}","Area projections","DOF county household projection",val,"households",f"January 1, {year}","Los Angeles County","S47","Official projection, Vintage 2025 / Baseline 2024; LA 2026-2030 revised. Household growth can coexist with population decline.","FIPS 6037",kind="projection")
for i, metric, vals in [
 ("SP","SCAG county population planning forecast",[(2019,10046000),(2030,10214000),(2045,10757000),(2050,10793000)]),
 ("SH","SCAG county household planning forecast",[(2019,3393000),(2030,3784000),(2045,4120000),(2050,4155000)]),
 ("SE","SCAG county employment planning forecast",[(2019,5031000),(2030,5277000),(2050,5461000)]),
]:
    for year,val in vals:
        m(f"{i}{year}","Area projections",metric,val,"people" if i=="SP" else "households" if i=="SH" else "jobs",str(year),"Los Angeles County","S08","Adopted 2024 policy-driven planning forecast; rounded. Do not average with DOF demographic projections.","Tables 3.14-8/9/10; ES-1/2-1",kind="projection")
m("D14","Area projections","DOF projection release vintage","Vintage 2026, released 2026-03-13","label","2026","California","S06","Baseline 2024 assumptions unchanged; latest published July 1 estimates incorporated.","Release notes",kind="rule")

# Schools.
m("E01","Schools","LAUSD enrollment",497105,"students","2025-26","Los Angeles Unified","S09","District-wide; subject attendance area unknown.")
m("E02","Schools","LAUSD English learners",81328,"students","2025-26","Los Angeles Unified","S09","District-wide count.")
m("E03","Schools","LAUSD English learner share",16.4,"percent","2025-26","Los Angeles Unified","S09","District-wide share.")
m("E04","Schools","Four-year adjusted cohort graduation rate",86.2,"percent","2024-25","LAUSD, default non-charter report","S10","29,358 cohort students; 25,304 regular diploma graduates. Charter schools excluded by default filter.","Report Totals")
m("E05","Schools","Dashboard combined four/five-year graduation measure",86.5,"percent","2025 Dashboard","Los Angeles Unified","S11","Different measure from E04; do not label as a four-year-only rate.")
m("E06","Schools","Dashboard four-year graduation component",84.6,"percent","2025 Dashboard","Los Angeles Unified","S11","Different filter/population from DataQuest default report.")
m("E07","Schools","Chronic absenteeism",21.9,"percent","2025 Dashboard","Los Angeles Unified","S11","District-wide engagement indicator.")
m("E08","Schools","ELA distance from standard",-17.8,"points","2025 Dashboard","LAUSD all students","S12","17.8 points below standard; increased 10.4 points. Not a proficiency rate.")
m("E09","Schools","Mathematics distance from standard",-48.9,"points","2025 Dashboard","LAUSD all students","S12","48.9 points below standard; increased 11.5 points. Not a proficiency rate.")
unknown("E10","Schools","Assigned elementary/middle/high school quality","school report","Subject property","S12","Attendance boundaries and school-level outcomes require the location; city/district averages are not a substitute.")

# Employment and economic drivers.
m("J01","Employment","County unemployment rate, not seasonally adjusted",4.5,"percent","September 2026","Los Angeles County","S03","Matches BLS county NSA series; do not mix with EDD seasonally adjusted 4.8%.")
m("J02","Employment","County unemployment rate, seasonally adjusted",4.8,"percent","September 2026","Los Angeles County","S03","EDD seasonally adjusted series.")
m("J03","Employment","County total nonfarm payrolls, not seasonally adjusted",4593800,"jobs","September 2026 preliminary","Los Angeles County","S03","EDD industry table; +20,300 / +0.4% year over year.")
m("J04","Employment","Metro division nonfarm payrolls, seasonally adjusted",6282100,"jobs","September 2026","LA-Long Beach-Glendale metro division","S02","BLS summary uses a different series/vintage from EDD NSA county payrolls; +30,200 / +0.5% year over year.")
m("J05","Employment","Leisure and hospitality payrolls",782000,"jobs","September 2026","Los Angeles metro area summary","S02","BLS regional summary; +11,500 year over year.")
m("J06","Employment","Information payrolls",187000,"jobs","September 2026","Los Angeles metro area summary","S02","BLS regional summary; -11,400 year over year.")
m("J07","Employment","Education and health services payrolls",1340700,"jobs","September 2026","Los Angeles metro area summary","S02","BLS regional summary; +49,100 year over year.")
m("J08","Employment","County average weekly wage",1704,"USD/week","Q1 2026","Los Angeles County","S02","QCEW covered employment; not household income.")
m("J09","Employment","All-items CPI year-over-year",3.7,"percent","September/October 2026 summary window","Los Angeles area","S02","Use the BLS summary's stated CPI period; not a rent escalator.")
m("J10","Employment","Food CPI year-over-year",2.8,"percent","September/October 2026 summary window","Los Angeles area","S02","Menu-cost pressure differs from headline CPI.")
m("J11","Employment","Energy CPI year-over-year",20.3,"percent","September/October 2026 summary window","Los Angeles area","S02","Volatile component; not extrapolated.")
m("J12","Employment","County personal income",818500000000,"USD","2024","Los Angeles County","S04","BEA release; nominal personal income, not GDP.")
m("J13","Economic drivers","Port container throughput",1042652,"TEU","September 2026","Port of Los Angeles","S37","Record month; trade exposure is indirect for a central-LA restaurant.")
m("J14","Economic drivers","Port loaded imports",545696,"TEU","September 2026","Port of Los Angeles","S37","Use the port's own release; third-party search snippets contained conflicting import figures.")
m("J15","Economic drivers","Visitor volume",49500000,"visitors","2025","Los Angeles destination","S38","Official tourism organization estimate; not a census count.")
m("J16","Economic drivers","Visitor-generated business sales",42600000000,"USD","2025","Los Angeles region","S38","Modeled total business sales, not direct visitor spending or taxable retail sales.")
m("J17","Economic drivers","D Line Section 1 opening","May 8, 2026","date","2026","Wilshire/La Brea, Fairfax, La Cienega","S36","Three new stations open; Sections 2-3 remain under construction. Site proximity unknown.")
m("J18","Public realm","City Reserve Fund",515100000,"USD","FY 2026-27 revised budget","City of Los Angeles","S45","Council release states 6.00% of General Fund revenues; combined reserves approximately 9%.")
m("J19","Public realm","Legacy crime dataset status","No longer updated; NIBRS replacement","label","Notice retrieved 2026-11-08","City of Los Angeles","S46","Do not present 2020-2024 UCR data as current 2026 crime conditions.",kind="rule")
unknown("J20","Public realm","2026 point-in-time homelessness count","people","Los Angeles city/county","S39","LAHSA 2026 release endpoint returned a runtime error; HUD AHAR index is available but no 2026 local count is asserted.")
unknown("J21","Public realm","Current neighborhood crime rate","rate per relevant exposure","Subject trade area","S46","Requires current NIBRS series, consistent offense definitions and a defined geography.")

# Labor rules.
m("L01","Employment","Statewide minimum wage",16.90,"USD/hour","Effective January 1, 2026","California","S13","General state minimum; local and industry rules may be higher.",kind="rule")
m("L02","Employment","Covered fast-food minimum wage",20.00,"USD/hour","AB 1228 regime","California covered employers","S14","Coverage depends on national limited-service chain criteria; confirm operator coverage.",kind="rule")
m("L03","Employment","City general minimum wage",18.42,"USD/hour","Effective July 1, 2026","City of Los Angeles","S15","Employer-size and coverage rules apply; fast-food rate analyzed separately.",kind="rule")

# Tenant and lease.
m("T01","Tenant & lease","JACK company-operated restaurants",149,"restaurants","July 5, 2026","Jack in the Box system","S19","System count, not subject operator.")
m("T02","Tenant & lease","JACK franchised restaurants",1966,"restaurants","July 5, 2026","Jack in the Box system","S19","System count, not subject operator.")
m("T03","Tenant & lease","JACK total restaurants (derived)",2115,"restaurants","July 5, 2026","Jack in the Box system","S19","149 + 1,966; also stated in the 10-Q overview.",kind="derived")
m("T04","Tenant & lease","Franchised share of system (derived)",92.95,"percent","July 5, 2026","Jack in the Box system","S19","1,966 / 2,115; rounded. Franchise model shifts credit analysis toward operators.",kind="derived")
m("T05","Tenant & lease","System same-store sales change, quarter",-1.1,"percent","12 weeks ended July 5, 2026","Jack in the Box system","S16","Company -0.9%; franchise -1.2%. Not this store's sales.","MD&A results of operations")
m("T06","Tenant & lease","System same-store sales change, year to date",-4.2,"percent","40 weeks ended July 5, 2026","Jack in the Box system","S16","Year-to-date includes a 16-week first quarter.","MD&A results of operations")
m("T07","Tenant & lease","Year-to-date restaurant closures",40,"restaurants","40 weeks ended July 5, 2026","Jack in the Box system","S16","2 company and 38 franchise closures; 19 openings. Not a parcel renewal probability.","MD&A restaurant count table")
m("T08","Tenant & lease","Cash and cash equivalents",46318000,"USD","July 5, 2026","JACK consolidated","S17","Balance-sheet cash; liquidity section separately reports $71.8M cash plus restricted cash.")
m("T09","Tenant & lease","Current portion of long-term debt",44160000,"USD","July 5, 2026","JACK consolidated","S17","Corporate debt, not subject mortgage.")
m("T10","Tenant & lease","Long-term debt, noncurrent",1428667000,"USD","July 5, 2026","JACK consolidated","S17","Corporate debt, not subject mortgage.")
m("T11","Tenant & lease","Total stockholders' deficit",-901286000,"USD","July 5, 2026","JACK consolidated","S17","Negative book equity is not by itself a default prediction.")
m("T12","Tenant & lease","Revenue, year to date",861438000,"USD","40 weeks ended July 5, 2026","JACK consolidated","S18","Continuing operations; Del Taco reported as discontinued.")
m("T13","Tenant & lease","Net earnings, year to date",27909000,"USD","40 weeks ended July 5, 2026","JACK consolidated","S18","Continuing earnings $47.971M less discontinued loss $20.062M.")
m("T14","Tenant & lease","Operating cash flow, year to date",56553000,"USD","40 weeks ended July 5, 2026","JACK continuing operations","S16","Down from $118.147M; filing cites working-capital changes and franchisee payment delays/deferrals.","Liquidity and capital resources")
m("T15","Tenant & lease","Available Variable Funding Notes",54600000,"USD","July 5, 2026","JACK consolidated","S16","Under a $150.0M facility; management expects sufficient liquidity for at least the next twelve months.","Liquidity and capital resources")
m("T16","Tenant & lease","Franchise restaurant average unit volume",1874000,"USD/year","FY2025","Jack in the Box franchise system","S20","Official filing excerpt: $1,874 thousand AUV. System average; never used as subject sales or rent.","MD&A franchise results")
m("T17","Tenant & lease","Company statement on lease renewals","Generally able to renew at then-current market rates","quotation summary","FY2025 10-K","JACK system leases","S20","A general corporate statement, not a renewal guarantee or probability for this lease.","Lease note")
m("T18","Tenant & lease","Typical new restaurant prototype size",1372,"square feet","FY2025 10-K","New CRAVED prototype","S20","New prototype only; subject building may be larger or smaller.","Site Selection and Design")
m("T19","Tenant & lease","FY2025 Jack in the Box closures",86,"restaurants","FY2025","Jack in the Box system","S49","Official preliminary-proxy excerpt: 31 openings, 86 closures, net -55 units; 51 closures in block program.","Unit activity excerpt")
for i, name, unit, why in [
 ("P01","Exact jurisdiction and location","address/jurisdiction","Determines city vs county taxes, schools, hazards, zoning and comparable sales."),
 ("P02","Exact lease expiry and all option terms","date/term","The 2030-2035 range is too wide for a property-specific decision; options may be unilateral."),
 ("P03","Contract rent, escalations and percentage rent","USD/terms","Actual NOI cannot be inferred from franchise AUV."),
 ("P04","Tenant legal entity and guarantor","entity/credit","Brand affiliation does not establish who owes rent."),
 ("P05","Landlord repair, roof/structure, parking and ADA duties","lease clauses","NNN labels do not eliminate all landlord obligations."),
 ("P06","Store-level sales, rent coverage and payment history","ratio/history","Needed to assess renewal economics and operator capacity."),
 ("P07","Current executable sale offers","USD/terms","Asking prices and portfolio cap rates are not offers."),
 ("P08","Owner tax basis, depreciation recapture and entity type","USD/entity","After-tax proceeds cannot be computed without these inputs."),
 ("P09","Property debt, rate, maturity, prepayment and assumptions","USD/terms","Leverage and refinancing can dominate equity outcomes."),
 ("P10","Insurance coverage, exclusions, deductibles and quotes","policy/USD","Especially earthquake, flood, ordinance/law and business interruption."),
 ("P11","Building/lot size, condition, access, parking and drive-thru rights","physical/legal","Reuse value and re-tenanting costs depend on the actual site."),
 ("P12","Environmental history and Phase I/II findings","reports","Gas-station/restaurant history and nearby cleanup sites matter."),
 ("P13","Owner liquidity needs, concentration and risk tolerance","constraints","Wealth preservation/growth trade-off is owner-specific."),
 ("P14","Extension proposal, concessions and tenant investment commitment","USD/terms","Extension value depends on executable terms, not a signed wish list."),
]:
    src_id = {"P01":"S43","P02":"S20","P03":"S20","P04":"S16","P05":"S21","P06":"S16","P07":"S21","P08":"S27","P09":"S22","P10":"S33","P11":"S20","P12":"S42","P13":"S28","P14":"S20"}[i]
    req(i,"Property & owner",name,src_id,why,"Obtain and verify the underlying document privately; publish only anonymized, decision-relevant terms.")

# Capital markets and taxes.
m("C01","Capital markets","10-year Treasury constant-maturity yield",4.86,"percent","November 6, 2026","United States","S22","Indicative CMT yield; not a guaranteed reinvestment return.")
m("C02","Capital markets","30-year Treasury constant-maturity yield",5.26,"percent","November 6, 2026","United States","S22","Indicative CMT yield; duration and reinvestment risks differ from real estate.")
m("C03","Capital markets","Federal funds target range","3.75%-4.00%","range","October 28, 2026 decision","United States","S23","Policy rate, not a mortgage or cap rate.",kind="rule")
m("C04","Capital markets","NNN 2025 acquisition weighted-average cap rate",7.4,"percent","FY2025","NNN diversified acquisition portfolio","S21","Initial cash annual base rent / purchase price; includes non-QSR and non-LA assets.","Item 7, Property Acquisitions")
m("C05","Capital markets","NNN remaining lease term",10.2,"years","December 31, 2025","NNN portfolio","S21","Weighted average; not the subject lease term.","Item 7, Property Analysis")
m("C06","Capital markets","NNN 2025 disposition weighted-average cap rate",6.4,"percent","FY2025","NNN occupied dispositions","S21","Cash annual base rent / gross proceeds; acquisition and disposition yields answer different questions.","Item 7, Property Dispositions")
unknown("C07","Capital markets","Subject market cap rate and value","percent/USD","Subject property","S21","Requires current rent, lease term, credit, site quality and comparable closed transactions; no official parcel appraisal available.")
m("X01","Taxes","City base transfer tax rate",2.25,"USD per $500 or fraction","Current FAQ","City of Los Angeles","S24","Equivalent to 0.45% before rounding; county tax and exemptions handled separately.","Rate components",kind="rule")
m("X02","Taxes","ULA lower threshold after June 30, 2026",5400000,"USD","Transactions closing after June 30, 2026","City of Los Angeles","S24","4% applies only above this amount and below $10.9M; equality at $5.4M does not trigger ULA.","Threshold note",kind="rule")
m("X03","Taxes","ULA upper threshold after June 30, 2026",10900000,"USD","Transactions closing after June 30, 2026","City of Los Angeles","S24","5.5% applies at or above this amount.","Threshold note",kind="rule")
m("X04","Taxes","ULA lower-band rate",4.0,"percent","Transactions closing after June 30, 2026","City of Los Angeles","S24","Applies to the full consideration in the band, not only the excess; confirm exemptions.",kind="rule")
m("X05","Taxes","ULA upper-band rate",5.5,"percent","Transactions closing after June 30, 2026","City of Los Angeles","S24","Applies at or above $10.9M; confirm exemptions.",kind="rule")
m("X06","Taxes","Proposition 13 general levy limit",1.0,"percent of assessed value","General rule","California real property","S25","Voter-approved debt and direct assessments are additional; not the total tax bill.",kind="rule")
m("X07","Taxes","Assessed-value growth limit",2.0,"percent/year","General rule, with exceptions","California real property","S25","Reassessment on change in ownership/new construction can reset basis; not a market-value cap.",kind="rule")
m("X08","Taxes","1031 replacement-property identification deadline",45,"days after transfer","2025 instructions","U.S. real-property exchanges","S26","Strict deferred-exchange timing; qualified intermediary and other rules apply.",kind="rule")
m("X09","Taxes","1031 replacement-property receipt deadline",180,"days or return due date, whichever earlier","2025 instructions","U.S. real-property exchanges","S26","Earlier of 180 days or tax-return due date including extensions.",kind="rule")
m("X10","Taxes","Maximum federal rate on unrecaptured section 1250 gain",25.0,"percent","2025 taxable year","Federal individual taxpayers","S27","Applies to the relevant gain portion; not a flat tax on the whole sale.",kind="rule")
m("X11","Taxes","Net investment income tax rate",3.8,"percent","Current topic","Certain individuals/estates/trusts","S28","Applies to lesser of NII or MAGI above threshold; activity and entity facts matter.",kind="rule")
m("X12","Taxes","California out-of-state exchange reporting","Annual FTB 3840 until California-source deferred gain recognized","rule","2025 instructions","California-source property exchanged out of state","S29","Applies regardless of residence status; a 1031 exchange is deferral, not forgiveness.",kind="rule")
m("X13","Taxes","Ordinary REIT shares as direct 1031 replacement","Generally not qualifying real property","rule","2025 instructions","Federal exchange rules","S26","Stocks/bonds/partnership interests are excluded except narrow statutory exceptions; structure-specific counsel required.",kind="rule")

# Hazards and public data portals.
m("H01","Hazards","UCERF3 regional probability, M6.7+",60,"percent over 30-year model window","UCERF3 FAQ","Los Angeles region","S30","Regional event probability, not parcel damage probability; model is not a fresh 2026 forecast.","FAQ",extra=["S48"],kind="model")
m("H02","Hazards","UCERF3 regional probability, M7+",46,"percent over 30-year model window","UCERF3 FAQ","Los Angeles region","S30","Regional event probability, not parcel damage probability.","FAQ",extra=["S48"],kind="model")
m("H03","Hazards","UCERF3 regional probability, M7.5+",31,"percent over 30-year model window","UCERF3 FAQ","Los Angeles region","S30","Regional event probability, not parcel damage probability.","FAQ",extra=["S48"],kind="model")
m("H04","Hazards","ARkStorm total scenario cost",725000000000,"USD, scenario-era estimate","2011 publication","California hypothetical scenario","S31","$400B direct property + $325B business interruption; statewide scenario, not expected annual loss or parcel loss.",kind="model")
m("H05","Hazards","Eaton Fire structures destroyed",9414,"structures","January 2025 incident","Eaton Fire footprint","S32","County fact sheet; not a central-LA parcel exposure estimate.")
m("H06","Hazards","Palisades Fire structures destroyed",6837,"structures","January 2025 incident","Palisades Fire footprint","S32","County fact sheet; not a central-LA parcel exposure estimate.")
m("H07","Hazards","Combined fires estimated output loss","$5.2B-$10.1B","USD range","County anniversary fact sheet","Affected Los Angeles communities","S32","Economic output estimate, not insured loss or subject loss.",kind="model")
m("H08","Hazards","FAIR Plan assessment approved in Order 2025-1",1000000000,"USD","Bulletin 2025-4","California FAIR Plan member insurers","S33","Recoupment through policyholder surcharges requires commissioner approval; not automatic for every policy.",kind="rule")
unknown("H09","Hazards","FEMA county NRI composite score","0-100 relative score","Los Angeles County","S34","Legacy viewer retired; county download failed. Prior repository value 89.6 came from a Census-tract report URL, not a verified county value.")
unknown("H10","Hazards","Parcel flood zone and elevation","zone/elevation","Subject property","S40","Official effective FIRM/NFHL lookup requires location; flood insurance is separate from standard property coverage.")
unknown("H11","Hazards","Parcel wildfire hazard and ember exposure","zone/exposure","Subject property","S32","Fire perimeters, wind-driven ember exposure, defensible space and insurance require site review; regional fires do not establish parcel risk.")
unknown("H12","Hazards","Fault rupture, liquefaction and landslide zoning","zone/report","Subject property","S41","CGS EQ Zapp / official maps and geotechnical review required.",extra=["S50"])
unknown("H13","Hazards","Environmental cleanup / underground tank status","record","Subject property and nearby sites","S42","GeoTracker search and Phase I ESA required.")
unknown("H14","Hazards","Seismic retrofit and building-code status","report","Subject building","S41","Building age, structural system and retrofit records unknown; regional hazard does not equal building vulnerability.")

# Risk register: mechanisms and controls, not invented probabilities.
risk("R01","BAU","Lease-term erosion","Shorter remaining term can reduce buyer financing depth and increase renewal uncertainty even while rent is paid.","Start price discovery and extension discussions before the final marketing window; compare net proceeds, not headline price.","S20",["S21"])
risk("R02","BAU","Tenant/operator default","The rent obligor may be a franchise entity, not the publicly traded franchisor; store sales and guarantor capacity are unknown.","Obtain rent roll, payment history, store P&L, guaranty and entity credit before relying on brand credit.","S16")
risk("R03","BAU","Renewal at lower rent or with concessions","Market-rate renewal can reset rent down; free rent, TI and landlord work reduce effective NOI.","Underwrite effective rent after concessions and compare with executable sale offers.","S20")
risk("R04","BAU","Vacancy and re-tenanting","Drive-thru use, zoning, parking, grease interceptor, ADA and building condition can constrain reuse and extend downtime.","Verify entitlements/access and obtain contractor/leasing estimates; stress 0/12/24-month downtime without assigning probabilities.","S20",["S43"])
risk("R05","BAU","NNN leakage","Roof/structure, parking, capital replacements, insurance gaps or environmental duties may remain with the landlord.","Read every lease clause and property-condition report; reserve for non-recoverable costs.","S21")
risk("R06","BAU","Cap-rate and financing shock","Higher required yields reduce value; buyer debt terms can change independently of property NOI.","Stress entry/exit caps and financing separately; keep liquidity for carry and avoid forced-sale timing.","S22",["S21"])
risk("R07","BAU","Inflation above fixed escalators","Fixed bumps may lag operating costs and market rents; CPI is not automatically the lease escalator.","Compare contract escalator with cost exposure; negotiate resets only if economics justify it.","S02",["S20"])
risk("R08","BAU","Labor and food-cost pressure","Higher wages and volatile food/energy costs can compress operator margins and rent coverage even if brand sales hold.","Review store-level coverage, pricing power and franchisee liquidity; do not infer from system AUV.","S14",["S02","S16"])
risk("R09","BAU","Concentration and liquidity","A single building, tenant and location cannot be diversified or sold instantly without transaction costs.","Set owner-level liquidity reserve and concentration limit; compare with genuinely executable alternatives.","S21",["S28"])
risk("R10","BAU","Tax and exchange execution","ULA boundary, recapture, NIIT, debt relief and missed 1031 deadlines can materially reduce net proceeds.","Model jurisdiction-specific taxes and use qualified tax/exchange professionals before signing.","S24",["S26","S27","S29"])
risk("R11","BAU","Environmental liability","Prior fuel/restaurant uses or nearby cleanup sites can create investigation, remediation and financing friction.","Phase I ESA, GeoTracker review and insurance/indemnity analysis; indemnity is only as strong as the obligor.","S42",["S21"])
risk("R12","BAU","Construction and access disruption","Nearby transit/street work can temporarily alter visibility, parking and customer access; long-run transit benefits are site-specific.","Check current project notices and actual frontage/access before underwriting a location premium.","S36")
risk("R13","BAU","Public-realm and demand shifts","Crime, homelessness, office attendance, tourism and household budgets can affect a specific block differently from city averages.","Use current official neighborhood data and site visits; leave unavailable current counts blank.","S46",["S39","S01"])
risk("R14","BAU","Insurance cost and availability","Premiums, deductibles, exclusions and FAIR Plan-related surcharges can change NOI and financeability.","Bindable quotes, replacement-cost review, ordinance/law and business-interruption limits; stress non-recoverable premiums.","S33")
risk("R15","Rare / severe","Earthquake and lifeline outage","Shaking, liquefaction, fault rupture or utility interruption can damage the building and stop sales even without total loss.","Site-specific seismic review, retrofit options, earthquake coverage and liquidity; do not convert regional odds into parcel loss.","S30",["S41","S48"])
risk("R16","Rare / severe","Wind-driven wildfire / ember event","The 2025 fires show severe losses can occur beyond intuitive forest-edge locations; smoke and evacuation also interrupt business.","Parcel fire/ember review, hardening, insurance and continuity plan; no parcel probability assigned.","S32",["S33"])
risk("R17","Rare / severe","Extreme atmospheric-river flooding","ARkStorm illustrates correlated property damage, business interruption and weeks-to-months lifeline restoration.","Flood mapping, drainage/elevation review, flood and BI coverage, emergency liquidity; scenario is not an annual forecast.","S31",["S40"])
risk("R18","Rare / severe","Franchisee or supply-chain failure","Operator bankruptcy, payment deferrals, food-safety event or distributor failure can interrupt rent and brand demand.","Tenant financial surveillance, guaranty review, guarantor diversification and lease-remedy analysis.","S16",["S20"])
risk("R19","Rare / severe","Debt/capital-market freeze","Refinancing may be unavailable or expensive at the owner or tenant level precisely when sale bids are weak.","Stagger maturities, avoid near-term forced sales, maintain reserves and test covenant/headroom scenarios.","S22",["S16"])
risk("R20","Rare / severe","Correlated regional shock","Trade disruption, entertainment contraction, disaster and fiscal stress can hit demand, costs and exit liquidity together.","Use combined downside scenarios rather than treating every risk as independent; preserve optionality.","S03",["S37","S32","S45"])

# Decision framework. No strategy receives a fabricated expected return or ranking.
decision("A","Sell before expiry","Executable offer clears after-tax, after-debt and reinvestment hurdles; buyer demand is deepest before short-term rollover risk.","Converts illiquid concentration into cash; removes future tenant/capex/disaster exposure.","Tax, transfer costs, prepayment penalties and reinvestment risk; a 1031 exchange defers rather than eliminates gain.","Viable; compare on net spendable proceeds and replacement-asset quality, not asking price.","S26",["S24","S27","S21"])
decision("B","Extend, then sell","Tenant signs a creditworthy, market-supported extension with limited landlord concessions and buyers pay for the added term.","Longer term can improve financeability and buyer pool; preserves rent during marketing.","Concessions/TI, time, market-rate reset risk and no guarantee of cap-rate compression.","Preferred candidate only if extension economics beat the best current net offer after costs and risk.","S20",["S21","S22"])
decision("C","Extend and hold long term","Rent coverage, guaranty, escalators, site quality and owner liquidity support continued concentration.","Retains income and potential land/location upside; avoids immediate sale tax.","Single-tenant, single-site, insurance, capex and future rollover risk remain.","Viable for an owner who can absorb a long vacancy and a severe correlated shock; not the default.","S16",["S33","S28"])
decision("D","Hold without extension","Near-term cash yield and liquidity needs justify waiting, with a defined review trigger.","Avoids premature sale and transaction costs.","Remaining term erodes; renewal and exit uncertainty can compound.","Avoid passive drift; set a dated decision gate before the lease becomes short-term.","S20",["S21"])
decision("E","Sell and exchange into diversified real property","Qualifying replacement assets, financing and 45/180-day execution are realistic; California-source reporting is understood.","Defers qualifying gain and can reduce single-site concentration if multiple assets/tenants are acquired.","Replacement quality, timing, intermediary, boot, debt replacement and FTB 3840 obligations.","Viable; ordinary REIT shares are not a direct like-kind replacement.","S26",["S29","S44"])
decision("F","Sell and hold liquid reserves / Treasury ladder","Preservation and near-term liquidity dominate; owner accepts taxable sale and lower/different return profile.","Reduces single-asset operating and disaster exposure; maturities can be matched to needs.","Tax drag, inflation, duration and reinvestment risk; CMT yields are not executable offers.","Legitimate preservation benchmark, not an automatic wealth-maximizing answer.","S22",["S27","S28"])
decision("G","Recapitalize / refinance owner debt","Debt terms create value without a sale and covenants/reserves remain manageable.","Can release liquidity while retaining ownership.","Adds leverage, maturity and covenant risk; does not solve tenant or location concentration.","Only after debt-service and downside stress; not a substitute for the hold/sell decision.","S22",["S16"])
decision("H","Partial interest / structured sale","A genuine partner or installment structure improves diversification and tax timing without unacceptable counterparty risk.","May share risk and spread proceeds.","Complexity, control, counterparty credit and tax rules; installment sale is not a 1031 exchange.","Explore only with executable terms and qualified counsel; no assumed buyer or pricing.","S26",["S27"])

# Flags are deliberately published; they do not block a technically sound build.
flag("F01","High","Property identity","No exact location, parcel, lease, rent, tenant entity, debt, basis or offer is available in the public brief.","Historical models use placeholder rent/expiry and precise rankings.","Keep observed fields blank; publish conditional decision rules and scenarios only.","S20",extra=["S43"])
flag("F02","High","Historical model","Root model converts 8% of franchise AUV into a $150,000 rent assumption and uses 2032 midpoint expiry, then reports precise wealth differences.","tools/model.py lines 31-47 and data/valuation.json A1/A3; generated root pages inherit these assumptions.","Do not endorse historical dollar rankings; current model normalizes NOI to 100 and labels every assumption.","S20")
flag("F03","High","Historical hazard data","Prior ledger labels 89.6 composite / 97.8 earthquake as urban-LA or county values, but the cited official viewer URL is a Census tract (06037295103).","session-18dacdea/data/metrics.json M-73 and source S24; FEMA now routes legacy viewer to RAPT.","County score left blank; tract values are not county or parcel values.","S34",extra=["S35"])
flag("F04","High","Tax boundary","Historical ULA logic must apply 4% only above $5.4M, not at equality, for post-June-2026 closings; jurisdiction and exemptions also matter.","Official Finance FAQ threshold table; current tests cover equality and both bands.","Use strict lower-bound comparison and parcel jurisdiction gate; obtain closing-date tax confirmation.","S24")
flag("F05","Medium","Forecast disagreement","DOF projects county population decline while SCAG's adopted planning forecast projects growth; households rise in both official systems.","DOF P-2A vs SCAG Appendix I; different baselines, methods and policy assumptions.","Show both separately; never average them or convert population growth into rent growth.","S05",extra=["S08","S47"])
flag("F06","Medium","Employment series","BLS and EDD payroll/unemployment figures differ because of geography, seasonal adjustment and revision vintage.","BLS November summary vs EDD September preliminary release.","Label each series; do not splice them into one trend.","S02",extra=["S03"])
flag("F07","Medium","School measures","DataQuest default non-charter ACGR 86.2% differs from Dashboard combined 86.5% and four-year component 84.6%.","Official CDE report filters and indicator definitions.","Keep measures separate and do not assign district outcomes to the unknown subject school.","S10",extra=["S11"])
flag("F08","Medium","Tenant credit","Public franchisor financials are not the subject franchisee's financials; current filing reports franchisee payment delays/deferrals.","JACK Q3 FY2026 liquidity section and restaurant-count note.","Require operator/guarantor financials and store rent coverage before credit scoring.","S16")
flag("F09","Medium","Capital-market benchmark","NNN acquisition cap 7.4% and portfolio WALT 10.2 years are diversified portfolio statistics, not this asset's cap rate or term.","NNN FY2025 10-K Item 7 definitions.","Use only as labeled context; subject value remains blank.","S21")
flag("F10","Medium","Unavailable official endpoint","LAHSA 2026 count release and PDF returned runtime errors during review.","Official search excerpt exists, but live primary retrieval failed.","Leave count blank and flag; do not replace with third-party numbers.","S39")
flag("F11","Medium","Unavailable hazard download","FEMA county NRI ZIP download failed; legacy NRI application is retired.","OpenFEMA download page retrieved; RAPT is current entry point.","Leave county score blank; use methodology and official parcel portals instead.","S35",extra=["S34"])
flag("F12","Medium","Broken legacy hazard link","Legacy CAL FIRE FHSZ viewer URL returned 404.","egis.fire.ca.gov/FHSZ retrieval on 2026-11-08.","Verified OSFM replacement page is now used; parcel lookup remains blank.","S51","resolved",["S32"])
flag("F13","Medium","Historical crime data","City's 2020-2024 UCR dataset is no longer updated; NIBRS replacement uses a different reporting system.","Official dataset notice retrieved 2026-11-08.","Do not call historical counts current; compute neighborhood trends only from a consistent current series.","S46")
flag("F14","Medium","Earthquake probability window","USGS FAQ probabilities come from UCERF3, a 2014/2015 model family, not a newly estimated 2026-2056 window.","USGS FAQ and 2015 time-dependent publication.","Label model vintage and regional scope; no parcel damage probability.","S30",extra=["S48"])
flag("F15","Medium","Historical verification claims","Existing checkers validate source IDs and text patterns, not agreement between every generated sentence and the underlying source table.","tools/check_site.py and historical verification pages.","Current checker validates row links, blank unknowns, arithmetic, privacy and internal links; source-value audit is recorded separately.","S01")
flag("F16","Low","Realty Income source","Previously cited supplemental PDF could not be retrieved in this environment.","investor.realtyincome.com Q4 2025 supplemental fetch failed.","Use SEC-filed NNN benchmark instead; do not assert the inaccessible 7.3% figure as freshly verified.","S21")
flag("F17","Low","Tourism impact estimate","Visitor business sales and jobs are modeled economic impacts from the official tourism organization, not government observations.","2025 report compiled by Tourism Economics and Los Angeles Tourism.","Label source type and do not treat $42.6B as direct spending or GDP.","S38")
flag("F18","Low","Port source conflict","Third-party search snippets disagreed with the port's own loaded-import figure.","Port release states 545,696 loaded imports for September 2026.","Use the port release; exclude third-party variants.","S37")
flag("F19","Medium","Coordination history","Historical board contains stale in-progress rows and inconsistent workspace counts; current platform pins one Arena branch.","COORDINATION.md A-H history; Session I appended without editing other claims.","Preserve history, document branch exception, and change shared navigation only in final integration.","S01")
flag("F20","High","Privacy","Public repository and Pages can expose committed files; private owner/operator details must never enter the public product.","No private documents were supplied or persisted in this session.","Use placeholders, blank unknowns, automated identifier scans and no analytics/forms/uploads.","S28")

# Write canonical ledgers.
def dump(name, rows, **meta):
    payload = dict(meta=dict(as_of=AS_OF, **meta), rows=rows)
    (DATA / name).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

dump("sources.json", SOURCES, note="Primary official sources; status distinguishes direct reads, search excerpts, partial retrieval and unavailable endpoints.")
dump("metrics.json", METRICS, note="Verified source-checked observations, official projections and rules are labeled by kind. Unknowns are blank. No subject rent/value is inferred.")
dump("requirements.json", REQUIREMENTS, note="All property/owner observed values remain blank until documents are available.")
dump("risks.json", RISKS, note="Qualitative mechanisms and mitigations; no invented probabilities.")
dump("decisions.json", DECISIONS, note="Conditional decision framework, not a fabricated expected-return ranking.")
dump("flags.json", FLAGS, note="Open review items are published and nonblocking for a technically sound site.")
print(f"built {len(SOURCES)} sources, {len(METRICS)} metrics, {len(REQUIREMENTS)} requirements, {len(RISKS)} risks, {len(DECISIONS)} decisions, {len(FLAGS)} flags")
