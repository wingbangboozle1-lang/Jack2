# Decision & recommendation

## The recommendation

**Sell.** Market the property now and close within 12–18 months, using a §1031 exchange to reinvest into a diversified net-lease position. Do not hold passively to the 2030–2035 expiry.

Confidence: **moderate-to-high on the ranking**, low on the absolute numbers. The ranking held in 96–99% of 20,000 simulated paths per expiry case, and the break-even exit cap (about 4.7%) is far enough from the base case to be robust. The absolute values rest on a going-in cap that has not been verified.

## The argument in five lines

1. The asset yields about 6.0%; diversified net-lease capital was buying at 7.3% in 2025. Exchanging raises income immediately and spreads risk across hundreds of tenants.
2. The tenant is very likely a franchisee in a system that is closing 50–100 units a year, with a 19–40% modelled probability of default before expiry.
3. The owner does not control renewal — the tenant does. "Renew" is not a decision available to the owner without paying for it.
4. Long rates rose 65 bp in 2026 and the Fed tightened in September. A 116 bp cap spread has room to widen, and each 50 bp costs ~7.7% of value.
5. Selling is the only strategy whose 10th-percentile outcome stays above today's value.

## The options, scored

| Option | Median wealth per $1 NOI | P10 | Median CAGR | Versus holding |
|---|---|---|---|---|
| **A. Sell now** | 33.26 | 29.49 | 7.1% | wins 98.2% of paths |
| B. Sell in 2027–28 | 33.26 | 29.49 | 7.1% | equivalent to A |
| C. Extend, then sell | 28.31 | 22.23 | 5.4% | wins 77.1% |
| D. Hold to expiry | 26.70 | 22.19 | 4.8% | baseline |

A and B are effectively the same trade — which is the point. The owner does not have to transact in the next ninety days. What the owner must not do is consume five years of lease term while waiting for a better market.

## Decision gates

These must be cleared in order before a listing agreement is signed. Each gate has a pass action and a fail action on the Decision page data (`data/decision.json`).

| Gate | Question | If it passes | If it fails |
|---|---|---|---|
| **G1** | Is the lease in hand, with amendments, options and any guaranty? | Replace the 2030–2035 placeholder with real dates and re-run the model. | Do not sign anything. No buyer will proceed without an estoppel. |
| **G2** | Is the tenant a franchisee or the corporation — and is the unit on a closure list? | A creditworthy operator with 5+ years of term makes Option B viable. | A closure-list answer or a stressed franchisee accelerates Option A. |
| **G3** | What do two independent broker opinions of value say the going-in cap is? | At 6.5%+ the sell-now edge narrows but persists. | At 5.5% or below, selling is even more clearly right. |
| **G4** | Is there a §1031 replacement at 7.0%+ with institutional credit? | Execute Option A. | Compare a taxable sale plus a diversified liquid portfolio — do not exchange into a worse asset to defer tax. |
| **G5** | Is the objective a hold-until-death basis step-up? | Option D can dominate on an after-tax, multi-generational basis and this ranking does not apply. | Proceed with A or B. |

## Tax execution

- Structure any sale as a **§1031 exchange**. Gain is deferred, not forgiven; the old basis carries into the replacement.
- Expect **unrecaptured §1250 gain at up to 25%** on depreciation taken, long-term capital gain at up to 20%, and possible net investment income tax, on whatever is not deferred.
- §1031 covers **real property only**. A diversified net-lease position assembled through a DST or a small portfolio qualifies; securities do not.
- **California basis tracking** applies when replacement property sits outside California. Confirm with a CPA before signing — this is a common and expensive surprise.
- **Measure ULA** adds 4% between $5.4m and $10.9m and 5.5% at or above $10.9m. If the property's value sits near a threshold, the pricing decision and the tax decision are the same decision.

## Risk budget

The recommendation is not "eliminate risk" — it is "hold a level of risk that is survivable and adequately paid for."

- **Single-tenant exposure at this location: zero after sale.** Replace with a portfolio in which no single tenant is material.
- **Downside tolerance:** the recommended path's P10 is above today's value, so the modelled downside is opportunity cost rather than loss of capital.
- **Liquidity:** DST interests are illiquid for their term. Size the position to the owner's actual liquidity needs, keeping a liquid sleeve outside the exchange.
- **Uninsurable risk:** obtain a seismic (PML) study and a binding property quote before closing. If either cannot be obtained on commercial terms, treat that as confirmation to sell, not as a reason to delay.

## What would change the answer

- A verified going-in cap materially above 7.0% — the asset is cheaper than assumed.
- A signed 10-year extension with a creditworthy guarantor at market rent — moves Option C to the top.
- A credible redevelopment or rezoning path that creates land value the income model cannot see.
- A hold-until-death estate objective, which the model does not capture.
- A sustained fall in long Treasury yields back toward 3% — though that would also raise the price at which the owner could sell.

## One sentence for the owner

The property is a good asset in a soft market with a weakening tenant, and the owner is being paid 130 bp less than diversified net-lease capital to hold the concentration — so sell while the lease term still has value to a buyer, exchange into something that pays more and depends on no single franchisee, and keep the redevelopment option open by not being forced to transact at a rollover.
