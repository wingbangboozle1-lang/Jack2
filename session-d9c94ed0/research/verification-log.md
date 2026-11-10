# Session M verification log — 2026-11-10

Independent re-verification of the root workbook (89 metric rows, 24 sources) against official sources. Method: live web search + official-site reads on 2026-11-10; values compared to `data/metrics.json` (accessed 2026-11-08). No value was changed by this session; discrepancies are flagged, not silently corrected.

## Confirmed unchanged

| Check | Official source | Result |
|---|---|---|
| BLS LA Area Economic Summary dated Nov 04, 2026; metro nonfarm 6,282.1k, +30.2k (+0.5%); Info −11.4k (−5.7%); Ed/health +49.1k (+3.8%) | S1 bls.gov | Confirmed |
| Census QuickFacts city median HH income $81,939; county $90,112 (2020–2024 ACS) | S2 census.gov | Confirmed |
| CA DOF P-2A direction: county mild decline 2025→2040 | S3 dof.ca.gov | Confirmed (vintage note F-M2) |
| CA statewide min wage $16.90 (Jan 1, 2026); fast food $20.00 | S4/S5 dir.ca.gov | Confirmed |
| Prop 13: 1% levy cap, 2% annual cap, reassessment on sale | S6 assessor.lacounty.gov | Confirmed |
| County DTT 0.11%, city DTT 0.45% | S7 lavote.gov | Confirmed |
| Measure ULA $5.4M / $10.9M thresholds (post–June 30, 2026), 4% / 5.5% | S8 finance.lacity.gov | Confirmed |
| JACK Q3 FY2026: system SSS −1.1% quarter, −4.2% YTD | S9 sec.gov EDGAR | Confirmed |
| Realty Income 7.3% initial weighted avg cash yield (FY2025, Q2 2026) | S10 realtyincome.com | Confirmed (Q3 6.8% flagged F-M1) |
| 10Y Treasury ~4.86% (Nov 6) / ~4.90% (Nov 4); 30Y ~5.26% | S11 fred.stlouisfed.org | Confirmed |
| USGS UCERF3 LA 30-yr: 60% M6.7+, 46% M7.0+, 31% M7.5+ | S18 usgs.gov FAQ | Confirmed (specific FAQ record) |
| Eaton 14,021 ac / 9,414 destroyed / 1,074 damaged; Palisades 23,448 ac / 6,837 destroyed | S13 file.lacounty.gov | Confirmed |
| EDD LA County Sep 2026: SA 4.8% (BLS NSA 4.5% — both correct, different adjustment); +20,300 jobs YoY (+0.4%) | EDD via S1 context | Confirmed; SA/NSA distinction already noted in workbook |

## Flagged (see flagged.html)

- F-M1: Q3 2026 Realty Income 6.8% print (reported by Session L) not independently re-read; this session uses verified 7.3%.
- F-M2: DOF vintage sensitivity (LAEDC-cited 9.3M by 2040 vs Vintage 2026 9.64M).
- F-M3: EWDD AP25 forecast horizon ends before 2030–2035 window.
- F-M4–F-M6: Owner facts, parcel hazards/insurance, and M46/M51/M87 remain blank.

## Privacy audit

Repository-wide scan of published HTML + data JSON for emails, phone numbers, APNs: **0 hits** (2026-11-10). No owner, tenant, address, APN, loan or account identifiers in this session's output. Unknowns stay blank.
