# COORDINATION.md — Shared Task Board

This file is the shared task board for all agent sessions working in this repository.
Protocol: read this before starting; claim a task by writing your session ID and file
scope; commit and push the claim immediately; never start a task another session has
claimed; keep scopes non-overlapping; make small, frequent commits; run
`git pull --rebase` before every push; record sources, verification performed, and
irregularities here when a task is done.

Statuses: `unclaimed` | `in progress` | `done` | `needs review`
("needs review" = published on the site's "Flagged for Review" page; does not block anything).

## Session registry

| Session ID | Branch | Role | Notes |
|---|---|---|---|
| arena-b4ec6128-jack2 | arena/b4ec6128-jack2 | Research + build + integration | PLATFORM CONSTRAINT: this environment binds the session to a single branch `arena/b4ec6128-jack2` and forbids creating or pushing to other branches. All tasks below are executed on this one branch with small, frequent commits (equivalent isolation to per-task branches). This session also acts as the final integration session because no other sessions are active. Deviation logged in "Irregularities & deviations" below. |

## Task board

| # | Task | Status | Owner | Files touched | Notes / log |
|---|---|---|---|---|---|
| T1 | Repo review + coordination setup | done | arena-b4ec6128-jack2 | COORDINATION.md, README.md | Repo initially contained README.md only ("# Jack2"). No prior sessions, no claims, no conflicts. |
| T2 | Research: demographics & housing (US Census ACS/PEP, HUD) | done | arena-b4ec6128-jack2 | research/02-demographics.md | Verified via Census QuickFacts (API key required — used HTML page). ZIP-level income -> IRS SOI flagged (file download). |
| T3 | Research: economy & labor (BLS, CA EDD, CA DIR) | done | arena-b4ec6128-jack2 | research/03-economy.md | BLS EAG + CPI release (Sept 2026, 26-1595-SAN) + CA DIR pages verified 2026-11-06. |
| T4 | Research: education (CA Dept of Education, CA Dashboard) | done | arena-b4ec6128-jack2 | research/04-education.md | CDE Directory + CA School Dashboard 2024 verified. |
| T5 | Research: hazards & insurance (FEMA, USGS, CAL FIRE, CDI, LADBS) | done | arena-b4ec6128-jack2 | research/05-hazards.md | USGS UCERF3 (60/46/31% 30-yr), CAL FIRE Palisades/Eaton incident pages, CDI Bulletin 2025-4, LADBS retrofit, FEMA NRI/MSC manual-review links. Parcel-level items flagged. |
| T6 | Research: tenant financials (SEC EDGAR — Jack in the Box Inc.) | done | arena-b4ec6128-jack2 | research/06-tenant.md | CIK 0000807882 FY2025 10-K (accession 0000807882-25-000072) + 8-K EX-99.1 Del Taco completion (12/22/2025) verified. |
| T7 | Research: tax/regulatory & growth forecasts (IRS, FTB, BOE, SCAG, CA DOF, LA City Planning) | done | arena-b4ec6128-jack2 | research/07-tax-forecasts.md | IRS + FTB + BOE Pub 800-10 verified; SCAG Connect SoCal 2024 PEIR App. I interval tables verified; DOF xlsx flagged manual review. |
| T8 | Analysis: decision framework, risk matrix, projection system | done | arena-b4ec6128-jack2 | research/08-analysis.md, site decision page | research/08-analysis.md + site decision.html: options, risk matrix, transparent projection system (CPI-banded scenarios, cap-rate sensitivity), deadlines, triggers, recommendation. |
| T9 | Executive summary | done | arena-b4ec6128-jack2 | site executive-summary page | executive-summary.html: situation, verified facts, recommendation, risk-by-decision table, privacy statement. |
| T10 | Site creation (GitHub Pages static site) | done | arena-b4ec6128-jack2 | index.html, *.html, assets/style.css | 11 pages: index, executive-summary, property, market, education, hazards, tenant, decision, data (master tables), flagged, sources; assets/style.css; .nojekyll. |
| T11 | Verification: line-by-line source audit + link check | done | arena-b4ec6128-jack2 | scripts/verify.py, site pages | scripts/verify.py: internal-link check + per-row source-link audit (391 rows incl. headers) + privacy pattern scan. ALL CHECKS PASSED 2026-11-06. Cap-rate bands and escalation scenarios labeled as assumptions on site + flagged page. |
| T12 | Integration: PR to main, merge, GitHub Pages deploy, final record | in progress | arena-b4ec6128-jack2 | COORDINATION.md, GitHub settings | PR/merge/deploy in progress this session; results recorded below when complete. |

## Irregularities & deviations

- **Platform branch constraint (logged 2026-11-06, session arena-b4ec6128-jack2):** The
  execution environment fixes this session to branch `arena/b4ec6128-jack2` and forbids
  creating/pushing other branches, so the per-task `session-<id>/<task>` branch scheme
  cannot be used. Mitigation: single branch + small frequent commits + immediate push of
  claims. No other sessions were active when work began (repo contained only README.md),
  so no conflict risk was introduced.
- **Property identity withheld (privacy):** No street address, parcel number, or
  ownership details were supplied, and personal information must be anonymized. All
  property-specific inputs therefore use placeholders (e.g., `[PROPERTY ADDRESS]`) and
  are flagged unverified rather than invented. Area-level analysis uses official public
  data for Central Los Angeles.

## Handoff / takeover log

(empty — no takeovers)
