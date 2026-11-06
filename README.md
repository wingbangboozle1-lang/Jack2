# PARCEL-01 — Jack in the Box NNN hold / sell analysis

A decision-grade research package and static site answering one question:

> A single-tenant Jack in the Box (NNN) in Central Los Angeles has a lease expiring
> between 2030 and 2035. Should the owner sell before expiry, or hold and renew?

**Recommendation: sell now, and exchange under §1031 into a diversified net-lease
position.** The full reasoning, the scored alternatives, the risk register and the
model are published on the site.

- Live site: <https://wingbangboozle1-lang.github.io/Jack2/>
- Flagged / unverified items: `/flagged.html`
- Sources register: `/sources.html`

---

## Privacy first

This repository and the published site contain **no personal information**.

| | |
|---|---|
| Owner | `OWNER-01` — no name, entity, contact or trust detail |
| Property | `PARCEL-01` — no address, APN, coordinates, photos or lot dimensions |
| Financials | no rent, NOI, purchase price, basis or debt is stored or published |
| Method | every result is normalised **per $1.00 of NOI**, so no dollar figure need exist |

`verify.py` scans every tracked file for emails, phone numbers, street addresses,
parcel-number patterns and plausible Los Angeles coordinates, and fails the build
if any appear. See `PRIVACY.md` and `/privacy.html`.

## What is here

```
index.html … privacy.html   generated static site (GitHub Pages, branch main, root)
assets/                     stylesheet + small progressive-enhancement JS (no CDN)
content/*.md                narrative, edited by hand
data/*.json                 verified findings, sources, model output, decision record
model/projection.py         20,000-path Monte Carlo — deterministic, seeded
build.py                    site generator AND data-integrity gate
verify.py                   data / link / privacy / HTML verification
COORDINATION.md             shared task board for parallel sessions
```

## Rebuild

No dependencies beyond the Python standard library.

```bash
python3 model/projection.py   # regenerate data/projection.json (seeded, reproducible)
python3 build.py              # validate data, generate the site, check links
python3 verify.py             # data integrity, links, privacy scan, HTML structure
```

`build.py` **fails** if a row carries a value without a resolvable official source,
or is marked `unverified` while carrying a value. That is the enforcement mechanism
behind the "no hallucinations" requirement — it is not a policy, it is a build error.

## Data status vocabulary

| Status | Meaning |
|---|---|
| **Verified** | read directly from an official publisher; link given |
| **Derived** | arithmetic on verified numbers; formula in the row note |
| **Reported** | an official body's number, read through secondary coverage; caveat printed |
| **Owner input** | stated by the owner, no public record; never counted as verified |
| **Unverified** | could not be confirmed; value left blank, listed on the Flagged page |

Only U.S. federal agencies, State of California sources, LA County and City
departments, and SEC/EDGAR filings qualify as official.

## Headline findings

| | |
|---|---|
| Diversified net-lease cash yield, 2025 (SEC) | 7.3% |
| Model going-in cap for the subject (assumption) | 6.00% |
| Yield gap in favour of selling | ~130 bp |
| Sell-now median terminal wealth per $1 NOI (2036) | 33.26 |
| Hold-to-expiry median | 26.70 |
| Break-even 2036 exit cap | ~4.7% |
| Modelled tenant default probability | 18.8% (2030 expiry) – 39.9% (2035) |
| 10-year Treasury, 5 Nov 2026 | 4.84% |

## Known limitations

- The lease, address, rent, basis and tenant identity were never supplied; the
  going-in cap rate and rent comparables are documented assumptions, not facts.
- No after-tax comparison is computed, because adjusted basis is unknown.
- Black-swan probabilities are stated judgements, not official statistics.
- Several official pages could not be retrieved during this pass; each is flagged
  rather than filled (see `/flagged.html`).

Nothing here is an appraisal, a tax opinion or investment advice.
