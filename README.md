# Jack2 — NNN Jack in the Box, central Los Angeles

An anonymised decision dossier answering one question:

> **Hold, renew, or sell** a single-tenant NNN Jack in the Box in central Los Angeles, with a lease
> described as expiring between **2030 and 2035**?

**Live site:** https://wingbangboozle1-lang.github.io/Jack2/

---

## The recommendation

**Do not let the lease run to expiry. Run a dual track for 6–12 months: pursue an early 10–15 year extension
*and* prepare a §1031 sale at the same time. Sell either way — the only variable is whether you sell with
13–15 years of term or with 4–9.**

Backed by 20,000 Monte-Carlo paths across five courses of action. Ranked on risk-adjusted (certainty-equivalent)
after-tax wealth, because the Owner's stated objective is wealth preservation with manageable risk:

| Rank | Strategy | Risk-adjusted score | Worst-decile |
|---|---|---|---|
| 1 | Sell now via §1031 | **11.79** | 10.96 |
| 2 | Extend now, sell 2028 | 11.06 | 9.51 |
| 3 | Sell now, pay the tax | 10.29 | 9.66 |
| 4 | Hold to expiry, sell vacant | 9.34 | 6.21 |
| 5 | Renew at expiry, hold to 2040 | 3.97 | **1.88** |

"Renew and hold" wins most often (52.6%) and has the highest median — and a tail five times worse than selling.
That is what this dossier means by "manageable risk".

---

## Privacy

**No personal information is collected, stored or published.** Owner, tenant, address, APN and legal description
are placeholders. The Owner's income, net worth, tax bracket and basis are never collected: the projection engine
is normalised to **$1.00 of current annual NOI**, so no financial disclosure is required to get dollar answers —
just multiply.

A consequence, published rather than hidden: because the address was deliberately not retained, parcel-level facts
(fire-hazard zone, flood zone, seismic class, school assignment, assessed value) are **blank and flagged** rather
than guessed. See the site's *Flagged for Review* page.

---

## Verification standard

Every table row on the site carries a **source link**, a **source tier** and a **status**.

| Tier | Meaning |
|---|---|
| **T1** | Government or central-bank primary source (FRED, BLS, Census, SEC, IRS, CAL FIRE, CA Legislature, LA County Assessor) |
| **T3** | Named commercial research house (The Boulder Group) — directional only, always badged |
| **D** | Arithmetic performed by this model on T1 inputs, with the formula shown |
| **A** | Analytical assumption — never presented as fact |

Statuses: `verified` · `derived` · `assumption` · `owner-stated` · `unverified`.
**An `unverified` row is always blank.** `model/build_facts.py` asserts this and fails the build otherwise.

---

## Repository layout

```
COORDINATION.md              shared task board, session claims, verification ledger
research/                    the analytical corpus (00 method → 07 executive summary)
model/
  build_facts.py             emits docs/data/facts.json — 195 sourced rows, with assertions
  projection_model.py        Monte-Carlo engine, fixed seed, emits docs/data/projections.json
  build_site.py              generates docs/*.html and fails on any broken internal link
docs/                        the published GitHub Pages site (no build step, no CDN)
```

## Reproduce everything

```bash
python3 model/build_facts.py        # dataset + integrity assertions
python3 model/projection_model.py   # model outputs (deterministic; seed 20261106)
python3 model/build_site.py         # site + link validation
python3 -m http.server -d docs 8080 # preview
```

No third-party libraries. No network access required to rebuild.

---

## Data cut-off

**2026-11-06.** Rates and prices move; re-run the engine before acting on any number.

*This is an analytical dossier, not legal, tax or investment advice. The tax module uses stated assumptions and
flags items that were not verified. Engage a qualified intermediary before any §1031 exchange and a California
tax adviser before identifying replacement property outside California.*
