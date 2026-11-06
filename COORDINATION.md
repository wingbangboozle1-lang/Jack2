# COORDINATION.md — Shared Task Board

> **Purpose.** Multiple agent sessions may work on this repository concurrently.
> This file is the single source of truth for who is doing what. Read it before
> starting work. Claim before you build.

**Last updated:** 2026-11-06 (UTC) by `arena-8149683c`

---

## 0. Session registry

| Session ID | Branch | Role | Status |
|---|---|---|---|
| `arena-8149683c` | `arena/8149683c-jack2` | **Integration session** — research, data, site build, verification, PR + merge | active |

> The repository name (`Jack2`) and the session branch both encode `Jack`/`jack2`;
> this is the only session working in this checkout. If a second session appears,
> append a row above, claim disjoint file scopes, and never edit a file owned by
> another row.

---

## 1. Rules of engagement

1. **Read this file first.** Claim a task by writing your session ID + file scope
   below, then `git commit` + `git push` the claim *immediately* — before doing any
   work, so no other session can start the same task.
2. **Never start a task another session has claimed.** A claim is live unless it is
   >60 minutes old with zero commits, in which case any session may take over and
   must note the handoff in §5 (Handoff log).
3. **Keep scopes non-overlapping.** Each session edits only the files listed in its
   claim. Branch naming: `session-<id>/<task>` (this session works on the
   Arena-managed branch `arena/8149683c-jack2`, which is equivalent).
4. **Shared outputs** — `data/*.json`, `site/index.html`, `site/assets/nav.js`, and
   anything under `site/` — are written **only** by the integration session, after
   all research tasks are done.
5. **Small, frequent commits.** `git pull --rebase` before every push.
6. **Merge conflicts:** stop, resolve without discarding the other session's work,
   and log the resolution in §5.
7. **Never mark anything verified** without checking it against an official source,
   and record that source URL in `data/sources.json`.
8. **Personal information:** no personal data of any person (owner, tenant
   principals, franchisees, employees, neighbours) may enter the repo, the data
   files, or the published site. Use placeholders. See `PRIVACY.md`.

---

## 2. Task board

Status vocabulary: `unclaimed` · `in progress` · `done` · `needs review`

| ID | Task | Owner | Status | File scope |
|---|---|---|---|---|
| T00 | Repo review + irregularity audit | `arena-8149683c` | in progress | `REPO_REVIEW.md`, `COORDINATION.md` |
| T01 | Source register + pruning of unverifiable claims | `arena-8149683c` | in progress | `data/sources.json`, `research/` |
| T02 | Tenant & asset-class research (SEC EDGAR primary) | `arena-8149683c` | in progress | `research/01-tenant-asset-class.md` |
| T03 | Macro & regional economy (LA County) | `arena-8149683c` | in progress | `research/02-macro-economy.md` |
| T04 | Demographics, income, population, education | `arena-8149683c` | in progress | `research/03-demographics.md` |
| T05 | Employment & job growth | `arena-8149683c` | in progress | `research/04-employment.md` |
| T06 | Geography, hazards, climate, insurance | `arena-8149683c` | in progress | `research/05-risk-hazards.md` |
| T07 | Net-lease valuation, cap rates, financing, tax | `arena-8149683c` | in progress | `research/06-valuation-financing.md` |
| T08 | Projection model + scenario / Monte Carlo engine | `arena-8149683c` | in progress | `model/`, `data/model_output.json` |
| T09 | Decision analysis: sell vs. renew vs. hold | `arena-8149683c` | in progress | `research/07-decision-analysis.md` |
| T10 | Site build (dashboard + category subpages) | `arena-8149683c` | in progress | `site/`, `assets/` |
| T11 | Line-by-line verification pass + link crawl | `arena-8149683c` | unclaimed → see §4 | `verification/` |
| T12 | PR to `main`, merge, Pages deploy verification | `arena-8149683c` | unclaimed → see §4 | `COORDINATION.md` |

> **Note.** Because Arena runs this checkout as a single session on a fixed branch,
> all rows are held by `arena-8149683c`. That session is *also* the designated
> integration session, so it performs §4. If the platform ever starts a second
> session, it must take rows from `unclaimed` only.

---

## 3. Shared-output lock

`data/*.json`, `site/**`, `index.html` are **integration-only**. Other sessions must
log a change request in §5 instead of editing.

---

## 4. Integration sequence (this session)

1. Research + data collection → `data/sources.json`, `research/*.md`
2. Model → `model/project_model.py`, `data/model_output.json`
3. Build site → `site/` (relative links only; must work on GitHub Pages project path)
4. Verification → `verification/LINK_CHECK.md`, `verification/ROW_AUDIT.md`
5. PR branch → `main`, merge, confirm Pages deploy

---

## 5. Log

### 2026-11-06 — `arena-8149683c`

- Read repo: **empty except `README.md` (7 bytes, no trailing newline, content `# Jack2`)**.
  No `COORDINATION.md` existed; created it. No other sessions detected.
- GitHub Pages is already enabled on `main` / root, `https://wingbangboozle1-lang.github.io/Jack2/`.
  Confirmed via GitHub API (`status: built`, `https://enforced: true`). Legacy build type.
- Claimed T00–T10 above and pushed the claim.

### Handoff log

_(empty — no handoffs)_

### Change requests from non-integration sessions

_(none)_
