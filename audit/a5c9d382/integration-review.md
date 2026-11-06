# Independent evidence and integration review

**Session:** a5c9d382. **Review date:** 2026-11-06 (UTC). This is a handoff for the final integration session, not an assertion that another session's work has been reviewed. The fixed Arena branch policy prevents creating the requested `session-…` branch. This report contains no property address, personal identifier, or private financial data.

## Release and coordination findings

- At inspection, default `main` pointed to `1430b4f` and contained only a heading in `README.md`. No PR existed. Pages was configured to deploy `/` on `main`; an old successful Pages workflow run does not prove that a new site has been deployed.
- Several active `arena/…` branches had separate copies of `COORDINATION.md` with overlapping claims. Some boards stated that research, integration, PR, merge, and deployment were complete, while their actual branch trees contained only the board and the initial README, and GitHub had no PRs. Future-dated activity on one board was also present. These statements were **not verified**. Do not treat them as proof of completion or take over current claims.
- A branch-local file cannot act as an atomic shared lock. Integrator: fetch and inspect all remote session branches, reconcile claims, coordinate owners, and record the real commits and any conflicts. Do not blindly merge unrelated competing versions of shared files or invent a handoff. Re-check PR and Pages status using GitHub immediately before and after release.

## Independently checked primary-source excerpts

Values below were read directly from each issuing source. They are public regional or system-wide observations, **not** facts about the unidentified subject parcel. Each line has its source; dates and geographic scope are part of the claim.

| Subject | Verified observation | Source and scope warning |
|---|---|---|
| Population | City of Los Angeles population estimate on July 1, 2025: 3,869,089; change since April 1, 2020 estimate base: −0.8%. | [U.S. Census Bureau QuickFacts](https://www.census.gov/quickfacts/fact/table/losangelescitycalifornia/INC110223). Citywide, not a trade area. |
| Income | Median household income: $81,939 in 2024 dollars, 2020–2024. | [U.S. Census Bureau QuickFacts](https://www.census.gov/quickfacts/fact/table/losangelescitycalifornia/INC110223). Citywide five-year ACS estimate, not current neighborhood or customer income. |
| Labor | City unemployment rate was 5.0% in August 2026; metro unemployment was 4.8%. | [BLS Los Angeles Area Economic Summary, updated October 5, 2026](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf). Not seasonally adjusted; subject to revision; city and metro differ. |
| Job growth | Metro total nonfarm employment rose 0.6% over the year to August 2026. | [BLS economic summary](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf). Metro-wide payroll data, not the parcel's trade area. |
| Inflation | Metro CPI-U all items rose 3.6% over the year to August 2026. | [BLS economic summary](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf). Metro inflation is not a property-specific rent escalator or forecast. |
| Tenant system risk | In the 12 weeks ended July 5, 2026, Jack in the Box system same-store sales declined 1.1% year-over-year; four restaurants opened and 17 closed. | [Company Q3 2026 earnings release](https://investors.jackinthebox.com/news/news-details/2026/Jack-in-the-Box-Inc--Reports-Third-Quarter-2026-Earnings/default.aspx). Issuer reporting, system-wide; no evidence this particular location is closing or that corporate entity guarantees the lease. |
| Historic tenant system risk | FY 2025 system same-store sales declined 4.2%; 31 restaurants opened and 86 closed. | [SEC-filed company earnings release](https://www.sec.gov/Archives/edgar/data/807882/000080788225000070/ex991-q425earningsrelease.htm). Do not present 2025 as the latest available operating data. |
| City transfer tax | For closings after June 30, 2026, the City lists ULA thresholds of $5,400,000 and $10,900,000; ULA 4% applies above the lower threshold and below the upper, 5.5% at or above the upper. Base tax is separately applicable, calculated per $500 or fractional part. | [Los Angeles Office of Finance FAQ](https://finance.lacity.gov/faq/measure-ula). Applies to qualifying city conveyances with potential exemptions; location, price, and exemption for the subject are unverified. Thresholds adjust annually, not a forecast for 2030–2035. |
| Deferred exchange timing | Replacement property identification generally within 45 days; receipt by the earlier of 180 days or the tax return due date including extensions. | [IRS Form 8824 instructions](https://www.irs.gov/instructions/i8824). Eligibility, tax consequences, and disaster relief depend on individual circumstances; no claim that this property qualifies. |
| Earthquake and flood | Official site-specific tools exist, but parcel classifications have not been determined. | [USGS fault and hazard maps](https://www.usgs.gov/faqs/how-do-i-find-fault-or-hazard-maps-california), [USGS flood map guidance](https://www.usgs.gov/faqs/where-can-i-find-flood-maps). They are tools, not verification of this parcel. |
| Schools | State dashboard provides school and district information. No subject school, district, score or boundary is established. | [California School Dashboard](https://www.caschooldashboard.org/). Do not imply school performance predicts the subject store's profitability. |

## Required flagged items for final site

- The property is described by the request only. Its actual lease, legal tenant, guarantor, exact expiry date, renewal options and notification windows, rental income, reimbursements, taxes, insurance, building condition, debt, basis, ownership goals and market value have **not** been independently confirmed. Do not treat 2030–2035 as a verified expiration, infer an exact location, or publish sensitive facts.
- The applicable city jurisdiction, specific hazards, flood and wildfire zones, school district, local market and trade-area statistics are unknown. Keep fields empty and mark unverified; link to the official lookup as a research path, not as evidence of a parcel-specific value.
- A valid individual sell-versus-renew recommendation requires private lease and tax records, actual executable bids, and owner objectives. Without them, a conditional decision framework and a diligence checklist are defensible; a definitive personalized answer, current cap rate, projected return, or quantified black-swan probability is not.
- NNN is not evidence that a landlord has zero costs or that the lease renews automatically. Actual obligations, tenant rights and credit support must come from the executed contract. City averages and chain-wide metrics are not forecasts of restaurant demand.
- If a scenario engine is built, unknown inputs should suppress outputs rather than silently use plausible defaults. Hypothetical illustrative values must never be labeled verified, nor published in a field that purports to report subject-property facts. Include explicit formulas, valuation date, time periods, cash-flow timing, discounting, sale costs, tax treatment, debt and reinvestment assumptions, and sensitivity/low-liquidity and hazard loss scenarios. Without verified inputs, a reliable calibrated projection is unavailable.
- A personal risk tolerance or tax position cannot be deduced from the prompt. This analysis is informational, not a substitute for individualized legal, tax, insurance, or investment advice.

## Minimum integration tests

1. Re-read every published data row against the exact official source, geography, period, units, footnotes, date of access, and status. A link to a map or general documentation alone cannot verify a parcel-specific value.
2. Audit all generated assets and the repository history to avoid exposing private personal information; public source pages may themselves contain names or contacts, so link rather than copy those details.
3. Build from a clean checkout, test every internal route/anchor and asset under `/Jack2/`, validate source links separately, and verify accessible mobile/table navigation.
4. Inspect actual PR, checks, merge result, Pages build, and the deployed public content. An existing historical success or settings response is not a successful deployment of this change. Record actual evidence, not anticipated success.
