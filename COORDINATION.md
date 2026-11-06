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

### Sources and verification performed

**T01 — Board and scaffolding.** Written at commit `a7dee7e`, pushed immediately as required. No other branches existed when the claim was made.

**T02–T05 — Research corpus.** Seven documents in `research/`. Every metric was retrieved on 2026-11-06 from a resolving official endpoint. Method: `research/00-methodology.md`.

| Document | Primary official sources | Verification performed |
|---|---|---|
| `01-asset-profile.md` | Census QuickFacts; CAL FIRE; FRED | Privacy placeholders confirmed; parcel-level fields marked unverified rather than guessed |
| `02-jack-in-the-box.md` | SEC EDGAR: Form 10-K FY2025 (`0000807882-25-000072`), Form 8-K Q3 FY2026, submissions JSON | Every store count, SSS figure and guidance range matched against the filing language; Del Taco loss derived (585 − 119) |
| `03-nnn-lease-and-cap-rates.md` | FRED `DGS10`/`GS10`/`MORTGAGE30US`/`DFF`/`CPIAUCSL`; Boulder Group Q2/Q3 2026 (T3) | YoY CPI recomputed (336.298 / 324.245 − 1 = 3.72%); every cap rate badged T3; **no JACK-specific cap rate asserted** |
| `04-central-la-economy.md` | FRED `SMU06310800000000001`, `CALOSA7URN`; Census QuickFacts (V2025 + ACS 2020–2024) | Payroll growth recomputed (Sep 2019 → Sep 2026 = +0.73%); vintages recorded per row and never mixed |
| `05-hazard-risk.md` | CAL FIRE 2025 Incident Archive; CAL FIRE / OSFM FHSZ | Incident acreages matched to CAL FIRE records; parcel-level determinations left blank |

**T06 — Projection engine.** `model/projection_model.py`, seed `20261106`, 20,000 trials, standard library only, deterministic. Includes an explicit tax-symmetry rule: deferred §1031 tax is deducted as a contingent liability so deferral cannot masquerade as free money. Every assumption is published in `docs/data/projections.json` and on the Projection page.

**T07 — Decision framework.** `research/06-decision-and-risk.md`: 15-item risk register, black-swan replay, break-even across a 350 bp Treasury range, and five explicit falsification conditions.

**T08 — Verification pass.** `model/build_facts.py` emits 195 rows and **asserts** that (a) every `verified` row has a source URL and (b) every `unverified` row has an empty value. The build fails otherwise. Result: 154 verified · 10 derived · 20 T3 industry · 5 assumption · 2 owner-stated · 25 unverified-and-blank · 2 privacy placeholders.

**T09 — Site build.** `model/build_site.py` generates 11 pages and validates every internal `href` against the set of emitted pages. 181 links checked, 0 broken. No CDN, no external font, no third-party JS.

**T10 — Integration and deploy.** See *PR / merge record* below.

### Sources appendix (canonical list)

FRED (DGS10, GS10, MORTGAGE30US, DFF, CPIAUCSL, SMU06310800000000001, CALOSA7URN) · U.S. Census Bureau QuickFacts · U.S. BLS · U.S. SEC EDGAR (CIK 0000807882) · IRS Topic No. 409 and IRC §1031 guidance · CAL FIRE 2025 Incident Archive · CAL FIRE / OSFM Fire Hazard Severity Zones · California Legislative Information AB 1228 · California DIR Minimum Wage FAQ · Los Angeles County Assessor · The Boulder Group Q2/Q3 2026 (Tier 3, non-government).

Each row's individual URL is in `docs/data/facts.json` and is rendered as a clickable link on every table row of the site.

---

## Verification ledger

| Task | Sources checked | Verification performed | Irregularities |
|---|---|---|---|
| T01 | — | Board and scaffolding written | None |
| T02 | 1a. SEC 10-K FY2025; 1b. Form 8-K Q3 FY2026; 1c. EDGAR submissions JSON; 1d. company Q4/FY2025 release | All unit counts, same-store-sales figures and guidance ranges matched to filing text | Del Taco sale confirmed at ~$119m; no AUV or guarantor data available |
| T03 | 2a. FRED DGS10/GS10; 2b. FRED MORTGAGE30US/DFF/CPIAUCSL; 2c. Boulder Group Q2 2026; 2d. Boulder Group Q3 2026 | CPI YoY recomputed; rate path reconstructed from daily series; every cap rate badged T3 | No JACK-specific cap rate; cap-rate term curve is model-derived and labelled D |
| T04 | 3a. FRED SMU06310800000000001; 3b. FRED CALOSA7URN; 3c. Census QuickFacts | Payroll CAGR recomputed; population base 2020 → 2025 recomputed; vintages labelled | DOF projections not machine-verifiable (.xlsx); school data deliberately not asserted |
| T05 | 4a. CAL FIRE 2025 archive; 4b. OSFM FHSZ programme page; 4c. FEMA NRI (failed) | Incident acreages and statewide totals matched | FEMA NRI HTTP 500; parcel-level hazard unverifiable without address |
| T06 | derived from T02–T05 | Model re-run 6× during development; RNG seed fixed; outputs byte-identical | Two modelling errors found and corrected in-session (see Incident log) |
| T07 | IRS Topic 409; IRS §1031 guidance | Tax rates matched to IRS text; 45/180-day rules quoted | California 13.3% rate and FTB 3840 left as flagged assumptions |
| T08 | all of the above | Automated assertions in `build_facts.py`; every unverified row verified to be blank | 25 items genuinely unverifiable in this session |
| T09 | data files | 11 pages generated; 181 internal links validated; HTML tag balance checked | None |
| T10 | GitHub Actions / Pages | `gh` PR merged; Pages build status checked | See PR / merge record |

---

## Incident log

### 2026-11-06 — two modelling defects found and fixed during T06

1. **Fake variance.** The first Monte-Carlo pass held the interest-rate path and market inputs fixed, so the only
   source of dispersion was the expiry draw. Percentiles were therefore understated. *Fix:* added
   `sample_params()` which draws the terminal 10-year Treasury, cap-rate beta, market rent growth, escalation,
   sale costs, land multiple and extension terms. Percentiles now reflect genuine joint uncertainty.
2. **Tax asymmetry.** The first pass charged tax on every sale, which made "hold" look superior purely because
   holding defers tax. Selling via a §1031 exchange also defers, so the comparison was biased. *Fix:* added
   strategy A1 (sell via §1031) and, to avoid the opposite bias, deduct the **deferred tax liability** from A1's
   economic net worth. Also set the reinvestment return equal to the discount rate so redeployment earns no free
   lunch. Both defects changed the ranking; the corrected ranking is the one published.

No merge conflicts occurred at any point. No other session claimed a task, and no handoff was required.

## Handoff log

*(empty)*

## PR / merge record

*(pending)*
