# COORDINATION.md — Shared Task Board & Verification Ledger

**Repository:** `wingbangboozle1-lang/Jack2`  
**Active Session ID:** `session-a3a8ec08`  
**Assigned Session Branch:** `arena/a3a8ec08-jack2`  
**Base Commit (`main`):** `1430b4f04885e701ba4de07756105ff31122ee06`  
**Last Updated (UTC):** `2026-11-06`

---

## 1. Branch & Coordination Protocol Note

1. **Fixed Arena Branch Constraint:** This agent session is bound by platform policy to the fixed branch `arena/a3a8ec08-jack2` (creating, renaming, switching to, or pushing to `session-<id>/<task>` branches is disallowed by the Arena execution environment). Accordingly, all scoped tasks and final integration work for `session-a3a8ec08` are executed cleanly in non-overlapping file scopes on `arena/a3a8ec08-jack2` and integrated to `main` via Pull Request.
2. **Initial Repository Inspection (`main` @ `1430b4f`):** At session start, `main` contained solely `README.md` (`# Jack2`, 1 line, 7 bytes) and no `COORDINATION.md` on `main`. Separate isolated `arena/*` branches exist on the remote repository; none had merged to `main` at inspection time. Before every push and prior to PR integration, `origin/main` and `origin/arena/a3a8ec08-jack2` are checked so any upstream changes are preserved and logged without discarding work.
3. **Strict Privacy Rule (Highest Priority):** Zero personal information (PII), owner names, street addresses, Assessor Parcel Numbers (APNs), lease signatory identities, or private financial account identifiers may appear anywhere in data files, markdown docs, scripts, or website pages. Placeholders (`[REDACTED-OWNER-01]`, `[REDACTED-PROPERTY-01]`, `[REDACTED-PARCEL-ID]`) are enforced across the repository and audited automatically.
4. **Strict Verification Rule:** Every table row on the live website must link directly to a verified official source (`.gov`, `sec.gov`, `.ca.gov`, `lacounty.gov`, `lacity.gov`, `lausd.org`, `federalreserve.gov`, `usgs.gov`, `fema.gov`, etc.). Any metric that cannot be confirmed from an official source must have its value cell left **blank** (`""`) and be explicitly flagged on the **Flagged for Review** (`flagged.html`) page.

---

## 2. Shared Task Board

Allowed statuses: `unclaimed` | `in progress` | `done` | `needs review`  
*(Note: `needs review` denotes items published on the `Flagged for Review` page and does not block merge.)*

| Task ID | Task Description | Status | Owning Session ID | Claimed File Scope | Verification & Notes |
|---|---|---|---|---|---|
| `T-01` | Initial repository line-by-line review, privacy guardrails, & coordination setup | `in progress` | `session-a3a8ec08` | `COORDINATION.md`, `PRIVACY_POLICY.md` | Inspect `1430b4f` (`README.md`); log repo irregularities for `flagged.html`. |
| `T-02` | Official-source research: Tenant Corporate Credit (`JACK` SEC 10-K/10-Q) & NNN Lease Structure | `in progress` | `session-a3a8ec08` | `data/tenant_lease.json` | Verify all figures directly from SEC EDGAR (`CIK 0000807882`) and CA DIR AB 1228 official releases. |
| `T-03` | Official-source research: Geography, Demographics, Income, Population & Schools (Central LA / LA County) | `in progress` | `session-a3a8ec08` | `data/demographics_schools.json` | Verify via U.S. Census Bureau QuickFacts/ACS, CA Dept. of Finance, CDE / NCES / LAUSD official reports. |
| `T-04` | Official-source research: Local Economy, Labor Market, Inflation, Rates & Tax/Transfer Rules | `in progress` | `session-a3a8ec08` | `data/economy_tax.json` | Verify via BLS, BEA, CA EDD, Federal Reserve / Treasury, IRS (§1031), CA FTB, LA County Assessor (Prop 13), LA Office of Finance (Measure ULA). |
| `T-05` | Official-source research: BAU Risk Register & Black Swan Disasters (Wildfire, Seismic, Flood, Systemic) | `in progress` | `session-a3a8ec08` | `data/risks_blackswan.json` | Verify via FEMA National Risk Index, USGS (UCERF3 / NSHM), CAL FIRE (FHSZ & 2025 LA Fires), CA Dept. of Insurance, NOAA. |
| `T-06` | Quantitative Area & Decision Projection Engine (2026–2036 BAU + Black Swan Monte Carlo & Scenarios) | `in progress` | `session-a3a8ec08` | `scripts/projection_engine.py`, `data/projections_decisions.json` | Reproducible Python projection model anchored to official series; clearly separate official verified anchors from parametric lease inputs. |
| `T-07` | Executive Summary & Unverified / Irregularities Register | `in progress` | `session-a3a8ec08` | `EXECUTIVE_SUMMARY.md`, `data/flagged_items.json` | Comprehensive wealth-preservation & growth synthesis; line-by-line register of unverified parcel-specific fields & repo irregularities. |
| `T-08` | Static Dashboard Site Generator & Subpages (GitHub Pages Ready) | `unclaimed` | `session-a3a8ec08` (reserved for integration) | `scripts/build_site.py`, `assets/*`, `index.html`, `executive-summary.html`, `property-tenant.html`, `demographics-schools.html`, `economy-jobs.html`, `projections-decisions.html`, `risks-black-swans.html`, `sources.html`, `flagged.html`, `.nojekyll` | Reserved for final integration once `T-01`–`T-07` data verification completes. |
| `T-09` | Final Integration: Line-by-Line Audit, PII Scan, Link Check, PR, Merge & GitHub Pages Live Check | `unclaimed` | `session-a3a8ec08` (reserved for integration) | `scripts/verify_all.py`, `README.md`, `COORDINATION.md` | Automated verification of every `<tr>`, source URL, blank unverified value, PII absence, link integrity, PR merge, and live Pages deployment. |

---

## 3. Coordination & Activity Log

- **`2026-11-06` (`session-a3a8ec08`):** Inspected repository root at `1430b4f`. Confirmed only `README.md` (`# Jack2`) existed on `main` and no prior `COORDINATION.md` was present on `main`. Created `COORDINATION.md` and claimed research/model scopes `T-01` through `T-07` (reserving shared site output scopes `T-08` and `T-09` for final integration). Pushing initial claim immediately.
