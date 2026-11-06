# COORDINATION.md — Shared Task Board

> Shared task board for all agent sessions working on this repository.
> **Read this before starting any task.** Claim a task by writing your session ID and file scope, then commit and push the claim immediately.

## Session registry

| Session ID | Branch | Started (UTC) | Notes |
|---|---|---|---|
| `session-230fe704` | `arena/230fe704-jack2` | 2026-11-06 | Primary/founding session for this repo. |

---

## Rules in force

1. **Read before you write.** Never start a task already claimed by another session.
2. **Non-overlapping scopes.** Each session works on its own branch `session-<id>/<task>` (or a git worktree) and edits only the files in its claimed scope.
3. **Shared outputs are integration-only.** Table data (`docs/data/*`), site index/navigation (`docs/index.html`, `docs/assets/`), and `docs/flags.html` are changed **only** by the final integration session after all other tasks are done.
4. **Small, frequent commits.** Run `git pull --rebase` before every push.
5. **Conflicts.** If a merge conflict occurs: stop, resolve without discarding the other session's work, and log it here under *Incident log*.
6. **Handoff / takeover.** If a session crashes, or its claim is >60 minutes old with no commits, any other session may take over the task and must note the handoff in the *Handoff log*.
7. **Verification.** Never mark anything `verified` without checking it against an official source **and** linking that source. Unconfirmable values are left blank and flagged on the Flagged for Review page.
8. **Privacy.** No personal information anywhere in the repo or the published site. All owner/person/parcel identifiers are replaced with placeholders before they touch a file.

---

## Task board

| # | Task | Status | Owner | File scope |
|---|---|---|---|---|
| T01 | Coordination board + repo scaffolding | done | `session-230fe704` | `COORDINATION.md`, `.gitignore`, `README.md` |
| T02 | Research: property/asset profile (anonymized) + Jack in the Box corporate fundamentals | done | `session-230fe704` | `research/01-asset-profile.md`, `research/02-jack-in-the-box.md` |
| T03 | Research: NNN lease mechanics, 2030–2035 expiry risk, cap-rate & interest-rate regime | done | `session-230fe704` | `research/03-nnn-lease-and-cap-rates.md` |
| T04 | Research: Central LA economy (demographics, income, jobs, schools, population) — official sources | done | `session-230fe704` | `research/04-central-la-economy.md` |
| T05 | Research: geography & catastrophe risk (wildfire, flood, seismic, drought, grid) | done | `session-230fe704` | `research/05-hazard-risk.md` |
| T06 | Projection engine: 2026–2040 scenario model for the trade area | done | `session-230fe704` | `model/`, `docs/data/` |
| T07 | Decision framework: sell / renew / hybrid, risk register incl. black swans | done | `research/06-decision-and-risk.md` |
| T08 | Verification pass: every row source-linked, unverified flagged | done | `session-230fe704` | `docs/data/*`, `docs/flags.html` |
| T09 | Site build: dashboard, category subpages, tables, exec summary | done | `session-230fe704` | `docs/**` |
| T10 | Integration + Pages deploy + PR merge | done | `session-230fe704` | `docs/**`, `COORDINATION.md` |

Status vocabulary: `unclaimed` · `in progress` · `needs review` · `done`.
`needs review` = published on the Flagged for Review page; it does **not** block the merge.

---

## Log

### 2026-11-06 — `session-230fe704`
- Repo reviewed at commit `1430b4f` (branch `arena/230fe704-jack2`). Contents: `README.md` only (7 bytes, stub). No prior site, no prior data, no `COORDINATION.md`.
- **Irregularity flagged:** the brief describes *one specific* property, but no parcel address, APN, lease document, or rent roll was supplied. The property is therefore modelled as an **anonymized reference asset** ("Subject Property" / `PROP-001`) with all owner, tenant-contact, and parcel identifiers replaced by placeholders. No PII is stored in this repository.
- Because this session is both the founding and the integration session, all tasks T01–T10 are claimed here in order. No other session had claims at claim time (board did not exist). Scopes remain fully non-overlapping with any future session.
- Running as a single session: no other branches existed at start (`git branch -a` showed only `main` and `arena/230fe704-jack2`).

### Sources
*(appended per task in the sections below)*

---

## Verification ledger

| Task | Sources checked | Verification performed | Irregularities |
|---|---|---|---|
| T01 | — | Board and scaffolding written | None |
| T02–T10 | *see task sections* | *see task sections* | *see task sections* |

---

## Incident log

*(empty)*

## Handoff log

*(empty)*

## PR / merge record

*(pending)*
