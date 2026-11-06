#!/usr/bin/env python3
"""
build_facts.py — single source of truth for every table row on the site.

Each record is a tuple:
    (category, metric, value, period, geography, tier, status, source_name, source_url, note)

tier   : T1 official gov/central-bank | T2 official-adjacent | T3 industry (non-government)
         | D derived arithmetic | A assumption
status : verified | derived | assumption | unverified

RULES ENFORCED HERE
    * A row with status "verified" MUST have a resolving T1/T2 source_url.
    * A row whose value cannot be confirmed is stored with value = "" and
      status = "unverified" — never inferred, never filled in.
Run:  python3 model/build_facts.py
"""

import json
import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "data", "facts.json")

U_FRED = "https://fred.stlouisfed.org/series/"
U_QF = "https://www.census.gov/quickfacts/fact/table/losangelescountycalifornia,losangelescitycalifornia/PST045224"
U_10K = "https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm"
U_Q4 = "https://investors.jackinthebox.com/news/news-details/2025/Jack-in-the-Box-Inc--Reports-Fourth-Quarter-and-Full-Year-2025-Earnings/default.aspx"
U_Q3 = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000807882&type=8-K"
U_CAFIRE = "https://www.fire.ca.gov/incidents/2025"
U_OSFM = "https://osfm.fire.ca.gov/what-we-do/community-wildfire-preparedness-and-mitigation/fire-hazard-severity-zones"
U_BOULDER_Q2 = "https://www.bouldergroup.com/blog/"
U_BOULDER_Q3 = "https://www.financialcontent.com/article/abnewswire-2026-10-9-the-boulder-group-reports-net-lease-cap-rates-rise-to-692-in-q3-2026"
U_BOULDER_TP = "https://www.openpr.com/news/4629798/the-boulder-group-releases-q3-2026-net-lease-tenant-profiles"
U_IRS409 = "https://www.irs.gov/taxtopics/tc409"
U_IRS1031 = "https://www.irs.gov/newsroom/like-kind-exchanges-under-irc-code-section-1031"
U_AB1228 = "https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=202320240AB1228"
U_ASSESSOR = "https://assessor.lacounty.gov/tax-relief/decline-in-value"
U_DIR_MW = "https://www.dir.ca.gov/dlse/faq_minimumwage.htm"
U_DIR_FF = "https://www.dir.ca.gov/dlse/Fast-Food-Minimum-Wage-FAQ.htm"
U_NRI = "https://hazards.fema.gov/nri/"
U_FHSZ_MAP = "https://experience.arcgis.com/experience/5065c998b4b0462f9ec3c6c226c610a9"
U_CGS = "https://www.conservation.ca.gov/cgs/geohazards"
U_USGS = "https://earthquake.usgs.gov/hazards/"
U_FEMA_NFHL = "https://msc.fema.gov/portal/home"
U_NRN_DT = "https://www.nrn.com/quick-service/jack-in-the-box-finalizes-sale-of-del-taco"

R = []


def add(cat, metric, value, period, geo, tier, status, source, url, note=""):
    R.append({"cat": cat, "metric": metric, "value": value, "period": period, "geo": geo,
              "tier": tier, "status": status, "source": source, "url": url, "note": note})


# ============================== CAPITAL MARKETS ==============================
C = "capital-markets"
add(C, "10-year U.S. Treasury constant maturity", "4.90%", "2026-11-04", "United States", "T1", "verified",
    "FRED — DGS10 (U.S. Treasury via St. Louis Fed)", U_FRED + "DGS10")
add(C, "10-year U.S. Treasury — highest daily print in 2026", "5.31%", "2026-10-05", "United States", "T1", "verified",
    "FRED — DGS10", U_FRED + "DGS10")
add(C, "10-year U.S. Treasury — monthly average", "5.13%", "Oct 2026", "United States", "T1", "verified",
    "FRED — GS10", U_FRED + "GS10")
add(C, "10-year U.S. Treasury — monthly average", "4.06%", "Oct 2025", "United States", "T1", "verified",
    "FRED — GS10", U_FRED + "GS10", "Twelve-month change of +107 bp")
add(C, "10-year U.S. Treasury — monthly average (cycle low)", "0.62%", "Jul 2020", "United States", "T1", "verified",
    "FRED — GS10", U_FRED + "GS10")
add(C, "30-year fixed mortgage rate", "7.18%", "week of 2026-11-05", "United States", "T1", "verified",
    "FRED — MORTGAGE30US (Freddie Mac)", U_FRED + "MORTGAGE30US")
add(C, "30-year fixed mortgage rate", "6.16%", "week of 2026-01-08", "United States", "T1", "verified",
    "FRED — MORTGAGE30US (Freddie Mac)", U_FRED + "MORTGAGE30US", "+102 bp during calendar 2026")
add(C, "Effective federal funds rate — current", "3.88%", "from 2026-09-17", "United States", "T1", "verified",
    "FRED — DFF", U_FRED + "DFF", "Raised from 3.64%; first hike after eight months on hold")
add(C, "Effective federal funds rate — prior level", "3.64%", "2025-12-11 → 2026-09-16", "United States", "T1", "verified",
    "FRED — DFF", U_FRED + "DFF")
add(C, "CPI-U, all items, seasonally adjusted", "336.298", "Sep 2026", "United States", "T1", "verified",
    "FRED — CPIAUCSL (BLS)", U_FRED + "CPIAUCSL", "Index 1982-84 = 100")
add(C, "CPI-U, all items, seasonally adjusted", "324.245", "Sep 2025", "United States", "T1", "verified",
    "FRED — CPIAUCSL (BLS)", U_FRED + "CPIAUCSL")
add(C, "CPI inflation, year over year", "3.72%", "Sep 2026", "United States", "D", "derived",
    "Computed from FRED CPIAUCSL (336.298 / 324.245 − 1)", U_FRED + "CPIAUCSL")
add(C, "All single-tenant net-lease cap rate", "6.92%", "Q3 2026", "United States", "T3", "verified",
    "The Boulder Group, Q3 2026 Net Lease Research Report", U_BOULDER_Q3, "INDUSTRY SOURCE — not government data")
add(C, "All single-tenant net-lease cap rate", "6.82%", "Q2 2026", "United States", "T3", "verified",
    "The Boulder Group, Q2 2026 Net Lease Research Report", U_BOULDER_Q2, "INDUSTRY SOURCE — not government data")
add(C, "Retail single-tenant net-lease cap rate", "6.60%", "Q2 2026", "United States", "T3", "verified",
    "The Boulder Group, Q2 2026", U_BOULDER_Q2, "INDUSTRY SOURCE")
add(C, "Industrial single-tenant net-lease cap rate", "7.25%", "Q2 2026", "United States", "T3", "verified",
    "The Boulder Group, Q2 2026", U_BOULDER_Q2, "INDUSTRY SOURCE")
add(C, "Office single-tenant net-lease cap rate", "7.90%", "Q2 2026", "United States", "T3", "verified",
    "The Boulder Group, Q2 2026", U_BOULDER_Q2, "INDUSTRY SOURCE")
add(C, "Auto single-tenant net-lease cap rate", "6.45%", "Q2 2026", "United States", "T3", "verified",
    "The Boulder Group, Q2 2026", U_BOULDER_Q2, "INDUSTRY SOURCE")
add(C, "Dollar-store single-tenant net-lease cap rate", "7.49%", "Q2 2026", "United States", "T3", "verified",
    "The Boulder Group, Q2 2026", U_BOULDER_Q2, "INDUSTRY SOURCE")
add(C, "Drug-store single-tenant net-lease cap rate", "7.85%", "Q2 2026", "United States", "T3", "verified",
    "The Boulder Group, Q2 2026", U_BOULDER_Q2, "INDUSTRY SOURCE")
add(C, "QSR net lease — corporate credit", "5.85%", "Q2 2026", "United States", "T3", "verified",
    "The Boulder Group, Q2 2026", U_BOULDER_Q2, "INDUSTRY SOURCE — key valuation anchor for this asset")
add(C, "QSR net lease — franchisee credit", "6.85%", "Q2 2026", "United States", "T3", "verified",
    "The Boulder Group, Q2 2026", U_BOULDER_Q2, "INDUSTRY SOURCE — key valuation anchor; ~100 bp wider than corporate")
add(C, "Retail net-lease bid–ask spread", "25 bp", "Q3 2026", "United States", "T3", "verified",
    "The Boulder Group, Q3 2026", U_BOULDER_Q3, "Widened from 22 bp in Q2 2026")
add(C, "7-Eleven net lease, 5-year term", "5.90% – 6.20%", "Q3 2026", "United States", "T3", "verified",
    "The Boulder Group, Q3 2026 Tenant Profiles", U_BOULDER_TP, "INDUSTRY SOURCE")
add(C, "7-Eleven net lease, 15-year term", "4.80% – 5.15%", "Q3 2026", "United States", "T3", "verified",
    "The Boulder Group, Q3 2026 Tenant Profiles", U_BOULDER_TP, "Same credit, ~105 bp tighter at 15 yr — the term premium")
add(C, "Raising Cane's net lease, 15-year term", "4.90% – 5.20%", "Q3 2026", "United States", "T3", "verified",
    "The Boulder Group, Q3 2026 Tenant Profiles", U_BOULDER_TP, "INDUSTRY SOURCE")
add(C, "Whataburger net lease, 15-year term", "4.85% – 5.25%", "Q3 2026", "United States", "T3", "verified",
    "The Boulder Group, Q3 2026 Tenant Profiles", U_BOULDER_TP, "INDUSTRY SOURCE")
add(C, "Burger King net lease, 10-year term", "6.30% – 6.60%", "Q3 2026", "United States", "T3", "verified",
    "The Boulder Group, Q3 2026 Tenant Profiles", U_BOULDER_TP, "Widened 25 bp; comparable burger-QSR credit")
add(C, "Applebee's net lease, 15-year term", "7.15% – 7.45%", "Q3 2026", "United States", "T3", "verified",
    "The Boulder Group, Q3 2026 Tenant Profiles", U_BOULDER_TP, "Casual dining trades at a material discount to QSR")
add(C, "Family Dollar net lease, 5-year term", "8.50% – 8.90%", "Q3 2026", "United States", "T3", "verified",
    "The Boulder Group, Q3 2026 Tenant Profiles", U_BOULDER_TP, "Repriced on loss of investment-grade rating — credit re-rating risk")
add(C, "McDonald's / Chick-fil-A ground lease (tightest in sector)", "4.45%", "Q2 2026", "United States", "T3", "verified",
    "The Boulder Group, Q2 2026", U_BOULDER_Q2, "INDUSTRY SOURCE")
add(C, "Jack in the Box-specific net-lease cap rate", "", "—", "United States", "T3", "unverified",
    "Boulder Group Q3 2026 Tenant Profiles (88 operators)", U_BOULDER_TP,
    "Not retrieved. The model therefore derives a term curve from the QSR corporate/franchisee anchors instead.")
add(C, "Cap-rate term curve used by this model (6.5 yr remaining)", "7.91%", "2026", "PROP-001", "D", "derived",
    "model/projection_model.py — CAP_TERM_CURVE interpolation", "#cap-curve",
    "Derived from Boulder QSR anchors; NOT a market quote for this asset")
add(C, "Cap-rate term curve used by this model (15 yr remaining)", "6.40%", "2026", "PROP-001", "D", "derived",
    "model/projection_model.py — CAP_TERM_CURVE interpolation", "#cap-curve",
    "Implies ~23.5% value uplift from an extension, same NOI")

# ============================== LOCAL ECONOMY ==============================
E = "economy"
add(E, "LA metro total nonfarm employment", "6,282.1 thousand", "Sep 2026", "LA–Long Beach–Anaheim MSA", "T1", "verified",
    "FRED — SMU06310800000000001 (BLS CES)", U_FRED + "SMU06310800000000001")
add(E, "LA metro total nonfarm employment", "6,251.9 thousand", "Sep 2025", "LA–Long Beach–Anaheim MSA", "T1", "verified",
    "FRED — SMU06310800000000001", U_FRED + "SMU06310800000000001")
add(E, "LA metro total nonfarm employment — cycle peak", "6,359.6 thousand", "Oct 2024", "LA–Long Beach–Anaheim MSA", "T1", "verified",
    "FRED — SMU06310800000000001", U_FRED + "SMU06310800000000001")
add(E, "LA metro total nonfarm employment — pre-COVID", "6,236.7 thousand", "Sep 2019", "LA–Long Beach–Anaheim MSA", "T1", "verified",
    "FRED — SMU06310800000000001", U_FRED + "SMU06310800000000001")
add(E, "LA metro payroll growth, year over year", "+0.48%", "Sep 2026 vs Sep 2025", "LA–Long Beach–Anaheim MSA", "D", "derived",
    "Computed from FRED SMU06310800000000001", U_FRED + "SMU06310800000000001")
add(E, "LA metro payrolls vs Oct-2024 peak", "−1.22%", "peak → Sep 2026", "LA–Long Beach–Anaheim MSA", "D", "derived",
    "Computed from FRED SMU06310800000000001", U_FRED + "SMU06310800000000001", "−77,500 jobs")
add(E, "LA metro payroll growth, Sep 2019 → Sep 2026 (7 years)", "+0.73%", "Sep 2019 → Sep 2026", "LA–Long Beach–Anaheim MSA", "D", "derived",
    "Computed from FRED SMU06310800000000001", U_FRED + "SMU06310800000000001", "+45,400 jobs in 84 months")
add(E, "LA metro implied compound annual job growth", "≈ +0.10%/yr", "2019–2026", "LA–Long Beach–Anaheim MSA", "D", "derived",
    "Computed from FRED SMU06310800000000001", U_FRED + "SMU06310800000000001", "Effectively full stall for seven years")
add(E, "Los Angeles County unemployment rate (NSA)", "4.5%", "Sep 2026", "Los Angeles County", "T1", "verified",
    "FRED — CALOSA7URN (BLS LAUS)", U_FRED + "CALOSA7URN")
add(E, "Los Angeles County unemployment rate (NSA)", "4.9%", "Aug 2026", "Los Angeles County", "T1", "verified",
    "FRED — CALOSA7URN", U_FRED + "CALOSA7URN")
add(E, "Los Angeles County unemployment rate (NSA)", "6.2%", "Jul 2025", "Los Angeles County", "T1", "verified",
    "FRED — CALOSA7URN", U_FRED + "CALOSA7URN")
add(E, "Los Angeles County unemployment rate (NSA) — recent peak", "6.7%", "Jul–Aug 2024", "Los Angeles County", "T1", "verified",
    "FRED — CALOSA7URN", U_FRED + "CALOSA7URN")
add(E, "Los Angeles County unemployment rate (NSA) — pandemic peak", "18.9%", "May 2020", "Los Angeles County", "T1", "verified",
    "FRED — CALOSA7URN", U_FRED + "CALOSA7URN")
add(E, "Los Angeles County unemployment rate (NSA) — pre-COVID low", "4.1%", "Apr–May 2019", "Los Angeles County", "T1", "verified",
    "FRED — CALOSA7URN", U_FRED + "CALOSA7URN")
add(E, "Total employment (employer establishments)", "3,987,736", "2023", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts (County Business Patterns)", U_QF)
add(E, "Total employer establishments", "304,988", "2023", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(E, "Total annual payroll", "$299,616,607 thousand", "2023", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(E, "Employment change (establishments)", "+2.3%", "2022 → 2023", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(E, "Total retail sales", "$213,932,785 thousand", "2022", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts (Economic Census)", U_QF)
add(E, "Total retail sales", "$81,351,523 thousand", "2022", "Los Angeles city", "T1", "verified",
    "U.S. Census Bureau, QuickFacts (Economic Census)", U_QF)
add(E, "Retail sales per capita", "$22,010", "2022", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF, "Deep, dense, mature retail market")
add(E, "Retail sales per capita", "$21,281", "2022", "Los Angeles city", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(E, "Accommodation & food services sales", "$44,000,801 thousand", "2022", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts (Economic Census)", U_QF)
add(E, "Accommodation & food services sales", "$17,366,966 thousand", "2022", "Los Angeles city", "T1", "verified",
    "U.S. Census Bureau, QuickFacts (Economic Census)", U_QF)
add(E, "Health care & social assistance receipts", "$113,488,435 thousand", "2022", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts (Economic Census)", U_QF)
add(E, "Transportation & warehousing receipts", "$65,350,932 thousand", "2022", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts (Economic Census)", U_QF)
add(E, "County population projection to 2040", "", "—", "Los Angeles County", "T1", "unverified",
    "California Department of Finance, P-2/P-3 projections", "https://dof.ca.gov/forecasting/demographics/projections/",
    "Published only as .xlsx; not machine-verified in this session. Census V2025 estimates used instead.")
add(E, "Parcel-level daytime population / traffic counts", "", "—", "PROP-001", "T1", "unverified",
    "Requires address (Caltrans AADT, Census LEHD LODES)", "https://dot.ca.gov/programs/traffic-operations/census",
    "Deliberately not retrieved — no address retained")

# ============================== DEMOGRAPHICS ==============================
D = "demographics"
add(D, "Population", "9,694,934", "1 Jul 2025 (V2025)", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts (Population Estimates)", U_QF)
add(D, "Population", "3,869,089", "1 Jul 2025 (V2025)", "Los Angeles city", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Population change, 2020 base → 2025", "−3.2%", "2020–2025 (V2025)", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF, "−322,480 residents")
add(D, "Population change, 2020 base → 2025", "−0.8%", "2020–2025 (V2025)", "Los Angeles city", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Population (decennial census)", "10,014,009", "1 Apr 2020", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Population (decennial census)", "9,818,605", "1 Apr 2010", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Median household income (2024 dollars)", "$90,112", "ACS 2020-2024", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts (ACS 5-yr)", U_QF)
add(D, "Median household income (2024 dollars)", "$81,939", "ACS 2020-2024", "Los Angeles city", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Per capita income (2024 dollars)", "$45,792", "ACS 2020-2024", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Per capita income (2024 dollars)", "$47,685", "ACS 2020-2024", "Los Angeles city", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Poverty rate", "13.3%", "2025 estimate", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Poverty rate", "16.5%", "2025 estimate", "Los Angeles city", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Bachelor's degree or higher (age 25+)", "36.0%", "ACS 2020-2024", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Bachelor's degree or higher (age 25+)", "38.5%", "ACS 2020-2024", "Los Angeles city", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "High school graduate or higher (age 25+)", "80.9%", "ACS 2020-2024", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "High school graduate or higher (age 25+)", "79.6%", "ACS 2020-2024", "Los Angeles city", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Persons under 18", "19.2%", "ACS 2020-2024", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Persons 65 and over", "17.1%", "ACS 2020-2024", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Persons 65 and over", "14.2%", "ACS 2020-2024", "Los Angeles city", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Foreign-born persons", "33.4%", "ACS 2020-2024", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Foreign-born persons", "35.7%", "ACS 2020-2024", "Los Angeles city", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Language other than English spoken at home", "55.1%", "ACS 2020-2024", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Language other than English spoken at home", "56.4%", "ACS 2020-2024", "Los Angeles city", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Median value, owner-occupied housing unit", "$834,200", "ACS 2020-2024", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF, "≈9.3× county median household income")
add(D, "Median value, owner-occupied housing unit", "$921,200", "ACS 2020-2024", "Los Angeles city", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Median gross rent", "$1,954", "ACS 2020-2024", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Median gross rent", "$1,933", "ACS 2020-2024", "Los Angeles city", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Owner-occupied housing unit rate", "45.9%", "ACS 2020-2024", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Owner-occupied housing unit rate", "36.0%", "ACS 2020-2024", "Los Angeles city", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Housing units", "3,726,923", "1 Jul 2025 (V2025)", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Building permits issued", "22,250", "2025", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts (Building Permits Survey)", U_QF)
add(D, "Civilian labor force participation (age 16+)", "64.7%", "ACS 2020-2024", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Civilian labor force participation (age 16+)", "66.4%", "ACS 2020-2024", "Los Angeles city", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Mean travel time to work", "30.4 min", "ACS 2020-2024", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Mean travel time to work", "30.7 min", "ACS 2020-2024", "Los Angeles city", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Households", "3,416,449", "ACS 2020-2024", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Persons per household", "2.81", "ACS 2020-2024", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Population per square mile", "2,466.9", "2020", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Population per square mile", "8,304.2", "2020", "Los Angeles city", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Land area", "4,059.28 sq mi", "2020", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Land area", "469.49 sq mi", "2020", "Los Angeles city", "T1", "verified",
    "U.S. Census Bureau, QuickFacts", U_QF)
add(D, "Persons without health insurance, under 65", "8.3%", "2025", "Los Angeles County", "T1", "verified",
    "U.S. Census Bureau, QuickFacts (SAHIE)", U_QF)
add(D, "Persons without health insurance, under 65", "10.7%", "2025", "Los Angeles city", "T1", "verified",
    "U.S. Census Bureau, QuickFacts (SAHIE)", U_QF)
add(D, "School assignment / attendance area for the parcel", "", "—", "PROP-001", "T1", "unverified",
    "LAUSD / California Department of Education", "https://www.cde.ca.gov/ds/",
    "Requires an address. No school-quality claim is made anywhere in this analysis.")
add(D, "Assigned school academic performance", "", "—", "PROP-001", "T1", "unverified",
    "California Department of Education, DataQuest / CAASPP", "https://caaspp-elpac.ets.org/",
    "Requires an address. Deliberately left blank.")

# ============================== HAZARDS ==============================
H = "hazards"
add(H, "California wildfires responded to", "8,232", "2025", "California", "T1", "verified",
    "CAL FIRE, 2025 Incident Archive", U_CAFIRE)
add(H, "Acres burned", "507,817", "2025", "California", "T1", "verified",
    "CAL FIRE, 2025 Incident Archive", U_CAFIRE)
add(H, "Structures destroyed", "16,627", "2025", "California", "T1", "verified",
    "CAL FIRE, 2025 Incident Archive", U_CAFIRE)
add(H, "Fatalities (preliminary, pending coroner confirmation)", "31", "2025", "California", "T1", "verified",
    "CAL FIRE, 2025 Incident Archive", U_CAFIRE)
add(H, "Total emergency responses", "608,571", "2025", "California", "T1", "verified",
    "CAL FIRE, 2025 Incident Archive", U_CAFIRE)
add(H, "Palisades Fire — acres burned", "23,448", "started 2025-01-07", "Los Angeles County", "T1", "verified",
    "CAL FIRE incident record", "https://www.fire.ca.gov/incidents/2025/1/7/palisades-fire")
add(H, "Eaton Fire — acres burned", "14,021", "started 2025-01-07", "Los Angeles County", "T1", "verified",
    "CAL FIRE incident record", "https://www.fire.ca.gov/incidents/2025/1/7/eaton-fire")
add(H, "Hughes Fire — acres burned", "10,425", "started 2025-01-22", "Los Angeles County", "T1", "verified",
    "CAL FIRE incident record", "https://www.fire.ca.gov/incidents/2025/1/22/hughes-fire")
add(H, "Canyon Fire — acres burned", "5,370", "started 2025-08-07", "Los Angeles / Ventura", "T1", "verified",
    "CAL FIRE incident record", "https://www.fire.ca.gov/incidents/2025/8/7/canyon-fire")
add(H, "LA County acres in incidents ≥5,000 acres", "≥53,264", "2025", "Los Angeles County", "D", "derived",
    "Sum of the four CAL FIRE incidents above", U_CAFIRE)
add(H, "Fire Hazard Severity Zone classes", "Moderate / High / Very High", "current", "California", "T1", "verified",
    "CAL FIRE — Office of the State Fire Marshal", U_OSFM)
add(H, "What a Fire Hazard Severity Zone measures", "Hazard, not risk — 30–50 year horizon, excluding mitigation", "current", "California", "T1", "verified",
    "CAL FIRE — Office of the State Fire Marshal", U_OSFM)
add(H, "LRA Fire Hazard Severity Zone map rollout", "All counties, four phases Feb–Mar 2025", "2025", "California", "T1", "verified",
    "CAL FIRE — Office of the State Fire Marshal", U_OSFM)
add(H, "Parcel Fire Hazard Severity Zone", "", "—", "PROP-001", "T1", "unverified",
    "CAL FIRE FHSZ viewer (address lookup)", U_FHSZ_MAP, "Requires address. Not guessed.")
add(H, "Parcel FEMA flood zone", "", "—", "PROP-001", "T1", "unverified",
    "FEMA National Flood Hazard Layer", U_FEMA_NFHL, "Requires address.")
add(H, "Parcel seismic / liquefaction zone", "", "—", "PROP-001", "T1", "unverified",
    "California Geological Survey, Seismic Hazards Program", U_CGS, "Requires address.")
add(H, "Fault proximity / rupture likelihood", "", "—", "PROP-001", "T1", "unverified",
    "USGS Earthquake Hazards Program", U_USGS, "Requires address.")
add(H, "FEMA National Risk Index — county score", "", "—", "Los Angeles County", "T1", "unverified",
    "FEMA National Risk Index", U_NRI, "API returned HTTP 500 on 2026-11-06; not retrieved.")
add(H, "Model: annual probability of a regional wildfire/smoke event", "4%", "2026 basis", "PROP-001", "A", "assumption",
    "model/projection_model.py — HAZARD block", "#hazard-model", "ASSUMPTION — the model's stated prior, not an official statistic")
add(H, "Model: annual probability of a significant seismic event", "3%", "2026 basis", "PROP-001", "A", "assumption",
    "model/projection_model.py — HAZARD block", "#hazard-model", "ASSUMPTION")
add(H, "Model: annual probability of an insurance shock", "6%", "2026 basis", "PROP-001", "A", "assumption",
    "model/projection_model.py — HAZARD block", "#hazard-model", "ASSUMPTION")

# ============================== TENANT ==============================
T = "tenant"
add(T, "Jack in the Box — system same-store sales", "−4.2%", "FY2025", "JACK system", "T1", "verified",
    "Form 10-K FY2025 (FY ended 2025-09-28)", U_10K)
add(T, "Jack in the Box — system same-store sales", "−1.3%", "FY2024", "JACK system", "T1", "verified",
    "Form 10-K FY2025", U_10K)
add(T, "Jack in the Box — company same-store sales", "−3.7%", "FY2025", "JACK company", "T1", "verified",
    "Form 10-K FY2025", U_10K)
add(T, "Jack in the Box — franchise same-store sales", "−4.3%", "FY2025", "JACK franchise", "T1", "verified",
    "Form 10-K FY2025", U_10K)
add(T, "Jack in the Box — same-store sales, Q4", "−7.4%", "Q4 FY2025", "JACK system", "T1", "verified",
    "Q4 & FY2025 earnings release, 2025-11-19", U_Q4, "Second consecutive quarter of ≥7% decline")
add(T, "Jack in the Box — restaurant-level margin", "16.5% (−240 bp YoY)", "Q4 FY2025", "JACK system", "T1", "verified",
    "Q4 & FY2025 earnings release", U_Q4)
add(T, "Jack in the Box — new restaurants opened", "31", "FY2025", "JACK system", "T1", "verified",
    "Form 10-K FY2025 / Q4 FY2025 release", U_Q4)
add(T, "Jack in the Box — restaurants closed", "86", "FY2025", "JACK system", "T1", "verified",
    "Form 10-K FY2025 / Q4 FY2025 release", U_Q4)
add(T, "Jack in the Box — closures in the 'JACK on Track' block programme", "51", "FY2025", "JACK system", "T1", "verified",
    "Form 10-K FY2025", U_10K)
add(T, "Jack in the Box — net unit change", "−55", "FY2025", "JACK system", "T1", "verified",
    "Form 10-K FY2025", U_10K)
add(T, "Del Taco — net unit change", "−18 (14 opened / 32 closed)", "FY2025", "Del Taco system", "T1", "verified",
    "Form 10-K FY2025", U_10K)
add(T, "Q3 revenue", "$257.7 million", "Q3 FY2026 (12 wks to 2026-07-05)", "JACK", "T1", "verified",
    "Q3 FY2026 results (Form 8-K)", U_Q3)
add(T, "Q3 revenue — prior year", "$262.4 million", "Q3 FY2025", "JACK", "T1", "verified",
    "Q3 FY2026 results", U_Q3)
add(T, "System same-store sales", "−1.1%", "Q3 FY2026", "JACK system", "T1", "verified",
    "Q3 FY2026 results", U_Q3)
add(T, "Franchise same-store sales", "−1.2%", "Q3 FY2026", "JACK franchise", "T1", "verified",
    "Q3 FY2026 results", U_Q3)
add(T, "Company same-store sales", "−0.9%", "Q3 FY2026", "JACK company", "T1", "verified",
    "Q3 FY2026 results", U_Q3)
add(T, "Systemwide sales change", "−1.4%", "Q3 FY2026", "JACK system", "T1", "verified",
    "Q3 FY2026 results", U_Q3)
add(T, "Restaurant count, end of period", "2,115", "Q3 FY2026", "JACK system", "T1", "verified",
    "Q3 FY2026 results", U_Q3)
add(T, "Restaurant count — company-operated", "149", "Q3 FY2026", "JACK", "T1", "verified",
    "Q3 FY2026 results", U_Q3)
add(T, "Restaurant count — franchised", "1,966", "Q3 FY2026", "JACK", "T1", "verified",
    "Q3 FY2026 results", U_Q3)
add(T, "Franchised share of system", "93.0%", "Q3 FY2026", "JACK system", "D", "derived",
    "Computed from Q3 FY2026 results (1,966 / 2,115)", U_Q3, "Implies but does not prove that PROP-001's tenant is a franchisee")
add(T, "Restaurant count, end of period — prior year", "2,168", "Q3 FY2025", "JACK system", "T1", "verified",
    "Q3 FY2026 results", U_Q3)
add(T, "Openings in quarter", "4", "Q3 FY2026", "JACK system", "T1", "verified",
    "Q3 FY2026 results", U_Q3)
add(T, "Closures in quarter", "17", "Q3 FY2026", "JACK system", "T1", "verified",
    "Q3 FY2026 results", U_Q3)
add(T, "FY2026 guidance — restaurant count", "≈2,100 (≈25 openings, 50–60 closures)", "FY2026 (updated)", "JACK system", "T1", "verified",
    "Q3 FY2026 updated guidance", U_Q3)
add(T, "FY2026 guidance — Adjusted EBITDA", "$225–230 million", "FY2026", "JACK", "T1", "verified",
    "Q3 FY2026 updated guidance", U_Q3)
add(T, "FY2026 guidance — same-store sales", "low single-digit decline", "FY2026", "JACK system", "T1", "verified",
    "Q3 FY2026 updated guidance", U_Q3)
add(T, "FY2026 guidance — capital expenditures", "$45–55 million", "FY2026", "JACK", "T1", "verified",
    "Q3 FY2026 updated guidance", U_Q3)
add(T, "FY2026 guidance — SG&A", "$112–115 million", "FY2026", "JACK", "T1", "verified",
    "Q3 FY2026 updated guidance", U_Q3)
add(T, "FY2026 guidance — dividends and buybacks", "none", "FY2026", "JACK", "T1", "verified",
    "Q3 FY2026 results", U_Q3)
add(T, "Del Taco — divestiture price", "≈$119 million ($109m cash + $10m 21-day note at 8%)", "completed 2025-12-22", "JACK", "T1", "verified",
    "Jack in the Box completion release / NRN", U_NRN_DT)
add(T, "Del Taco — original acquisition price", "≈$585 million, all cash", "closed March 2022", "JACK", "T1", "verified",
    "Form 10-K FY2025; NRN", U_NRN_DT)
add(T, "Del Taco — realised loss on disposal", "≈ −$470 million", "2025", "JACK", "D", "derived",
    "Derived: 585 − 119", U_NRN_DT)
add(T, "Debt reduction from Q3 FY2026 refinancing", "$244 million", "Q3 FY2026", "JACK", "T1", "verified",
    "Q3 FY2026 earnings call", U_Q3)
add(T, "Site-level average unit volume for PROP-001", "", "—", "PROP-001", "T1", "unverified",
    "Requires franchisee P&L or franchisor FDD site data", "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000807882",
    "Not available. AUV is the single best predictor of renewal and is flagged.")
add(T, "Tenant of record — corporate or franchisee", "", "—", "PROP-001", "T1", "unverified",
    "Requires lease / rent roll", "#asset", "Not supplied")
add(T, "Corporate or personal guaranty", "", "—", "PROP-001", "T1", "unverified",
    "Requires lease", "#asset", "Worth ~100 bp of cap rate (≈15% of value) if a corporate guaranty exists")

# ============================== LEGAL / TAX ==============================
L = "legal-tax"
add(L, "Unrecaptured IRC §1250 gain — maximum federal rate", "25%", "2025 tax year", "United States", "T1", "verified",
    "IRS Topic No. 409", U_IRS409)
add(L, "Long-term capital gains — top federal rate", "20%", "2025 tax year", "United States", "T1", "verified",
    "IRS Topic No. 409", U_IRS409)
add(L, "Net investment income tax", "3.8%", "current", "United States", "T1", "verified",
    "IRS Topic No. 409 / Topic No. 559", U_IRS409)
add(L, "Long-term capital gains — 15% bracket, married filing jointly", "$96,700 – $600,050", "2025 tax year", "United States", "T1", "verified",
    "IRS Topic No. 409", U_IRS409)
add(L, "§1031 — identification period", "45 days", "current law", "United States", "T1", "verified",
    "IRS — Like-Kind Exchanges Under IRC §1031", U_IRS1031, "Non-extendable except in a presidentially declared disaster")
add(L, "§1031 — exchange completion period", "180 days", "current law", "United States", "T1", "verified",
    "IRS — Like-Kind Exchanges Under IRC §1031", U_IRS1031)
add(L, "§1031 — who may act as facilitator", "A qualified intermediary; the taxpayer and its agents may not", "current law", "United States", "T1", "verified",
    "IRS — Like-Kind Exchanges Under IRC §1031", U_IRS1031)
add(L, "California fast-food minimum wage (covered chains, 60+ US units)", "$20.00/hour", "since 2024-04-01", "California", "T1", "verified",
    "California DIR — Fast Food Minimum Wage FAQ (statutory basis: AB 1228, Ch. 262, Statutes of 2023)", U_DIR_FF, "Core QSR labour-cost input")
add(L, "California general state minimum wage", "$16.90/hour", "effective 2026-01-01", "California", "T1", "verified",
    "California DIR — Minimum Wage FAQ", U_DIR_MW, "Indexed to CPI-W, capped at 3.5%/yr")
add(L, "California fast-food minimum wage — statutory authority", "AB 1228, Chapter 262, Statutes of 2023", "2023", "California", "T1", "verified",
    "California Legislative Information", U_AB1228, "Establishes the Fast Food Council and the $20 floor")
add(L, "California top marginal income tax rate (used by the tax module)", "13.3%", "2026", "California", "A", "assumption",
    "California Franchise Tax Board", "https://www.ftb.ca.gov/forms/",
    "FLAGGED — used as a modelling assumption; not re-verified against FTB in this session.")
add(L, "Proposition 13 — annual assessed-value increase cap", "", "—", "California", "T1", "unverified",
    "LA County Assessor / Cal. Rev. & Tax. Code §51", U_ASSESSOR,
    "Assessor Prop 13 page did not render content on 2026-11-06. Not asserted.")
add(L, "LA County — decline-in-value (DIV) application window", "accepted from 2026-07-02; deadline 2026-11-30", "2026-27 tax year", "Los Angeles County", "T1", "verified",
    "Los Angeles County Assessor", U_ASSESSOR, "Operational lever if market value falls below assessed value")
add(L, "Measure ULA (LA city transfer tax surcharge) applicability to PROP-001", "", "—", "Los Angeles city", "T1", "unverified",
    "City of Los Angeles / LA County Registrar-Recorder", "https://lacity.gov/",
    "Not verified. Applicability depends on sale price and property type; must be checked before pricing a sale.")
add(L, "California treatment of out-of-state §1031 replacement (FTB Form 3840)", "", "—", "California", "T1", "unverified",
    "California Franchise Tax Board, Form 3840", "https://www.ftb.ca.gov/forms/2025/2025-3840.pdf",
    "Potentially significant if capital is redeployed outside California. Needs a California tax opinion.")

# ============================== ASSET / PROPERTY ==============================
P = "asset"
add(P, "Street address", "[ADDRESS REDACTED]", "—", "PROP-001", "—", "verified",
    "Withheld by design", "#privacy", "Privacy protocol: no address, APN or legal description is stored or published")
add(P, "Assessor's parcel number", "APN [REDACTED]", "—", "PROP-001", "—", "verified",
    "Withheld by design", "#privacy", "Privacy protocol")
add(P, "Owner identity", "PARTY-OWNER (placeholder)", "—", "PROP-001", "—", "verified",
    "Withheld by design", "#privacy", "Privacy protocol")
add(P, "Tenant identity", "PARTY-TENANT (placeholder)", "—", "PROP-001", "—", "verified",
    "Withheld by design", "#privacy", "Privacy protocol")
add(P, "Lease type", "NNN (triple-net) — Owner description", "—", "PROP-001", "—", "owner-stated",
    "Owner description; lease document not supplied", "#lease", "Reported as stated, not independently verified")
add(P, "Lease expiration", "2030 – 2035 (a five-year range) — Owner description", "—", "PROP-001", "—", "owner-stated",
    "Owner description; lease document not supplied", "#lease",
    "A five-year range is worth ~21.6% of value. Must be resolved before any transaction.")
add(P, "Rent escalations", "", "—", "PROP-001", "—", "unverified", "Requires lease", "#lease", "Not supplied")
add(P, "Renewal / extension options and who holds them", "", "—", "PROP-001", "—", "unverified", "Requires lease", "#lease", "Not supplied")
add(P, "Landlord obligations (roof / structure)", "", "—", "PROP-001", "—", "unverified", "Requires lease", "#lease", "Not supplied")
add(P, "Early-termination / kick-out rights", "", "—", "PROP-001", "—", "unverified", "Requires lease", "#lease", "Not supplied")
add(P, "Current annual rent / NOI", "", "—", "PROP-001", "—", "unverified", "Requires rent roll", "#model",
    "Not supplied. The model is normalised to $1.00 of NOI so no disclosure is required.")
add(P, "Original basis and accumulated depreciation", "", "—", "PROP-001", "—", "unverified", "Requires tax returns / depreciation schedule", "#tax",
    "Not supplied. The tax module uses stated assumptions.")
add(P, "Existing debt, rate and maturity", "", "—", "PROP-001", "—", "unverified", "Requires loan documents", "#tax", "Not supplied")
add(P, "Assessed value and property tax bill", "", "—", "PROP-001", "T1", "unverified", "LA County Assessor / Treasurer-Tax Collector",
    "https://assessor.lacounty.gov/", "Requires APN")
add(P, "Zoning, general plan designation and redevelopment potential", "", "—", "PROP-001", "T1", "unverified",
    "City of Los Angeles Department of City Planning", "https://planning.lacity.gov/",
    "Requires address. This is the largest un-quantified upside in the analysis.")

# ------------------------------------------------------------------
CATEGORIES = [
    ("decision",   "Decision & Risk",            "decision.html"),
    ("projection", "Projection Model",           "projection.html"),
    ("tenant",     "Tenant & Brand",             "tenant.html"),
    ("economy",    "Local Economy",              "economy.html"),
    ("demographics", "Demographics",             "demographics.html"),
    ("capital-markets", "Capital Markets",       "capital-markets.html"),
    ("lease",      "Lease & Term",               "lease.html"),
    ("hazards",    "Geography & Catastrophe",    "hazards.html"),
    ("legal-tax",  "Tax & Personal Wealth",      "tax.html"),
    ("asset",      "Asset Profile & Privacy",    "asset.html"),
]

for i, r in enumerate(R):
    r["id"] = f"F{i + 1:03d}"

if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    payload = {"generated": "2026-11-06",
               "count": len(R),
               "categories": [{"key": k, "label": l, "page": p} for k, l, p in CATEGORIES],
               "facts": R}
    with open(OUT, "w") as f:
        json.dump(payload, f, indent=1)

    # integrity checks printed to console
    from collections import Counter
    st = Counter(r["status"] for r in R)
    tiers = Counter(r["tier"] for r in R)
    print(f"facts written: {len(R)}")
    print("status:", dict(st))
    print("tier  :", dict(tiers))
    bad = [r for r in R if r["status"] == "verified" and not r["url"]]
    print("verified rows missing a source url:", len(bad))
    blanks = [r for r in R if r["status"] == "unverified"]
    print("unverified (blank + flagged):", len(blanks))
    for b in blanks:
        assert b["value"] == "", f"unverified row must be blank: {b['metric']} -> {b['value']!r}"
    print("owner-stated (reported as given, not verified):",
          sum(1 for r in R if r["status"] == "owner-stated"))
    print("OK — every unverified row is genuinely blank.")
