# Repository and decision-readiness review

**Review date:** 2026-11-12 (UTC)  
**Scope:** current `main` baseline (`99c6519`, PR #45 merge) and the root decision/model/data artifacts relevant to the sell-versus-renew recommendation. This is an additive independent review; prior workbooks remain untouched.  
**Personal data:** none collected or published. The exact property location and all private owner/tenant data remain withheld.

## Root repository checks

Ran on the unchanged root site before producing this workspace:

- `python3 tools/model.py` — passed; model outputs regenerated deterministically.
- `python3 tools/build_site.py` — passed; rebuilt the 16 generated root pages.
- `python3 tools/check_site.py` — passed: 16 root pages; 208 pages including archives; 24 source records; 89 metric rows (82 marked verified, 7 blank/flagged); 24 risk rows.
- `git diff --check` — passed after this workspace was created; no root generated files changed.

Those automated checks establish structural/link/data consistency under the repository's own rules. They do **not** independently certify every historical narrative claim or make unknown site facts known.

## Decision-critical root-file audit

| Artifact inspected | Concrete finding | Decision consequence / review action | Official reference |
|---|---|---|---|
| `data/valuation.json`, assumption `A1` | The model's `$150,000/year` base rent is explicitly a proxy set to 8% of Jack in the Box FY2025 average unit volume, not the subject lease rent; it is marked low-confidence/unverified in the input file. | Price estimates and comparisons using this input are illustrative only; substitute executed lease rent and reconciled property NOI before considering outputs. | [SEC FY2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm) — issuer-level data is not the subject's rent. |
| `tools/model.py`, expiry setup / `data/valuation.json`, `A3` | The script assigns 2032 as the midpoint of the reported 2030–2035 window. | The actual date and option rights are material. Replace midpoint with exact lease dates and separately model each enforceable option/notice deadline. | [SEC FY2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm) — does not replace the private executed lease. |
| `tools/model.py`, `SCENARIOS`; `data/valuation.json`, `A2`, `A5`, `A7`–`A9` | Scenario escalation, exit cap rates, renewal probability, rent reset, downtime and leasing cost are analyst assumptions; no subject comparables or tenant-specific likelihood evidence are provided. The model's algebra uses base rent divided by assumed cap rate for price. | Do not present resulting dollar outputs, rank scores, cap-rate cutoffs or probability-weighted wealth as a property appraisal, forecast, or measured likelihood. Obtain independent appraisal and primary tenant/lease/property evidence; publish ranges and sensitivities. | [SEC FY2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/807882/000080788225000072/jack-20250928.htm) — company disclosures have narrower scope. |
| `data/valuation.json`, `netlease_yield`; root executive summary | A public REIT acquisition yield is used as a comparison/reinvestment benchmark. It is not evidence of the yield available to this owner on a specific replacement asset or of the subject cap rate. | Obtain actual replacement opportunities and compare fees, debt, taxes, location, asset, tenant, liquidity and risk on a like-for-like basis. | [IRS Instructions for Form 8824](https://www.irs.gov/pub/irs-pdf/i8824.pdf) — exchange reporting framework, not investment yield assurance. |
| `data/property_lease.json`; site description | The repository has placeholders rather than exact parcel and private lease inputs. “Central Los Angeles” does not establish a city limit, census tract, school district, zoning, or hazard overlay. | No site-level geography, school, income, hazard, insurance, or market value finding can be assigned until the owner/adviser privately geocodes the property. | [Census ACS API](https://www.census.gov/programs-surveys/acs/data/data-via-api.html); [ZIMAS](https://zimas.lacity.org/); [CAL FIRE/OSFM FHSZ](https://osfm.fire.ca.gov/what-we-do/community-wildfire-preparedness-and-mitigation/fire-hazard-severity-zones). |
| `data/valuation.json`, transfer tax inputs; root model | City and county transfer taxes are modeled using Los Angeles City-specific assumptions, while the actual municipality is not verified. Official county guidance lists different city-specific rates; official LA City guidance states its thresholds/rates apply to property conveyed within City jurisdiction and change over time. | Do not use the modeled cost stack until location, transaction date/value and current law are verified with closing counsel. | [LA County Recorder DTT](https://www.lavote.gov/home/recorder/property-document-recording/documentary-transfer-taxes/general-info); [LA City ULA FAQ](https://finance.lacity.gov/faq/measure-ula). |
| `data/risks.json` meta; root decision workbook | Root risk likelihood/impact scores are explicitly analyst judgments rather than observed probabilities. | Keep these labeled as judgments; do not cite a score as a statistical chance of default, wildfire, earthquake, or loss. | [CAL FIRE/OSFM FHSZ](https://osfm.fire.ca.gov/what-we-do/community-wildfire-preparedness-and-mitigation/fire-hazard-severity-zones) distinguishes hazard from risk. |

## Official public context independently checked for this workspace

- BLS Los Angeles Area Economic Summary (updated November 4, 2026): metro unemployment **4.4%** in September 2026; nonfarm employment **+0.5%** year over year; CPI-U all items **+3.7%** over 12 months. These are broad-area observations, not parcel demand or a 2030–2035 forecast. [Official BLS PDF](https://www.bls.gov/regions/west/summary/blssummary_losangeles.pdf)
- BEA county release: Los Angeles County 2024 total personal income **$818.5 billion**. This is a nominal county aggregate, not local household income or purchasing power near the site. County 2025 estimates were scheduled for December 2, 2026, so this release remains the 2024 county reference available on the audit date. [Official BEA release](https://www.bea.gov/news/2026/gross-domestic-product-county-and-personal-income-county-2024)
- Census Bureau ACS documentation confirms 2024 ACS 5-year data includes geographies down to block group; use its uncertainty/margins and private geocoding after the location is verified. [ACS API docs](https://www.census.gov/programs-surveys/acs/data/data-via-api.html) · [2024 dataset reference](https://api.census.gov/data/2024/acs/acs5.html)
- The CAL FIRE/OSFM page explains that FHSZ mapping characterizes hazard, not total risk, and links current map processes/data. A zone cannot be assigned here because no parcel location is available. [Official OSFM page](https://osfm.fire.ca.gov/what-we-do/community-wildfire-preparedness-and-mitigation/fire-hazard-severity-zones)

## Irregularities for review

1. Prior model precision is input-sensitive: rent is a brand-average-derived placeholder; expiry is a midpoint; several financial and risk parameters are judgment. See `flagged.html`.
2. Regional/county economic indicators are often presented next to property scenarios, but they cannot substitute for actual trade-area, tenant, lease or parcel data.
3. City-level transfer tax or zoning assumptions are unsafe until jurisdiction is known; the City of LA must not be inferred from “Central LA.”
4. Probability-weighted projection labels can imply empirical probabilities even where renewal likelihood is an analyst input.
5. A useful numeric recommendation is not responsibly computable from the supplied facts. The interim recommendation is to preserve legal options and run private parallel diligence; it is not a final investment directive.

## Workspace verification

`python3 session-5f15df5c/scripts/build.py` generated nine responsive dashboard pages. `python3 session-5f15df5c/scripts/verify.py` passed: 14 official-source URLs; 20 decision questions; six sourced context metrics; 15 risk items; all table rows have official hyperlinks; internal links resolve; privacy scan clear. The check verifies structure/traceability, not the truth of unknown property facts.
