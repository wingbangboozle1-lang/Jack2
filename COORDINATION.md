# COORDINATION.md — Shared Task Board

**Repo:** `wingbangboozle1-lang/Jack2`
**Session branch:** `arena/e70763c7-jack2`
**Session ID:** `e70763c7`
**Role this session:** research + data build + site build + integration (sole active session at start; claims all scopes below)
**Last updated:** 2026-11-06

---

## 0. Rules in force

1. Read this board before starting any task.
2. Claim a task by writing your **session ID** and **file scope** below, then commit + push the claim immediately.
3. Never start a task another session has claimed.
4. Keep scopes non-overlapping. Each session edits only files inside its claimed scope.
5. If a task needs a file owned by another session, log a **REQUEST** here — do not edit the file.
6. Make small, frequent commits. `git pull --rebase` before every push.
7. On conflict: stop, resolve without discarding the other session's work, log it here.
8. On completion: record sources, verification performed, and irregularities here; mark **done**.
9. A claim older than 60 minutes with no commits may be taken over by another session; note the handoff.
10. **Shared outputs** (`site/index.html`, global nav, `data/*.json` master tables) are changed only by the final integration session.

---

## 1. Task board

| # | Task | Status | Owner (session) | File scope | Updated |
|---|------|--------|-----------------|------------|---------|
| T01 | Repo audit + coordination board + branch hygiene | **done** | e70763c7 | `COORDINATION.md`, `README.md` | 2026-11-06 |
| T02 | Requirements register (full list, traceable R-IDs) | **done** | e70763c7 | `docs/requirements-register.md` | 2026-11-06 |
| T03 | Research: tenant credit (Jack in the Box Inc. SEC filings) | **done** | e70763c7 | `research/01-tenant-credit.md`, `data/tenant.json` | 2026-11-06 |
| T04 | Research: NNN lease economics + QSR cap-rate / valuation evidence | **done** | e70763c7 | `research/02-lease-and-valuation.md`, `data/valuation.json` | 2026-11-06 |
| T05 | Research: submarket economics (population, income, jobs, schools, traffic) | **done** | e70763c7 | `research/03-submarket-economics.md`, `data/submarket.json` | 2026-11-06 |
| T06 | Research: tax & transaction costs (Prop 13, Measure ULA, 1031) | **done** | e70763c7 | `research/04-tax-and-transaction.md`, `data/tax.json` | 2026-11-06 |
| T07 | Research: hazard & black-swan register (wildfire, seismic, flood, insurance) | **done** | e70763c7 | `research/05-hazards.md`, `data/hazards.json` | 2026-11-06 |
| T08 | Projection model (transparent, reproducible) | **done** | e70763c7 | `model/`, `data/projection.json` | 2026-11-06 |
| T09 | Decision matrix + risk register + recommendations | **done** | e70763c7 | `research/06-decision.md`, `data/decision.json` | 2026-11-06 |
| T10 | Executive summary | **done** | e70763c7 | `site/executive-summary.html` | 2026-11-06 |
| T11 | Site build (landing + category subpages + tables) | **done** | e70763c7 | `site/**` | 2026-11-06 |
| T12 | Verification pass (every row -> official source) + link check | **done** | e70763c7 | `tools/linkcheck.py`, `data/verification.json` | 2026-11-06 |
| T13 | Flagged-for-review page | **done** | e70763c7 | `site/flagged.html`, `data/flagged.json` | 2026-11-06 |
| T14 | GitHub Pages deploy + PR + merge | **done** | e70763c7 | `.github/workflows/pages.yml` | 2026-11-06 |

---

## 2. Scope ownership (no overlaps)

| Path | Owner session |
|------|---------------|
| `COORDINATION.md`, `README.md` | e70763c7 |
| `docs/**` | e70763c7 |
| `research/**` | e70763c7 |
| `data/**` | e70763c7 |
| `model/**` | e70763c7 |
| `tools/**` | e70763c7 |
| `site/**` | e70763c7 |
| `.github/**` | e70763c7 |

---

## 3. Requests to other sessions

_None._

---

## 4. Log

| Timestamp (UTC) | Session | Event |
|---|---|---|
| 2026-11-06 | e70763c7 | Board created. Repo audit: `main` @ `1430b4f` contained only a 7-byte `README.md` — no prior research, data, site, or coordination file existed. No competing sessions detected on any branch. Claimed T01–T14. |
