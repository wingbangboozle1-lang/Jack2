#!/usr/bin/env python3
"""
Session J projection engine - Central Los Angeles Jack in the Box on an NNN lease.

Design rules
------------
1. Everything is normalised to $100,000 of in-place annual NOI. No private rent,
   basis, loan or owner figure is ever required or stored. The owner can scale
   every output by (actual NOI / 100,000).
2. Only two kinds of number appear: (a) verified official inputs, loaded from
   data/sources.json facts cited in the text, and (b) analyst assumptions, which
   are declared in ASSUMPTIONS below and published on the site as assumptions.
   No assumption is ever labelled as an observation.
3. The engine is deterministic. The Monte Carlo is seeded, so the published
   output is reproducible byte-for-byte.

Run:  python3 session-6ad87c21/scripts/model.py
Out:  session-6ad87c21/data/model_output.json
"""

import json
import math
import os
import random
import statistics
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
NOI0 = 100_000.0
YEAR0 = 2026
HORIZON = 2040
SEED = 20261108

# --------------------------------------------------------------------------- assumptions
# Every entry here is an ASSUMPTION (tier C). Each carries the range tested and a
# note saying what it stands in for and how to replace it with a real figure.
ASSUMPTIONS = [
    {"id": "A1", "name": "Base-case net operating income growth", "value": 0.020,
     "range": "1.0% to 3.0% a year", "note":
     "Stands in for the lease's contractual escalations. LA metro CPI-U is +3.7% and ECI +3.9% "
     "(S01), so 2.0% is deliberately conservative for a legacy NNN lease. Replace with the actual "
     "escalation clause."},
    {"id": "A2", "name": "Remaining lease term at the access date", "value": 6,
     "range": "4 to 9 years", "note":
     "Derived from the owner-supplied 2030-2035 expiry window and a 2032 midpoint. The exact date is "
     "unknown (F108); the 2030 and 2035 endpoints are both tested in the sensitivity grid."},
    {"id": "A3", "name": "Base-case capitalisation rate for a 10-year-or-longer term", "value": 0.0600,
     "range": "5.50% to 6.75%", "note":
     "No official public cap-rate series exists (F86). The level is anchored to the 4.86% 10-year "
     "Treasury (S09) plus a property and credit spread, and must be replaced by a broker opinion of "
     "value or an appraisal."},
    {"id": "A4", "name": "Term premium: cap-rate widening per year of term below 10 years", "value": 0.0025,
     "range": "0.15% to 0.35% a year", "note":
     "The market penalty for a lease that will roll soon. Capped at 1.50% in total."},
    {"id": "A5", "name": "Sale costs", "value": 0.0481,
     "range": "4.0% to 6.5%", "note":
     "Broker 4.0% + City base transfer tax 0.45% (F90) + assumed County documentary transfer tax 0.11% "
     "(F97, unverified) + title/legal 0.25%. The 4.0%-5.5% Measure ULA surtax (F91, F92) is added "
     "automatically when the modelled price crosses the official threshold."},
    {"id": "A6", "name": "Adjusted cost basis as a share of 2026 value", "value": 0.45,
     "range": "0.25 to 0.75", "note":
     "Private tax data (F113) are never collected. This ratio only sets the size of the tax bill in the "
     "after-tax comparison; the ranking is tested across the range."},
    {"id": "A7", "name": "Tax on appreciation (federal + California)", "value": 0.371,
     "range": "0.30 to 0.41", "note":
     "20% federal long-term capital gain + 3.8% net investment income tax + 13.3% California top rate "
     "(F98, unverified). Replace with the owner's actual marginal position."},
    {"id": "A8", "name": "Tax on unrecaptured depreciation", "value": 0.383,
     "range": "0.25 to 0.41", "note":
     "25% federal unrecaptured Section 1250 rate + 13.3% California. Applied to the share of gain "
     "treated as recapture."},
    {"id": "A9", "name": "Share of gain treated as depreciation recapture", "value": 0.40,
     "range": "0.20 to 0.60", "note": "Depends on holding period and prior depreciation taken."},
    {"id": "A10", "name": "Discount rate for present values", "value": 0.050,
     "range": "4.5% to 6.0%", "note":
     "Anchored to the 4.86% 10-year Treasury on 2026-11-06 (F81)."},
    {"id": "A11", "name": "Reinvestment cap rate after a sale (diversified NNN)", "value": 0.065,
     "range": "6.0% to 7.5%", "note":
     "Where the proceeds go after a Section 1031 exchange. A diversified net-lease portfolio is assumed "
     "to trade wider than a single asset because it carries no single-tenant risk."},
    {"id": "A12", "name": "Reinvestment income growth", "value": 0.020, "range": "1.5% to 2.5%",
     "note": "Contractual escalations in the replacement portfolio."},
    {"id": "A13", "name": "Probability the tenant renews at or above in-place rent", "value": 0.65,
     "range": "0.40 to 0.85", "note":
     "Informed by the closure programme and negative same-store sales (F68, F76), which push it down, "
     "and by the scarcity of drive-thru sites, which pushes it up. It is a judgement, not an observation."},
    {"id": "A14", "name": "Rent reset on renewal", "value": 0.00, "range": "-15% to +10%",
     "note": "The brand's stated policy is to renew at market. A zero reset is the neutral case."},
    {"id": "A15", "name": "Vacancy period if the tenant does not renew", "value": 1.5,
     "range": "0.75 to 3.0 years", "note":
     "Drive-thru re-tenanting takes time; the site is desirable but the conditional-use permit is not "
     "automatic."},
    {"id": "A16", "name": "Re-leasing cost and capital", "value": 0.05, "range": "0.03 to 0.10",
     "note": "Share of value spent on tenant improvements, leasing commissions and downtime make-ready."},
    {"id": "A17", "name": "Cap rate on a re-let asset with no credit tenant", "value": 0.0675,
     "range": "6.0% to 8.0%", "note": "A local operator is weaker credit than a national brand."},
    {"id": "A18", "name": "Annual volatility of NOI growth", "value": 0.015, "range": "0.010 to 0.025",
     "note": "Used only in the Monte Carlo."},
    {"id": "A19", "name": "Annual volatility of the cap rate", "value": 0.0015, "range": "0.0010 to 0.0025",
     "note": "A 15 basis point annual standard deviation on the cap rate compounds to a wide band by 2040."},
    {"id": "A20", "name": "Black-swan impairment", "value": 0.25, "range": "0.15 to 0.40",
     "note":
     "Value loss, applied in 4% of Monte Carlo trials, from a severe earthquake, an urban fire, a "
     "pandemic-style closure order or a forced sale. The 30-year M>=6.7 probability in the LA region is "
     "60% (F99), so a 4% chance over 15 years is not a tail that can be ignored - it is a tail that is "
     "insured against, which is why it is modest here and discussed at length on the risk page."},
    {"id": "A21", "name": "Risk aversion (CRRA coefficient) for the certainty equivalent", "value": 2.0,
     "range": "1.0 to 3.0", "note":
     "A coefficient of 2 means the owner would accept a materially lower certain amount instead of a "
     "risky gamble with the same average. This is the measure that ranks the strategies."},
]

A = {a["id"]: a["value"] for a in ASSUMPTIONS}

SCENARIOS = {
    "Bear": {"growth": 0.010, "base_cap": 0.0675, "cap_drift": 0.0015,
             "label": "Recession, cap-rate expansion, tenant weakness"},
    "Base": {"growth": 0.020, "base_cap": 0.0600, "cap_drift": 0.0,
             "label": "Slow growth, flat cap rates, tenant performs"},
    "Bull": {"growth": 0.030, "base_cap": 0.0550, "cap_drift": -0.0010,
             "label": "Rate relief, strong trade area, early extension"},
}


# --------------------------------------------------------------------------- mechanics
def term_premium(remaining_years):
    """Cap-rate penalty for a lease that will roll soon. Capped at 150 bp."""
    shortfall = max(0.0, 10.0 - remaining_years)
    return min(0.0150, A["A4"] * shortfall)


def cap_rate(scenario, year, remaining_years):
    s = SCENARIOS[scenario]
    drift = s["cap_drift"] * (year - YEAR0)
    return s["base_cap"] + term_premium(remaining_years) + drift


def transfer_tax_on(price):
    """City base 0.45% plus the Measure ULA surtax at the official thresholds."""
    rate = 0.0045
    if price >= 10_900_000:
        rate = 0.0595
    elif price > 5_400_000:
        rate = 0.0445
    return rate


def sale_costs(price):
    """Broker + title/legal + County DTT (assumption A5) + City transfer taxes."""
    fixed = 0.040 + 0.0025 + 0.0011
    return price * (fixed + transfer_tax_on(price))


def tax_on_sale(price, basis, deferred=False):
    """Total income tax on a taxable sale; zero when a Section 1031 exchange defers it."""
    if deferred:
        return 0.0
    gain = price - basis
    if gain <= 0:
        return 0.0
    recapture = gain * A["A9"]
    appreciation = gain - recapture
    return recapture * A["A8"] + appreciation * A["A7"]


def noi_path(scenario, years, start_value=NOI0, start_year=YEAR0, growth=None):
    g = SCENARIOS[scenario]["growth"] if growth is None else growth
    return {y: start_value * (1 + g) ** (y - start_year) for y in years}


# --------------------------------------------------------------------------- strategies
def run_strategy(strategy, scenario, expiry=2032, growth=None, cap_shift=0.0,
                 impaired=False, reinvest_cap=None, exchange=True):
    """
    Every strategy is measured at 2040: the owner either still holds the asset (marked to
    market, net of notional sale costs) or holds a reinvested diversified portfolio.

    exchange=True defers tax at an interim sale under IRC 1031 (F94-F96) and carries the
    original basis forward, so the tax is paid at the 2040 liquidation instead. exchange=False
    pays it at the interim sale. Both are modelled, because the exchange is a decision, not a
    fact.
    """
    growth = A["A1"] if growth is None else growth
    base_cap = SCENARIOS[scenario]["base_cap"] + cap_shift
    reinvest_cap = A["A11"] if reinvest_cap is None else reinvest_cap
    value_now = NOI0 / (base_cap + term_premium(max(0, expiry - YEAR0)))
    basis0 = A["A6"] * value_now
    years = list(range(YEAR0, HORIZON + 1))

    def cap_at(year, remaining, override=None):
        if override is not None:
            return override
        return base_cap + term_premium(remaining) + SCENARIOS[scenario]["cap_drift"] * (year - YEAR0)

    cash = {y: 0.0 for y in years}
    notes = []

    def reinvest(net, from_year, basis_after):
        """Deploy sale proceeds into a diversified NNN portfolio and liquidate it at 2040."""
        state = {"value": net}
        for y in range(from_year + 1, HORIZON + 1):
            income = net * reinvest_cap * (1 + A["A12"]) ** (y - from_year - 1)
            cash[y] += income
        final_price = (net * reinvest_cap * (1 + A["A12"]) ** (HORIZON - from_year)) / reinvest_cap
        cash[HORIZON] += final_price - sale_costs(final_price)
        cash[HORIZON] -= tax_on_sale(final_price, basis_after, deferred=False)
        return final_price

    # ---------- sell at the access date, then reinvest
    if strategy in ("S1_sell_now_1031", "S2_sell_now_taxable"):
        price = value_now
        if impaired:
            price *= (1 - A["A20"])
        costs = sale_costs(price)
        deferred = strategy == "S1_sell_now_1031"
        tax = tax_on_sale(price, basis0, deferred=deferred)
        net = price - costs - tax
        cash[YEAR0] += net
        basis_after = basis0 if deferred else net
        notes.append(f"Sold at {price:,.0f} on a {expiry - YEAR0}-year remaining term. "
                     f"Costs {costs:,.0f}, tax {tax:,.0f} ({'deferred under 1031' if deferred else 'paid now'}).")
        final_price = reinvest(net, YEAR0, basis_after)
        notes.append(f"Proceeds reinvested at {reinvest_cap:.2%} and liquidated in {HORIZON} "
                     f"at {final_price:,.0f}.")

    # ---------- hold, then sell at a chosen year and reinvest
    elif strategy in ("S3_hold_to_expiry_renew_then_sell", "S4_extend_then_sell",
                      "S5_expire_no_renewal"):
        if strategy == "S4_extend_then_sell":
            sale_year, remaining_at_sale, rent_factor, vacancy = 2030, 12, 1.0, 0.0
            note = ("Tenant agrees in 2027 to add 10 years at or above in-place rent; the asset is "
                    "sold in 2030 with about 12 years of term left.")
        elif strategy == "S3_hold_to_expiry_renew_then_sell":
            sale_year, remaining_at_sale, rent_factor, vacancy = 2036, 10, 1 + A["A14"], 0.0
            note = "Held to the 2032 expiry, renewed at market on a 10-year term, sold in 2036."
        else:
            sale_year, remaining_at_sale, rent_factor, vacancy = 2036, 10, 0.90, A["A15"]
            note = ("Tenant leaves at expiry; the site is dark for the vacancy period, re-let to a "
                    "local operator at 90% of prior rent, and sold in 2036 without brand credit.")
        paths = noi_path(scenario, range(YEAR0, sale_year + 1), growth=growth)
        for y in range(YEAR0, sale_year + 1):
            if vacancy:
                if y < expiry + vacancy:
                    cash[y] += 0.0
                else:
                    cash[y] += paths[y] * rent_factor
            else:
                cash[y] += paths[y] * (1.0 if y < expiry else rent_factor)
        cap_override = (A["A17"] if strategy == "S5_expire_no_renewal" else None)
        price = paths[sale_year] * rent_factor / cap_at(sale_year, remaining_at_sale, cap_override)
        if impaired:
            price *= (1 - A["A20"])
        costs = sale_costs(price)
        if strategy == "S5_expire_no_renewal":
            costs += price * A["A16"]
        tax = tax_on_sale(price, basis0, deferred=exchange)
        net = price - costs - tax
        cash[sale_year] += net
        notes.append(note)
        notes.append(f"Sold at {price:,.0f} in {sale_year}. Costs {costs:,.0f}, "
                     f"tax {tax:,.0f} ({'deferred under 1031' if exchange else 'paid now'}).")
        final_price = reinvest(net, sale_year, basis0 if exchange else net)
        notes.append(f"Proceeds reinvested at {reinvest_cap:.2%} and liquidated in {HORIZON} "
                     f"at {final_price:,.0f}.")

    # ---------- never sell: hold the asset through 2040
    elif strategy == "S6_hold_to_2040":
        rent_factor = 1 + A["A14"]
        paths = noi_path(scenario, years, growth=growth)
        for y in years:
            cash[y] += paths[y] * (1.0 if y < expiry else rent_factor)
        remaining_2040 = max(0, (expiry + 10) - HORIZON)
        price = paths[HORIZON] * rent_factor / cap_at(HORIZON, remaining_2040)
        if impaired:
            price *= (1 - A["A20"])
        cash[HORIZON] += price - sale_costs(price)
        notes.append("Held throughout; renewed in 2032 on a 10-year term. The 2040 position is marked "
                     f"to market at {price:,.0f} net of notional sale costs, with no sale tax assumed "
                     "because no sale has occurred.")
    else:
        raise ValueError(strategy)

    terminal = sum(cash[y] for y in years)
    npv = sum(cash[y] / (1 + A["A10"]) ** (y - YEAR0) for y in years)
    return {"strategy": strategy, "scenario": scenario, "sale_notes": notes,
            "cash": {str(y): round(v, 2) for y, v in cash.items()},
            "terminal_after_tax": round(terminal, 2), "npv": round(npv, 2),
            "value_now": round(value_now, 2)}


STRATEGY_LABELS = {
    "S1_sell_now_1031": "Sell now through a Section 1031 exchange",
    "S2_sell_now_taxable": "Sell now and pay the tax",
    "S3_hold_to_expiry_renew_then_sell": "Hold to expiry, renew at market, sell in 2036",
    "S4_extend_then_sell": "Extend early in 2027, sell in 2030 with 12 years of term",
    "S5_expire_no_renewal": "Do not renew: go dark at expiry, re-let, sell in 2036",
    "S6_hold_to_2040": "Hold the asset through 2040 and never sell",
}


# --------------------------------------------------------------------------- Monte Carlo
def monte_carlo(strategy, trials=10000, seed=SEED, expiry=2032):
    rng = random.Random(seed + zlib.crc32(strategy.encode()) % 100000)
    out = []
    for _ in range(trials):
        g = max(-0.03, rng.gauss(A["A1"], A["A18"]))
        cap_shift = rng.gauss(0, A["A19"] * math.sqrt(HORIZON - YEAR0))
        local = strategy
        if strategy in ("S3_hold_to_expiry_renew_then_sell", "S4_extend_then_sell"):
            if rng.random() > A["A13"]:
                local = "S5_expire_no_renewal"
        impaired = rng.random() < 0.04
        r = run_strategy(local, "Base", expiry=expiry, growth=g, cap_shift=cap_shift, impaired=impaired)
        out.append(r["terminal_after_tax"])
    out.sort()
    n = len(out)
    mean = statistics.fmean(out)
    p05 = out[int(0.05 * n)]
    p50 = out[n // 2]
    p95 = out[int(0.95 * n) - 1]

    def utility(w):
        g = A["A21"]
        return (w ** (1 - g)) / (1 - g) if g != 1 else math.log(max(w, 1))

    mean_utility = statistics.fmean(utility(max(w, 1.0)) for w in out)
    ce = (mean_utility * (1 - A["A21"])) ** (1 / (1 - A["A21"]))
    value_now = NOI0 / (A["A3"] + term_premium(max(0, expiry - YEAR0)))
    return {"trials": trials, "seed": seed, "mean": round(mean, 2), "p05": round(p05, 2),
            "p50": round(p50, 2), "p95": round(p95, 2),
            "certainty_equivalent": round(ce, 2),
            "multiple_of_value_now": round(mean / value_now, 2),
            "value_now": round(value_now, 2)}


# --------------------------------------------------------------------------- sensitivity
def sensitivity(strategy, expiry=2032):
    grid = []
    for label, kwargs in [
        ("Expiry 2030 (earliest)", {"expiry": 2030}),
        ("Expiry 2032 (midpoint)", {"expiry": 2032}),
        ("Expiry 2035 (latest)", {"expiry": 2035}),
        ("Cap rate -50 bp", {"cap_shift": -0.005}),
        ("Cap rate +50 bp", {"cap_shift": +0.005}),
        ("NOI growth 1.0%", {"growth": 0.010}),
        ("NOI growth 3.0%", {"growth": 0.030}),
    ]:
        r = run_strategy(strategy, "Base", **kwargs)
        grid.append({"case": label, "terminal_after_tax": r["terminal_after_tax"], "npv": r["npv"]})
    return grid


# --------------------------------------------------------------------------- main
def main():
    expiry = 2032
    strategies = {}
    for sid in STRATEGY_LABELS:
        scenarios = {}
        for scen in SCENARIOS:
            scenarios[scen] = run_strategy(sid, scen, expiry=expiry)
        mc = monte_carlo(sid, expiry=expiry)
        strategies[sid] = {
            "label": STRATEGY_LABELS[sid],
            "deterministic": scenarios,
            "monte_carlo": mc,
            "sensitivity": sensitivity(sid, expiry=expiry),
        }

    ranking = sorted(strategies.items(), key=lambda kv: kv[1]["monte_carlo"]["certainty_equivalent"],
                     reverse=True)

    # Breakeven: how far can the base cap rate fall before "sell now" wins on certainty equivalent?
    breakeven = []
    for shift in [-0.010, -0.005, 0.0, 0.005, 0.010]:
        s1 = run_strategy("S1_sell_now_1031", "Base", expiry=expiry, cap_shift=shift)
        s4 = run_strategy("S4_extend_then_sell", "Base", expiry=expiry, cap_shift=shift)
        breakeven.append({"cap_shift_bp": int(shift * 10000),
                          "sell_now": s1["terminal_after_tax"],
                          "extend_then_sell": s4["terminal_after_tax"],
                          "advantage_of_extend": round(s4["terminal_after_tax"] - s1["terminal_after_tax"], 2)})

    # Robustness: the recommendation must survive the assumptions being wrong.
    robustness = []
    for label, sid, kw in [
        ("Hold-to-expiry plan with a 10% rent cut on renewal",
         "S3_hold_to_expiry_renew_then_sell", {"growth": 0.020}),
        ("Hold-to-expiry plan, expiry at the 2035 end of the window",
         "S3_hold_to_expiry_renew_then_sell", {"expiry": 2035}),
        ("Hold-to-expiry plan, expiry at the 2030 end of the window",
         "S3_hold_to_expiry_renew_then_sell", {"expiry": 2030}),
        ("Extend-then-sell with no rent increase on extension",
         "S4_extend_then_sell", {"growth": 0.010}),
        ("Sell now, replacement portfolio only yields 6.0%",
         "S1_sell_now_1031", {"reinvest_cap": 0.060}),
        ("Sell now, replacement portfolio yields 7.5%",
         "S1_sell_now_1031", {"reinvest_cap": 0.075}),
        ("Sell now, cap rates 50 bp higher (weaker pricing)",
         "S1_sell_now_1031", {"cap_shift": 0.005}),
        ("Sell now, cap rates 50 bp lower (stronger pricing)",
         "S1_sell_now_1031", {"cap_shift": -0.005}),
    ]:
        if sid == "S3_hold_to_expiry_renew_then_sell" and "rent cut" in label:
            # a 10% reset is modelled by overriding the rent factor via a temporary assumption
            saved = A["A14"]
            A["A14"] = -0.10
            r = run_strategy(sid, "Base", **kw)
            A["A14"] = saved
        else:
            r = run_strategy(sid, "Base", **kw)
        base = run_strategy(sid, "Base", expiry=expiry)["terminal_after_tax"]
        robustness.append({"case": label, "strategy": sid,
                           "terminal_after_tax": r["terminal_after_tax"], "npv": r["npv"],
                           "deterministic_base": base,
                           "delta_vs_base": round(r["terminal_after_tax"] - base, 2)})

    out = {
        "meta": {
            "generated_by": "session-6ad87c21/scripts/model.py",
            "seed": SEED,
            "horizon": f"{YEAR0}-{HORIZON}",
            "normalisation": "All figures are per $100,000 of in-place annual NOI.",
            "access_date": "2026-11-08",
            "engine_version": "1.0",
        },
        "assumptions": ASSUMPTIONS,
        "scenarios": SCENARIOS,
        "expiry_used": expiry,
        "strategies": strategies,
        "ranking_by_certainty_equivalent": [
            {"rank": i + 1, "strategy": sid, "label": v["label"],
             "certainty_equivalent": v["monte_carlo"]["certainty_equivalent"],
             "p05": v["monte_carlo"]["p05"], "mean": v["monte_carlo"]["mean"]}
            for i, (sid, v) in enumerate(ranking)
        ],
        "breakeven": breakeven,
        "robustness": robustness,
        "checked_inputs": {
            "ten_year_treasury_2026_11_06": 0.0486,
            "cpi_u_los_angeles_sep_2026": 0.037,
            "eci_los_angeles_csa_sep_2026": 0.039,
            "measure_ula_threshold_2026": 5_400_000,
            "prop_13_levy": 0.01,
            "prop_13_cap": 0.02,
        },
    }

    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    path = os.path.join(ROOT, "data", "model_output.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
        fh.write("\n")

    print(f"wrote {path}")
    print(f"{'strategy':52s} {'CE':>12s} {'P05':>12s} {'mean':>12s}")
    for row in out["ranking_by_certainty_equivalent"]:
        print(f"{row['label'][:52]:52s} {row['certainty_equivalent']:12,.0f} {row['p05']:12,.0f} "
              f"{row['mean']:12,.0f}")
    print("\nbreakeven (extend-then-sell minus sell-now):")
    for b in breakeven:
        print(f"  cap {b['cap_shift_bp']:+5d} bp  {b['advantage_of_extend']:+,.0f}")


if __name__ == "__main__":
    main()
