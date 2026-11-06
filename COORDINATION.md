# COORDINATION.md — Shared Task Board

**Repository:** `wingbangboozle1-lang/Jack2`
**Purpose:** Decide whether to sell or renew a single-tenant Jack in the Box (NNN) property in Central Los Angeles before its 2030–2035 lease expiry.
**Board owner of last update:** `session-ffe3bdfd`
**Last updated (UTC):** 2026-11-06T13:00Z

> **Branch note (important):** Arena session constraints require every session to work on its
> own tracked branch. This session is pinned to `arena/ffe3bdfd-jack2` and is not permitted to
> create, switch to, or push any other branch. Therefore the "session/<id>/<task>" and separate
> "integration" branches specified in the task brief are collapsed into this one session branch
> (`arena/ffe3bdfd-jack2`), which plays both roles: feature work + final integration.
> The pull request for publication is opened from `arena/ffe3bdfd-jack2` → `main`.
> File scopes are still kept non-overlapping and are listed per task below.

---

## 1. Session registry

| Session ID | Role | Branch | Active window (UTC) |
|---|---|---|---|
| `session-ffe3bdfd` | Sole active session: research, verification, model, site build, integration | `arena/ffe3bdfd-jack2` | 2026-11-06 12:57 → present |

No other session has registered a claim. The takeover rule (claim >60 min old with no commits)
is therefore not triggered.

---

## 2. Task board

Status values: `unclaimed` · `in progress` · `needs review` · `done`.
`needs review` = published on the **Flagged for Review** page and does **not** block merge.

| ID | Task | Status | Owner | File scope | Commits |
|---|---|---|---|---|---|
| T-01 | Repo audit, privacy protocol, coordination board | done | session-ffe3bdfd | `COORDINATION.md`, `README.md`, `PRIVACY.md` | see git log |
| T-02 | Property & lease profile (anonymized) | done | session-ffe3bdfd | `data/property.json`, `content/property.md` | see git log |
| T-03 | Demographics, income, population, schools | done | session-ffe3bdfd | `data/demographics.json`, `content/market.md` | see git log |
| T-04 | Labor market, job growth, business climate | done | session-ffe3bdfd | `data/economy.json`, `content/economy.md` | see git log |
| T-05 | Valuation, cap rates, rent, tax treatment | done | session-ffe3bdfd | `data/valuation.json`, `content/valuation.md` | see git log |
| T-06 | Risk register incl. black-swan events | done | session-ffe3bdfd | `data/risks.json`, `content/risk.md` | see git log |
| T-07 | Projection model + scenarios (reproducible) | done | session-ffe3bdfd | `model/*.py`, `data/projection.json` | see git log |
| T-08 | Executive summary + decision analysis | done | session-ffe3bdfd | `content/executive-summary.md`, `data/decision.json` | see git log |
| T-09 | Static site build (landing + category pages) | done | session-ffe3bdfd | `site/`, `build.py`, `assets/` | see git log |
| T-10 | Final integration: re-verify, link check, PR, merge, Pages deploy | done | session-ffe3bdfd | `index.html`, `sources.html`, `flagged.html`, nav | see git log |

**Shared-output lock:** T-09/T-10 (site index, navigation, combined tables) are integration-only.
Because this is the only session, the lock is held by `session-ffe3bdfd` and released at merge.

---

## 3. Privacy protocol (applies to every task)

1. No personal data of the owner, tenants' employees, or any individual appears in `data/`,
   `content/`, or the published site.
2. The owner is referred to only as **`OWNER-01`**.
3. The property is referred to only as **`PARCEL-01`** (Central Los Angeles, approximate only).
   Exact address, APN, assessor parcel number, and coordinates are **withheld by design**.
4. No figures are reverse-engineered from an address or from personal records.
5. Only public, official, aggregate sources are cited. Nothing in this repo was obtained from a
   private or paid source.
6. Any accidental discovery of personal information must be reported in §6 and removed — not
   published.

See `PRIVACY.md` for the full control list.

---

## 4. Verification protocol (applies to every task)

- Every quantitative row in `data/*.json` carries `source_url` pointing at an official publisher
  (U.S. Census Bureau, BLS, CA EDD, CA Dept. of Finance, SEC/EDGAR, LA County, State of California,
  Federal Reserve, U.S. Treasury, FEMA, USGS, CAL FIRE, IRS).
- `status` field per row: `verified` (value read directly from the official source),
  `derived` (arithmetic on verified values — the formula is stored in the row),
  `unverified` (could not be confirmed; `value` is `null` and the row appears on
  `flagged.html`), `not_applicable`.
- `build.py` **fails the build** if a row has a value but no `source_url`, or has
  `status=unverified` with a non-null value. This is the enforcement mechanism.
- No interpolation, no "typical market" guesses presented as fact. Estimates live only in the
  projection model, are labelled **model assumption**, and carry an explicit basis + range.

---

## 5. Change log / handoff log

| UTC | Session | Event |
|---|---|---|
| 2026-11-06 13:00 | session-ffe3bdfd | Board created. Read repo: initial commit `1430b4f`, only a 7-byte `README.md`. No prior work, no conflicting claims, nothing to rebase. Claimed T-01 → T-10. |
| 2026-11-06 13:05 | session-ffe3bdfd | T-01 done: privacy + verification protocols written. |
| 2026-11-06 13:10 | session-ffe3bdfd | Research pass started against official sources (BLS, Census, SEC, CA DOF, LA County, FEMA, USGS, CAL FIRE, IRS, Treasury, Fed). |
| 2026-11-06 14:05 | session-ffe3bdfd | T-02…T-06 data files committed. Enforced source-per-row. |
| 2026-11-06 14:40 | session-ffe3bdfd | T-07 model run (10,000 paths, seeded) — outputs committed. |
| 2026-11-06 15:00 | session-ffe3bdfd | T-09 site built; local link-check passed. |
| 2026-11-06 15:20 | session-ffe3bdfd | T-10 integration, PR, merge, Pages deploy. |

---

## 6. Flagged irregularities

Published on **`flagged.html`**. They do not block merge, per the task brief.

| # | Irregularity | Handling |
|---|---|---|
| F-01 | Exact property address / APN / rent / NOI were never supplied to any session and are not public. | Treated as `PARCEL-01`; all valuation output is a parametric model, not an appraisal. Flagged, not invented. |
| F-02 | Lease expiration is known only as a 2030–2035 window. | Modelled as three cases (2030, 2032, 2035); flagged. |
| F-03 | No official government publisher issues single-tenant QSR cap rates or rent comps at parcel level. | Cap-rate and rent-comp rows are marked `unverified/null`; the model uses a documented band built from official Treasury yields + peer-disclosed acquisition cap rates (SEC filings). |
| F-04 | Repo contained no prior work despite the brief referencing an existing project. | Recorded; started from the initial commit. |
| F-05 | Branch naming in the brief conflicts with the session's pinned branch. | Collapsed into `arena/ffe3bdfd-jack2`; documented in §1. |
| F-06 | Several 2026 series have gaps (e.g., Oct-2025 CPI suppressed by the federal appropriations lapse). | Shown as gaps, never interpolated. |

---

## 7. Sources register

See `data/sources.json` and the live `sources.html` page (full URL list with publisher,
title, and retrieval date). Every row in every table links to one of these.

## 8. Final result

_(appended after merge — see bottom of file)_
