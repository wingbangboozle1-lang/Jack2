# COORDINATION.md — Shared Task Board

Branch policy note: this session is pinned to `arena/1944e5a3-jack2` by the Arena
environment (work on any other branch is not tracked). Per the task brief we would
otherwise branch `session-<id>/<task>`; here the single session works on
`arena/1944e5a3-jack2` and that branch doubles as the integration branch for the
pull request to `main`.

Session ID: `arena-1944e5a3`

## Task board

| # | Task | Status | Owner | Files / scope |
|---|------|--------|-------|----------------|
| 1 | Create/claim COORDINATION.md task board | done | arena-1944e5a3 | COORDINATION.md |
| 2 | Repo review (line-by-line) + flag irregularities | done | arena-1944e5a3 | README.md, repo config; findings on site `flagged.html` |
| 3 | Research: property/market/demographics/economy/risk (official sources) | done | arena-1944e5a3 | site data files under `site/assets/data/` |
| 4 | Build GitHub Pages site (landing + subpages, tables, sources) | done | arena-1944e5a3 | `site/**` |
| 5 | Verification pass (every row sourced or flagged) | done | arena-1944e5a3 | `site/sources.html`, `site/flagged.html` |
| 6 | Final integration: merge to main via PR, enable Pages deploy, verify live | done | arena-1944e5a3 | repo settings / PR |

## Rules (from task brief)

- Work only in claimed scope; small frequent commits; `git pull --rebase` before push.
- Every table row carries an official source link; unverifiable values are left blank
  and listed on the Flagged for Review page.
- Personal information is anonymized; no personal information appears on the site.
- "Needs review" = published on Flagged for Review; does not block merge.

## Handoff log

- 2026-11-06: Session arena-1944e5a3 started. Repo contained only a one-line README.md
  ("# Jack2") and no COORDINATION.md; board created. No other sessions detected.
- 2026-11-06: Research + site build completed; verification pass done; PR opened to main
  and merged; GitHub Pages enabled and verified live. See "Sources & verification" below.

## Sources & verification

(See site/sources.html for the full table with links. Summary: U.S. Census Bureau
QuickFacts/ACS, BLS Economy at a Glance & LAUS, CA EDD/LAEDC, LAUSD, City of Los
Angeles / LA County, CAL FIRE, FEMA, USGS, SEC EDGAR (Jack in the Box Inc.),
City of Los Angeles Planning Department. All cited inline on the site.)

## Flagged irregularities / unverified items

(All published on site/flagged.html — see that page for the review list.)
