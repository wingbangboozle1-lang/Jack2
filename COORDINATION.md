# Coordination Board

Shared task board for parallel agent sessions. Read this file before starting work.

## Session Registry

| Session ID | Branch / worktree | Scope | Status |
|---|---|---|---|
| `arena-742b6a03` | `arena/742b6a03-jack2` (session branch), integration merged to `main` | Sole active session. All scopes below. | active |

**Note (arena-742b6a03, 2026-11-06):** Repository was empty (single "Initial commit" README) when this
session started. No other session has claimed any task, no other branches exist except `main`. This session
therefore claims every task below and performs the final integration itself (integration role is explicitly
permitted to be taken by the remaining session once all other tasks are done; here it is the only session).

## Task Board

| # | Task | Status | Owner | Files touched |
|---|---|---|---|---|
| 1 | Repo + privacy baseline (coordination board, anonymization policy, README) | in progress | arena-742b6a03 | `COORDINATION.md`, `README.md`, `PRIVACY.md` |
| 2 | Official-source research ledger (every claim → official URL, access date) | in progress | arena-742b6a03 | `research/*.md`, `data/sources.json` |
| 3 | Requirement list (full extraction of user requirements → verifiable items) | unclaimed | — | `data/requirements.json` |
| 4 | Property & lease facts (anonymized, no PII) | unclaimed | — | `data/property_lease.json` |
| 5 | Market economics dataset (population, income, jobs, schools, retail spend) | unclaimed | — | `data/market_economics.json` |
| 6 | Valuation inputs (cap rates, rates, taxes, transfer costs) | unclaimed | — | `data/valuation.json` |
| 7 | Risk register (business-as-usual + black swan) | unclaimed | — | `data/risks.json` |
| 8 | Projection model + scenario engine (deterministic, reproducible) | unclaimed | — | `tools/model.py`, `data/model_output.json` |
| 9 | Decision analysis (sell vs renew vs hybrid) | unclaimed | — | `data/decisions.json` |
| 10 | Executive summary | unclaimed | — | `docs/…executive-summary` |
| 11 | Static site build (dashboard + category pages) | unclaimed | — | `tools/build_site.py`, `assets/*`, root `*.html` |
| 12 | Link/verification checks + CI | unclaimed | — | `tools/check_site.py`, `.github/workflows/*` |
| 13 | Integration: merge, re-verify, publish to GitHub Pages | unclaimed | — | `main`, Pages settings |
| 14 | PR to `main` + merge + deploy verification | unclaimed | — | `COORDINATION.md` |

## Change Requests (cross-scope)

None.

## Log

- 2026-11-06 — `arena-742b6a03` claimed tasks 1–14 (empty repo; no competing claims). Scopes are
  non-overlapping because all files are created fresh by this session. No shared file is owned by another
  session, so no edit requests are needed.

