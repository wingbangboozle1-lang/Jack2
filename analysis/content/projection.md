# Projection system

## What this is

A reproducible Monte Carlo model, not a forecast. It runs 20,000 independent paths per expiry case, with a fixed seed, and reports the distribution of terminal wealth for each strategy rather than a single number. The code is in `model/projection.py`; the output is `data/projection.json`; anyone can re-run it and get identical results.

## Why it is normalised to NOI

The owner's rent, NOI and basis are private. Rather than invent them, every result is expressed **per $1.00 of current annual NOI**. Multiply by the owner's actual NOI once and the whole table becomes dollars. This is not a workaround — it is the only honest way to model an asset whose income is withheld.

## The three strategies

| | Strategy | What happens |
|---|---|---|
| **A** | Sell now | Sell in Q4 2026, pay 2.5% transaction cost, exchange into a diversified net-lease position at the benchmark yield, hold to 2036. |
| **B** | Hold to expiry | Collect contract rent to the lease expiry, then sell into a rollover market (+125 bp cap, 6% re-letting cost), redeploy the proceeds into the same diversified position. |
| **C** | Extend, then sell | The tenant renews at expiry at market, the owner holds to 2036 and sells at a 35 bp WALT premium. If the tenant does not renew, this collapses into B. |

Every strategy is measured at the same 2036 horizon, with interim cash flows compounded at the 10-year Treasury (4.84%) so that no strategy gets a favourable reinvestment assumption.

## Inputs: verified anchors versus assumptions

Five inputs are official statistics, each with a source link in the register:

- 10-year Treasury 4.84% (U.S. Treasury, 5 Nov 2026)
- CPI-U Los Angeles 3.7% and food-away-from-home 2.8% (BLS, Sept 2026)
- Diversified net-lease cash yield 7.3% and same-store growth 1.3% (Realty Income FY2025 SEC filing)

Everything else is an explicit **model assumption** with a stated range and a stated basis. The important ones:

- **Going-in cap 6.00%** (range 5.2%–7.0%) — the assumption the conclusion is most sensitive to.
- **Exit cap 2036 6.50%** (range 5.0%–9.0%) — spans 50 bp of compression to 250 bp of expansion.
- **Contract escalator 2.5%** (range 0.5%–4.5%) — below the 3.7% CPI, i.e. a real-terms rent cut.
- **Renewal probability 35%–75%**, drawn per path — the owner does not control this.
- **Tenant default hazard 5%/yr**, after which the unit is re-let 12 months later at 15% below the in-place rent.
- **Earthquake 1.5%/yr** at a 15% value loss; **regional disruption 3.0%/yr** at a 3% income loss.

No assumption is dressed up as a fact. The Methodology page lists every one, and the site renders them separately from the verified table.

## Results

| Expiry case | Strategy | Median | P10 | P90 | Median CAGR | P(beats hold) |
|---|---|---|---|---|---|---|
| 2030 (3.15 yrs) | Sell now | 33.22 | 29.33 | 37.66 | 7.1% | 99.3% |
| 2030 | Extend, then sell | 28.95 | 22.62 | 37.69 | 5.7% | 72.3% |
| 2030 | Hold to expiry | 27.24 | 22.57 | 29.38 | 5.0% | — |
| 2032 (5.65 yrs) | Sell now | 33.26 | 29.49 | 37.63 | 7.1% | 98.2% |
| 2032 | Extend, then sell | 28.31 | 22.23 | 36.57 | 5.4% | 77.1% |
| 2032 | Hold to expiry | 26.70 | 22.19 | 29.58 | 4.8% | — |
| 2035 (9.15 yrs) | Sell now | 33.28 | 29.44 | 37.59 | 7.2% | 96.0% |
| 2035 | Extend, then sell | 27.04 | 21.80 | 35.02 | 5.0% | 82.2% |
| 2035 | Hold to expiry | 26.01 | 21.80 | 29.91 | 4.5% | — |

Read the P10 column carefully. For sell-now it never falls below about 29 — it does not lose money in any of 20,000 paths. For the hold strategies the P10 is roughly 22, and the median is 4–7 points lower. The distribution is not just shifted; it is much wider.

## The break-even question

The cleanest way to test the conclusion is to ask: *what 2036 exit cap would make holding as good as selling?*

| Going-in cap | Expiry 2030 | Expiry 2032 | Expiry 2035 |
|---|---|---|---|
| 5.0% | 3.5% | 3.5% | 3.2% |
| 5.5% | 4.1% | 4.1% | 3.9% |
| 6.0% | 4.7% | 4.7% | 4.7% |
| 6.5% | 5.3% | 5.4% | 5.6% |
| 7.0% | 5.9% | 6.1% | 6.6% |

Holding only wins if the 2036 exit cap is *below* those numbers. At a 6.0% going-in cap, that means an exit cap under about 4.7% — a level that would require a sustained collapse in long-term rates back below 3%. It is not impossible. It is not the base case.

The break-even is fairly stable across the going-in cap, which is reassuring: the conclusion does not depend on guessing the entry price precisely. What it depends on is the **gap between what this asset yields and what diversified net-lease capital yields**. That gap is currently about 130 bp in favour of selling.

## Limitations, stated plainly

- No after-tax comparison is computed, because adjusted basis was not supplied. Tax could change the ranking for a very low-basis owner; §1031 deferral partly neutralises it.
- The going-in cap, exit cap and rent comps are assumptions. Two broker opinions of value would replace the first and second.
- The model does not capture redevelopment or entitlement value. If the land is worth more as something else, the income model understates the hold case.
- It does not capture a hold-until-death basis step-up, which for some owners dominates everything else.
- Black-swan probabilities are judgement calls, not official statistics. They are stated as such.
