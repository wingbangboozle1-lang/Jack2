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
| T2 | Research: demographics & housing (US Census ACS/PEP, HUD) | in progress | arena-b4ec6128-jack2 | research/02-demographics.md | Central LA area (ZCTAs), LA city/county |
| T3 | Research: economy & labor (BLS, CA EDD, CA DIR) | in progress | arena-b4ec6128-jack2 | research/03-economy.md | LA metro employment, CPI, minimum wage, fast-food wage |
| T4 | Research: education (CA Dept of Education, CA Dashboard) | in progress | arena-b4ec6128-jack2 | research/04-education.md | LAUSD + area schools |
| T5 | Research: hazards & insurance (FEMA, USGS, CAL FIRE, CDI, LADBS) | in progress | arena-b4ec6128-jack2 | research/05-hazards.md | Earthquake, wildfire, flood; Jan 2025 fire events; insurance market |
| T6 | Research: tenant financials (SEC EDGAR — Jack in the Box Inc.) | in progress | arena-b4ec6128-jack2 | research/06-tenant.md | 10-K data, JACK on Track closures, Del Taco divestiture |
| T7 | Research: tax/regulatory & growth forecasts (IRS, FTB, BOE, SCAG, CA DOF, LA City Planning) | in progress | arena-b4ec6128-jack2 | research/07-tax-forecasts.md | 1031, Prop 13, capital gains, SCAG/DOF projections |
| T8 | Analysis: decision framework, risk matrix, projection system | in progress | arena-b4ec6128-jack2 | research/08-analysis.md, site decision page | Sell vs renew vs hold; black swan scenarios |
| T9 | Executive summary | in progress | arena-b4ec6128-jack2 | site executive-summary page | |
| T10 | Site creation (GitHub Pages static site) | in progress | arena-b4ec6128-jack2 | index.html, *.html, assets/style.css | Static HTML/CSS dashboard, no build step |
| T11 | Verification: line-by-line source audit + link check | in progress | arena-b4ec6128-jack2 | scripts/check_links.py, site pages | Every table row must link an official source or be flagged unverified |
| T12 | Integration: PR to main, merge, GitHub Pages deploy, final record | in progress | arena-b4ec6128-jack2 | COORDINATION.md, GitHub settings | Confirm deploy; record PR link + merge result here |

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
