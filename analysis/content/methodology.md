# Methodology & verification

## The standard this project holds itself to

Every quantitative claim on this site is one of five things, and the type is printed next to it:

| Status | Meaning |
|---|---|
| **Verified** | The number was read directly from an official publisher's page or filing, and the link is given. |
| **Derived** | Arithmetic performed on verified numbers. The formula is in the row note. |
| **Reported** | The number comes from an official body but was read through secondary coverage, because the primary page could not be retrieved. Shown with a warning and listed on the Flagged page. |
| **Input** | A fact stated by the owner that has no public record. Never counted as verified. |
| **Unverified** | Could not be confirmed. The value is left blank. Not estimated, not interpolated, not filled from a third-party site. |

Two structural controls enforce this:

1. **The build fails** if any row carries a value but no source, or is marked unverified while carrying a value. `build.py` refuses to publish an inconsistent dataset.
2. **The flagged page is generated**, not hand-written. It is the mechanical output of every row whose status is not `verified` or `derived`. Nothing can quietly disappear from it.

## What counts as an official source

Only U.S. federal agencies, State of California agencies and courts of record, County of Los Angeles departments, City of Los Angeles departments, and SEC/EDGAR filings. A real-estate portal, a trade publication, a brokerage research note or a school-rating site is **not** an official source, no matter how reliable it usually is. Where a trade publication was the only available window onto an official number, the row is marked `reported` and the caveat is printed.

## What was retrieved, and what was not

Retrieved and read directly:

- BLS Economy at a Glance for the LA–Long Beach–Anaheim MSA, and the September 2026 CPI news release.
- Census QuickFacts for the City and County of Los Angeles (V2025 population estimates and 2020–2024 ACS).
- U.S. Treasury daily par yield curve for November 2026, and the Federal Reserve's open-market-operations rate history.
- Jack in the Box FY2025 Form 10-K, the Q4 FY2025 earnings exhibit, and the Q3 FY2026 earnings exhibit, all from EDGAR.
- IRS Publication 946 and Topic 409; IRC §1031 guidance.
- Revenue and Taxation Code §§51 and 93 via the California Legislative Information site.
- City of Los Angeles Office of Finance Measure ULA FAQ.
- CAL FIRE's 2025 incident archive and FEMA's DR-4856-CA declaration page.
- USGS National Seismic Hazard Model; Metro's D Line project page.

Attempted and **not** retrieved, hence flagged rather than filled:

- California DIR minimum-wage pages (404s) — no wage rate is asserted.
- California Department of Education district profile (404) — no school metric is asserted.
- LA County Assessor Proposition 13 page (returned generic homepage content) — the statutory rule is cited from the Revenue and Taxation Code instead.
- LAHSA's own 2026 count report — the count is marked `reported` from press coverage.
- California Department of Finance projections — published only as spreadsheets; no projector number asserted.

## The model

`model/projection.py` is a 20,000-path Monte Carlo with seed 20261106, run three times for the three expiry years. It is deterministic: re-running it produces the same file. The full assumption table — with ranges and stated bases — is rendered on the Projection page from `data/projection.json`, so the assumptions cannot drift away from the results.

Modelling choices worth challenging:

- **NOI normalisation.** Nothing is expressed in dollars, because rent is private. Results are per $1.00 of NOI.
- **Reinvestment at 4.84%.** Interim cash flows compound at the 10-year Treasury, applied identically to every strategy.
- **Strategy B redeploys into the same diversified position as A.** Without this, B would be penalised for holding cash, which would be an artefact rather than a finding.
- **Tax is not in the model.** Adjusted basis was not supplied, so a post-tax comparison would require inventing one. Tax is handled as a documented overlay on the Decision page.
- **Black-swan probabilities are judgements.** 1.5%/yr for a damaging earthquake and 3.0%/yr for a regional disruption are stated assumptions, not USGS output. The USGS source supports the *hazard class*, not the frequency used.

## Privacy controls

- The owner is `OWNER-01`; the property is `PARCEL-01`. No address, APN, coordinate, rent, basis, or financial statement is stored anywhere in this repository, including in git history.
- No figure was reverse-engineered from an address, a parcel record or a personal document.
- Only public, aggregate, official data was collected. Nothing came from a paid or private source.
- The site is safe to publish: the recommendation can be read without identifying who it is about, or where exactly the asset is.

## Known irregularities

A running list, also published on the Flagged page and in `COORDINATION.md`:

- The property's identity is withheld by design, so no parcel-level figure in this project can be verified.
- The lease expiry is a window, not a date, and it is owner-stated.
- No official publisher issues single-tenant QSR cap rates or rents; the model's cap-rate band is an assumption.
- Several 2026 federal series have gaps (for example, October 2025 CPI is missing because of the appropriations lapse). Gaps are shown as gaps and never interpolated.
- The branch-naming convention in the task brief conflicts with this session's pinned branch; the work was therefore consolidated onto `arena/ffe3bdfd-jack2`, documented in `COORDINATION.md`.
