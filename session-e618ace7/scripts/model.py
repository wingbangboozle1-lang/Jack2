#!/usr/bin/env python3
"""
Projection engine for the Central Los Angeles Jack in the Box NNN asset.

Design rules
------------
1. Nothing in this file is data. Every number it reads comes from
   ../data/assumptions.json, and every assumption is labelled on the site.
2. Output is normalised to $100,000 of current annual net operating income.
   The Owner's actual NOI is unknown and is never guessed.
3. Deterministic: same inputs, same bytes out. The Monte Carlo is seeded.
4. Standard library only.

Core valuation identity
-----------------------
    value = NOI / cap
    cap(term, treasury) = base_cap + beta * (treasury - 0.0486)
                          + slope * max(0, 10 - remaining_term), floor 4.50%

Two offsets move in opposite directions: NOI grows, remaining term shrinks.
Which wins is the whole question.

Hazard treatment
----------------
Every hold-type strategy is exposed to the same hazard draws within a trial, so the
strategies are compared on identical luck. Sell-now strategies are not exposed because
the asset is sold before the exposure period begins.
"""
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")

NOI0 = 100_000.0
YEAR0, YEAR1 = 2026, 2040
N = YEAR1 - YEAR0

with open(os.path.join(DATA, "assumptions.json"), encoding="utf-8") as f:
    A = {a["id"]: a for a in json.load(f)["assumptions"]}


def num(aid):
    s = A[aid]["value"].replace(",", "").replace("$", "")
    buf, out = "", []
    for ch in s:
        if ch.isdigit() or ch == ".":
            buf += ch
        else:
            if buf:
                out.append(buf)
                buf = ""
    if buf:
        out.append(buf)
    return float(out[0])


BASE_CAP = num("A01") / 100
TERM_SLOPE = num("A02") / 10000
RATE_BETA = num("A03")
GROWTH = num("A04") / 100
TERM0 = int(num("A05"))
P_RENEW = num("A06") / 100
BROKER = num("A09") / 100
T_SALE = num("A10") / 100
GAIN_SHARE = num("A11") / 100
R_TAXABLE = num("A12") / 100
R_1031 = num("A13") / 100
T_ORD = num("A14") / 100
P_IMPAIR = num("A15") / 100
P_LOSS = num("A16") / 100

TREASURY_SPOT = 0.0486
CASH_RATE = 0.0433
CASH_AFTER_TAX = CASH_RATE * (1 - T_ORD)

COUNTY_DTT = 0.0011
CITY_BASE = 0.0045
ULA_T1_PRICE, ULA_T1 = 5_400_000.0, 0.040
ULA_T2_PRICE, ULA_T2 = 10_900_000.0, 0.055
CAP_FLOOR = 0.0450

BASIS = (1 - GAIN_SHARE) * (NOI0 / BASE_CAP)

# share of the reinvestment return taken as taxable current income (A20)
YIELD_SHARE = num("A20") / 100


def cap_rate(term, treasury=TREASURY_SPOT, base_cap=None):
    b = BASE_CAP if base_cap is None else base_cap
    c = b + RATE_BETA * (treasury - TREASURY_SPOT) + TERM_SLOPE * max(0.0, 10.0 - term)
    return max(CAP_FLOOR, c)


def value(noi, term, treasury=TREASURY_SPOT, base_cap=None):
    return noi / cap_rate(term, treasury, base_cap)


def sale_costs(price):
    c = price * (BROKER + COUNTY_DTT + CITY_BASE)
    if price >= ULA_T2_PRICE:
        c += price * ULA_T2
    elif price >= ULA_T1_PRICE:
        c += price * ULA_T1
    return c


def tax_on_sale(price, basis=BASIS):
    return max(0.0, price - basis) * T_SALE


def net_sale(price, basis=BASIS):
    return price - sale_costs(price) - tax_on_sale(price, basis)


def grow_cash(amount, years):
    return amount * (1 + CASH_AFTER_TAX) ** years


def reinvest(p, r, years, basis=0.0, pay_end_tax=False):
    """After-tax terminal wealth from reinvesting p at total return r for `years`.

    The return is split into a taxable current yield (YIELD_SHARE of r) and appreciation.
    Appreciation is only taxed if pay_end_tax (the 1031 case, where basis is carried over);
    a plain taxable sale has already been taxed at the point of sale.
    """
    y = r * YIELD_SHARE
    g = r - y
    end = p * (1 + g) ** years
    income = sum(p * y * (1 - T_ORD) * (1 + g) ** (years - t) for t in range(1, years + 1))
    total = end + income
    if pay_end_tax:
        total -= max(0.0, end - basis) * T_SALE
    return total


# ------------------------------------------------------------------ hazard
def draw_hazard(rng):
    """Return a permanent NOI multiplier for one year."""
    if rng is None:
        return 1.0
    u = rng.random()
    if u < P_LOSS:
        return 0.10
    if u < P_LOSS + P_IMPAIR:
        return 0.75
    return 1.0


# ------------------------------------------------------------------ strategies
def hold_path(rng=None, growth=GROWTH, term0=TERM0, treasury=TREASURY_SPOT,
              p_renew=None, renew_choice=None, uplift=0.0, base_cap=None):
    """Run the lease to expiry and react. Returns (terminal_value, cash, impaired)."""
    p = P_RENEW if p_renew is None else p_renew
    noi, term, cash = NOI0, float(term0), 0.0
    for year in range(1, N + 1):
        noi *= (1 + growth) * draw_hazard(rng)
        term -= 1
        if term <= 0:
            if renew_choice is None:
                renews = True if rng is None else (rng.random() < p)
            else:
                renews = renew_choice
            if renews:
                noi *= (1 + uplift)
                term = 10.0
            else:
                noi *= 0.50          # 18 months of downtime at half rent
                noi *= 0.90          # re-let below the expiring rent
                cash -= 0.06 * value(noi, 10.0, treasury, base_cap)
                term = 10.0
        cash += noi * (1 - T_ORD)
    price = value(noi, max(term, 0.5), treasury, base_cap)
    return net_sale(price), cash, noi


def run_hold(rng=None, growth=GROWTH, term0=TERM0, treasury=TREASURY_SPOT, p_renew=None,
             base_cap=None):
    tv, cash, _ = hold_path(rng, growth, term0, treasury, p_renew, None, 0.0, base_cap)
    return tv + grow_cash(cash, 1)


def run_hold_expected(growth=GROWTH, term0=TERM0, treasury=TREASURY_SPOT, p_renew=None,
                      base_cap=None):
    """Deterministic hold = probability-weighted outcome of renew vs not renew."""
    p = P_RENEW if p_renew is None else p_renew
    a = hold_path(None, growth, term0, treasury, p, True, 0.0, base_cap)
    b = hold_path(None, growth, term0, treasury, p, False, 0.0, base_cap)
    tv = p * a[0] + (1 - p) * b[0]
    cash = p * a[1] + (1 - p) * b[1]
    return tv + grow_cash(cash, 1)


def extend_path(rng=None, growth=GROWTH, term0=TERM0, treasury=TREASURY_SPOT, uplift=0.0,
                base_cap=None, sell_year=None, sell_return=R_TAXABLE):
    """Extend the lease by ten years during 2027, then hold or sell at sell_year."""
    noi, term, cash = NOI0, float(term0), 0.0
    for year in range(1, N + 1):
        noi *= (1 + growth) * draw_hazard(rng)
        term -= 1
        if year == 1:
            noi *= (1 + uplift)
            term = max(term, 0.0) + 10.0
        cash += noi * (1 - T_ORD)
        yr = YEAR0 + year
        if sell_year is not None and yr == sell_year:
            price = value(noi, term, treasury, base_cap)
            proceeds = net_sale(price)
            return reinvest(proceeds, sell_return, YEAR1 - yr) + grow_cash(cash, YEAR1 - yr)
    price = value(noi, max(term, 0.5), treasury, base_cap)
    return net_sale(price) + grow_cash(cash, 1)


def run_sell_now(kind="taxable", growth=GROWTH, term0=TERM0, treasury=TREASURY_SPOT,
                 base_cap=None):
    price = value(NOI0, float(term0), treasury, base_cap)
    if kind == "taxable":
        proceeds = net_sale(price)
        return reinvest(proceeds, R_TAXABLE, N)
    proceeds = price - sale_costs(price)        # tax deferred
    return reinvest(proceeds, R_1031, N, basis=BASIS, pay_end_tax=True)


def run_wait_then_sell(wait=2, growth=GROWTH, term0=TERM0, treasury=TREASURY_SPOT,
                       base_cap=None):
    noi, term, cash = NOI0, float(term0), 0.0
    for _ in range(wait):
        noi *= (1 + growth)
        term -= 1
        cash += noi * (1 - T_ORD)
    price = value(noi, max(term, 0.5), treasury, base_cap)
    return reinvest(net_sale(price), R_TAXABLE, N - wait) + grow_cash(cash, N - wait)


STRATEGIES = [
    ("HOLD", "Passive hold to expiry, then react"),
    ("WAIT2Y", "Wait two years, then sell"),
    ("EXT_HOLD", "Extend in 2027, hold to 2040"),
    ("EXT_SELL", "Extend in 2027, sell in 2030"),
    ("SELL_NOW", "Sell in 2026 and pay the tax"),
    ("SELL_1031", "Sell in 2026 through a Section 1031 exchange"),
]


def run(code, rng=None, growth=GROWTH, term0=TERM0, treasury=TREASURY_SPOT, p_renew=None,
        base_cap=None):
    if code == "HOLD":
        return run_hold(rng, growth, term0, treasury, p_renew, base_cap)
    if code == "HOLD_E":
        return run_hold_expected(growth, term0, treasury, p_renew, base_cap)
    if code == "WAIT2Y":
        return run_wait_then_sell(2, growth, term0, treasury, base_cap)
    if code == "EXT_HOLD":
        return extend_path(rng, growth, term0, treasury, 0.0, base_cap)
    if code == "EXT_SELL":
        return extend_path(rng, growth, term0, treasury, 0.0, base_cap, 2030)
    if code == "SELL_NOW":
        return run_sell_now("taxable", growth, term0, treasury, base_cap)
    if code == "SELL_1031":
        return run_sell_now("1031", growth, term0, treasury, base_cap)
    raise ValueError(code)


def pct(xs, q):
    i = min(len(xs) - 1, max(0, int(round(q * (len(xs) - 1)))))
    return xs[i]


def main():
    det = {code: round(run("HOLD_E" if code == "HOLD" else code), 0) for code, _ in STRATEGIES}

    trials = 10_000
    rng = random.Random(20261107)
    draws = []
    for _ in range(trials):
        draws.append({
            "growth": max(0.0, rng.gauss(GROWTH, 0.010)),
            "term0": max(1.0, rng.gauss(TERM0, 1.2)),
            "treasury": max(0.02, rng.gauss(TREASURY_SPOT, 0.012)),
            "p_renew": min(0.98, max(0.05, rng.gauss(P_RENEW, 0.15))),
            "seed": rng.randrange(1 << 30),
        })

    results, beats = {}, {}
    hold_vals = []
    for d in draws:
        hold_vals.append(run("HOLD", random.Random(d["seed"]), d["growth"], d["term0"],
                             d["treasury"], d["p_renew"]))
    for code, _ in STRATEGIES:
        vals = []
        for d in draws:
            vals.append(run(code, random.Random(d["seed"]), d["growth"], d["term0"],
                            d["treasury"], d["p_renew"]))
        vals.sort()
        inv = sum(1.0 / v for v in vals if v > 0) / len(vals)
        results[code] = {
            "ce_gamma2": round(1.0 / inv),
            "mean": round(sum(vals) / len(vals)),
            "p05": round(pct(vals, 0.05)),
            "p25": round(pct(vals, 0.25)),
            "p50": round(pct(vals, 0.50)),
            "p75": round(pct(vals, 0.75)),
            "p95": round(pct(vals, 0.95)),
        }
        beats[code] = round(sum(1 for v, h in zip(vals, hold_vals) if v > h) / trials, 4)

    sensitivity = []
    for g in (0.020, 0.030, 0.037):
        for c in (0.0475, 0.0500, 0.0525, 0.0550, 0.0575):
            sensitivity.append({
                "growth_pct": round(g * 100, 1),
                "base_cap_pct": round(c * 100, 2),
                "hold": round(run("HOLD_E", None, g, TERM0, TREASURY_SPOT, None, c)),
                "ext_hold": round(run("EXT_HOLD", None, g, TERM0, TREASURY_SPOT, None, c)),
                "ext_sell": round(run("EXT_SELL", None, g, TERM0, TREASURY_SPOT, None, c)),
                "sell_now": round(run("SELL_NOW", None, g, TERM0, TREASURY_SPOT, None, c)),
                "sell_1031": round(run("SELL_1031", None, g, TERM0, TREASURY_SPOT, None, c)),
            })

    term_table = []
    for term in (1, 2, 3, 5, 7, 10, 15, 20):
        term_table.append({
            "remaining_term": term,
            "cap_pct": round(cap_rate(term) * 100, 2),
            "value_per_100k_noi": round(value(NOI0, term)),
            "change_vs_10yr_pct": round((value(NOI0, term) / value(NOI0, 10) - 1) * 100, 1),
        })

    cap_now = cap_rate(TERM0)
    ula_noi = ULA_T1_PRICE * cap_now

    out = {
        "meta": {
            "generated_by": "session-e618ace7/scripts/model.py",
            "normalisation": "All figures are per $100,000 of current annual net operating income. A ratio, not a property value.",
            "horizon": YEAR1,
            "seed": 20261107,
            "trials": trials,
            "currency": "nominal USD",
            "warning": "Assumption-driven, not an appraisal. See data/assumptions.json and the sensitivity grid.",
            "deterministic_hold": "The deterministic HOLD figure is the probability-weighted average of renewing and not renewing at the stated 65% assumption; the Monte Carlo draws both.",
        },
        "inputs": {
            "base_cap_pct": round(BASE_CAP * 100, 2),
            "cap_now_pct": round(cap_now * 100, 2),
            "term_slope_bp_per_year": round(TERM_SLOPE * 10000, 1),
            "rate_beta": RATE_BETA,
            "noi_growth_pct": round(GROWTH * 100, 2),
            "term0_years": TERM0,
            "p_renew_pct": round(P_RENEW * 100),
            "tax_ordinary_pct": round(T_ORD * 100, 1),
            "tax_sale_pct": round(T_SALE * 100, 1),
            "gain_share_of_price_pct": round(GAIN_SHARE * 100, 1),
            "treasury_spot_pct": TREASURY_SPOT * 100,
            "cash_rate_pct": CASH_RATE * 100,
            "yield_share_of_return_pct": round(YIELD_SHARE * 100),
            "basis_usd": round(BASIS),
            "ula_threshold_price": ULA_T1_PRICE,
            "ula_threshold_noi": round(ula_noi),
        },
        "deterministic": det,
        "monte_carlo": results,
        "prob_beats_hold": beats,
        "sensitivity": sensitivity,
        "term_table": term_table,
        "note_on_ula": (
            f"At the base cap rate of {cap_now*100:.2f}%, the property reaches the "
            f"${ULA_T1_PRICE:,.0f} Measure ULA threshold at about ${ula_noi:,.0f} of annual NOI. "
            "Below it the 4% City surtax does not apply; above it the surtax applies to the whole price."
        ),
    }
    with open(os.path.join(DATA, "projections.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
        f.write("\n")

    print("wrote data/projections.json")
    for code, _ in STRATEGIES:
        r = results[code]
        print(f"  {code:9s} det {det[code]:>10,.0f} | mean {r['mean']:>10,.0f} "
              f"| p05 {r['p05']:>10,.0f} | p50 {r['p50']:>10,.0f} | p95 {r['p95']:>10,.0f} "
              f"| CE(2) {r['ce_gamma2']:>10,.0f} | beats hold {beats[code]*100:5.1f}%")


if __name__ == "__main__":
    main()
