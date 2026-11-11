#!/usr/bin/env python3
"""Session N4 projection model - deterministic scenarios + seeded Monte Carlo.

Consistency rule: every strategy is compared as TERMINAL WEALTH at the common
horizon (2026 -> 2040), with every cash flow (rent, sale proceeds) reinvested at
the same accumulation rate w. No strategy is compared as PV against another as
terminal wealth.

Basis: every property-specific input the owner has not supplied (contract rent,
expiry, escalations, option terms, basis, debt) is an ILLUSTRATIVE ASSUMPTION,
clearly labelled below and restated in the output file. Verified market data
from data/metrics.json is loaded and referenced, never invented.

Index convention: outputs are per $1.00 of the subject's current annual NOI, so
no private rent number is required. A dollar display uses ASSUMED_NOI only for
Measure ULA tier tests.

Usage:  python3 scripts/model.py
Writes: data/model_output.json
"""
import json
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")

SEED = 20261111
TRIALS = 10000
HORIZON = 14  # 2026 -> 2040, common comparison horizon

# ---------------------------------------------------------------- assumptions
# Every value in this block is an ILLUSTRATIVE ASSUMPTION, not a measurement.
ASSUMPTIONS = {
    "ASSUMED_NOI": 250000.0,          # $/yr, ULA tier tests + dollar display only
    "c0_grid": [0.055, 0.060, 0.065, 0.070, 0.075],  # going-in cap scenarios
    "c1_grid": [0.055, 0.060, 0.065, 0.070, 0.075],  # exit cap scenarios
    "g_scenarios": {"low": 0.000, "base": 0.020, "high": 0.035},  # NOI growth p.a.
    "accumulation_rate_scenarios": {"low": 0.055, "base": 0.065, "high": 0.075},
    "extension_uplift_scenarios": {"flat": 0.00, "modest": 0.10, "strong": 0.25},
    "expiry_years_grid": [4, 5, 6, 7, 9],   # 2030-2035 window (2026 base year)
    "extension_term_grid": [5, 10],
    "transfer_costs": {
        "county_only": 0.0011,                     # verified 0.11% (S05)
        "in_city_tier1": 0.0011 + 0.0045 + 0.04,   # verified stack (S05, S06)
        "in_city_tier2": 0.0011 + 0.0045 + 0.055,
    },
    "replacement_yield_grid": [0.055, 0.065, 0.075],
    "mc_c0_mean": 0.065, "mc_c0_sd": 0.0075,       # ASSUMED cap-rate distribution
    "mc_g_mean": 0.020, "mc_g_sd": 0.015,          # ASSUMED NOI growth
    "mc_w_mean": 0.065, "mc_w_sd": 0.010,          # ASSUMED reinvestment yield
    "mc_exit_shock_p": 0.15, "mc_exit_shock_bp": 0.02,   # ASSUMED systemic widening
    "mc_quake_annual_p": 0.0303,  # from USGS UCERF3 60%/30yr (S16): 1-(0.4)^(1/30)
    "mc_quake_damage": 0.40,      # ASSUMED share of value/NOI lost if it hits here
    "mc_wildfire_annual_p": 0.005,  # ASSUMED - no official series for a dense central parcel
    "mc_wildfire_damage": 0.60,
    "mc_tenant_default_annual_p": 0.010,  # ASSUMED
    "mc_tenant_default_noi_loss": 0.40,   # ASSUMED during re-tenancy
    "mc_vacancy_years": 2.0,              # ASSUMED re-tenancy period
    "mc_do_nothing_cliff_penalty": 0.95,  # ASSUMED leakage from ignoring the WALT cliff
}


def annualize(prob30, years=30):
    return 1.0 - (1.0 - prob30) ** (1.0 / years)


def transfer_rate(price_usd, in_city):
    if not in_city:
        return ASSUMPTIONS["transfer_costs"]["county_only"]
    if price_usd >= 10_900_000:
        return ASSUMPTIONS["transfer_costs"]["in_city_tier2"]
    if price_usd > 5_400_000:
        return ASSUMPTIONS["transfer_costs"]["in_city_tier1"]
    return 0.0011 + 0.0045


def hold_flows(noi0, g, c1, n, in_city, uplift=1.0):
    """[(t, cash)] of NOI years 1..n plus net sale proceeds at n. Per $1 NOI0."""
    flows = []
    for t in range(1, n + 1):
        flows.append((t, noi0 * ((1.0 + g) ** t) * uplift))
    sale = (noi0 * ((1.0 + g) ** n) * uplift) / c1
    tr = transfer_rate(sale * ASSUMPTIONS["ASSUMED_NOI"], in_city)
    flows.append((n, sale * (1.0 - tr)))
    return flows


def terminal_wealth(flows, w, horizon=HORIZON):
    """All cash flows reinvested at w until the common horizon."""
    return sum(c * ((1.0 + w) ** (horizon - t)) for t, c in flows)


def sell_now_net(noi0, c0, in_city):
    p = noi0 / c0
    tr = transfer_rate(p * ASSUMPTIONS["ASSUMED_NOI"], in_city)
    return p * (1.0 - tr)


def wealth_sell(noi0, c0, w, in_city, horizon=HORIZON):
    return sell_now_net(noi0, c0, in_city) * ((1.0 + w) ** horizon)


# ------------------------------------------------------------ deterministic
def deterministic():
    A = ASSUMPTIONS
    g = A["g_scenarios"]["base"]
    w = A["accumulation_rate_scenarios"]["base"]
    out = {"unit": "terminal wealth at 2040 per $1.00 of current annual NOI"}

    # 1) Sell-now wealth across cap grid
    out["sell_now_wealth"] = {
        f"{c0:.3f}": {
            "county": round(wealth_sell(1.0, c0, w, False), 4),
            "in_city_tier2": round(wealth_sell(1.0, c0, w, True), 4),
        } for c0 in A["c0_grid"]
    }

    # 2) Hold-to-expiry wealth across expiry x exit cap
    out["hold_wealth_grid"] = []
    for n in A["expiry_years_grid"]:
        row = {"years_to_expiry": n, "by_exit_cap": {}}
        for c1 in A["c1_grid"]:
            row["by_exit_cap"][f"{c1:.3f}"] = {
                "county": round(terminal_wealth(hold_flows(1.0, g, c1, n, False), w), 4),
                "in_city_tier2": round(terminal_wealth(hold_flows(1.0, g, c1, n, True), w), 4),
            }
        out["hold_wealth_grid"].append(row)

    # 3) Extend-then-sell wealth
    out["extend_wealth_grid"] = []
    for e in A["extension_term_grid"]:
        for key, up in A["extension_uplift_scenarios"].items():
            for c1 in A["c1_grid"]:
                out["extend_wealth_grid"].append({
                    "extension_years": e, "uplift": key, "uplift_factor": 1.0 + up,
                    "exit_cap": c1,
                    "wealth_county": round(terminal_wealth(
                        hold_flows(1.0, g, c1, e, False, 1.0 + up), w), 4),
                    "wealth_in_city_tier2": round(terminal_wealth(
                        hold_flows(1.0, g, c1, e, True, 1.0 + up), w), 4),
                })

    # 4) Breakevens - all solved on the SAME terminal-wealth basis
    c0 = 0.065
    out["breakevens"] = {
        "basis": "terminal wealth at 2040, cash flows reinvested at w=6.5% (assumption), "
                 "going-in cap c0=6.5% (assumption), g=2% (assumption)",
        "exit_cap_hold_equals_sell_now": {},   # c1 where hold wealth == sell wealth
        "required_reinvest_yield_for_sell_now": {},  # w where sell==hold (hold cash at w too)
    }
    sell_w = wealth_sell(1.0, c0, w, False)
    for n in A["expiry_years_grid"]:
        # solve c1: hold(n, c1) == sell_now (both at w)
        lo, hi = 0.030, 0.160
        for _ in range(80):
            mid = (lo + hi) / 2.0
            hw = terminal_wealth(hold_flows(1.0, g, mid, n, False), w)
            if hw > sell_w:
                lo = mid          # higher cap (cheaper sale) would lower hold wealth
            else:
                hi = mid
        out["breakevens"]["exit_cap_hold_equals_sell_now"][str(n)] = round((lo + hi) / 2.0, 5)

        # solve w (same w for both branches): sell_now(w) == hold_flows(w)
        # Sell-now holds all cash from t=0, so its wealth grows faster in w:
        # above the crossing sell wins (sw > hw) -> move hi down, and vice versa.
        lo, hi = 0.001, 0.300
        for _ in range(80):
            mid = (lo + hi) / 2.0
            sw = wealth_sell(1.0, c0, mid, False)
            hw = terminal_wealth(hold_flows(1.0, g, 0.065, n, False), mid)
            if sw > hw:
                hi = mid
            else:
                lo = mid
        out["breakevens"]["required_reinvest_yield_for_sell_now"][str(n)] = round((lo + hi) / 2.0, 5)

    # capital-only closed-form check: (1+g)^n / c1 == 1/c0  =>  c1 = c0 * (1+g)^n
    # (pure price comparison, no rent, no transfer tax - sanity anchor only)
    out["breakevens"]["capital_only_closed_form_c1_equals_c0_times_growth"] = {
        str(n): round(c0 * ((1.0 + g) ** n), 5) for n in A["expiry_years_grid"]
    }

    # 5) verified anchors
    metrics = json.load(open(os.path.join(DATA, "metrics.json"), encoding="utf-8"))
    anchors = {r["id"]: {"metric": r["metric"], "value": r["value"], "source": r["source"]}
               for r in metrics["rows"] if r["id"] in
               ("N57", "N58", "N24", "N23", "N44", "N42", "N76", "N78", "N66", "N67")}
    out["verified_market_anchors"] = anchors
    out["official_hazard_inputs"] = {
        "usgs_ucerf3_la_m67_30yr": "60%",
        "implied_annual_rate": f"{annualize(0.60)*100:.2f}%",
        "source": "S16",
    }
    return out


# ------------------------------------------------------------ Monte Carlo
def monte_carlo():
    A = ASSUMPTIONS
    rng = random.Random(SEED)
    quake_annual = A["mc_quake_annual_p"]
    strat = ["SELL_NOW_1031", "HOLD_TO_EXPIRY", "EXTEND_THEN_SELL", "DO_NOTHING"]
    results = {s: [] for s in strat}
    best_counts = {s: 0 for s in strat}
    hazard_counts = {"quake": 0, "wildfire": 0, "tenant_default": 0, "exit_shock": 0}

    for _ in range(TRIALS):
        c0 = max(0.040, min(0.100, rng.gauss(A["mc_c0_mean"], A["mc_c0_sd"])))
        g = max(-0.02, min(0.06, rng.gauss(A["mc_g_mean"], A["mc_g_sd"])))
        w = max(0.02, min(0.12, rng.gauss(A["mc_w_mean"], A["mc_w_sd"])))
        in_city = rng.random() < 0.5          # parcel status unknown - flagged
        n = rng.choice(A["expiry_years_grid"])
        uplift = 1.0 + rng.choice(list(A["extension_uplift_scenarios"].values()))
        e = rng.choice(A["extension_term_grid"])

        # first-hit hazard years over the horizon
        quake_year = fire_year = tenant_year = None
        for yr in range(1, HORIZON + 1):
            if quake_year is None and rng.random() < quake_annual:
                quake_year = yr
            if fire_year is None and rng.random() < A["mc_wildfire_annual_p"]:
                fire_year = yr
            if tenant_year is None and rng.random() < A["mc_tenant_default_annual_p"]:
                tenant_year = yr
        if quake_year: hazard_counts["quake"] += 1
        if fire_year: hazard_counts["wildfire"] += 1
        if tenant_year: hazard_counts["tenant_default"] += 1

        exit_shock = rng.random() < A["mc_exit_shock_p"]
        if exit_shock: hazard_counts["exit_shock"] += 1
        c1 = max(0.035, c0 + rng.gauss(0.0, 0.005) + (A["mc_exit_shock_bp"] if exit_shock else 0.0))
        c1e = max(0.035, c0 + rng.gauss(0.0, 0.005) + (A["mc_exit_shock_bp"] if exit_shock else 0.0))

        def hazard_adjusted(t, x):
            if quake_year is not None and t >= quake_year:
                x *= (1.0 - A["mc_quake_damage"])
            if fire_year is not None and t >= fire_year:
                x *= (1.0 - A["mc_wildfire_damage"])
            return x

        def tenant_adjusted(t, x):
            if tenant_year is not None and tenant_year <= t <= tenant_year + int(A["mc_vacancy_years"]):
                x *= (1.0 - A["mc_tenant_default_noi_loss"])
            return x

        # branch 1: sell now (t=0), reinvest at w - no parcel hazard afterwards
        wealth_sell_v = wealth_sell(1.0, c0, w, in_city)

        # branch 2: hold to expiry n
        flows_h = []
        for t in range(1, n + 1):
            flows_h.append((t, tenant_adjusted(t, hazard_adjusted(t, (1.0 + g) ** t))))
        sale = (1.0 + g) ** n / c1
        if quake_year is not None and quake_year <= n:
            sale *= (1.0 - A["mc_quake_damage"])
        if fire_year is not None and fire_year <= n:
            sale *= (1.0 - A["mc_wildfire_damage"])
        if tenant_year is not None and n <= tenant_year + int(A["mc_vacancy_years"]):
            sale *= (1.0 - A["mc_tenant_default_noi_loss"])
        tr = transfer_rate(sale * A["ASSUMED_NOI"], in_city)
        flows_h.append((n, sale * (1.0 - tr)))
        wealth_hold_v = terminal_wealth(flows_h, w)

        # branch 3: extend e years at reset, then sell
        flows_e = []
        for t in range(1, e + 1):
            flows_e.append((t, tenant_adjusted(t, hazard_adjusted(t, (1.0 + g) ** t * uplift))))
        sale_e = (1.0 + g) ** e * uplift / c1e
        if quake_year is not None and quake_year <= e:
            sale_e *= (1.0 - A["mc_quake_damage"])
        if fire_year is not None and fire_year <= e:
            sale_e *= (1.0 - A["mc_wildfire_damage"])
        if tenant_year is not None and e <= tenant_year + int(A["mc_vacancy_years"]):
            sale_e *= (1.0 - A["mc_tenant_default_noi_loss"])
        tre = transfer_rate(sale_e * A["ASSUMED_NOI"], in_city)
        flows_e.append((e, sale_e * (1.0 - tre)))
        wealth_extend_v = terminal_wealth(flows_e, w)

        # branch 4: do nothing = hold, plus unmanaged-WALT-cliff leakage (assumption)
        wealth_dna_v = wealth_hold_v * A["mc_do_nothing_cliff_penalty"]

        vals = {"SELL_NOW_1031": wealth_sell_v, "HOLD_TO_EXPIRY": wealth_hold_v,
                "EXTEND_THEN_SELL": wealth_extend_v, "DO_NOTHING": wealth_dna_v}
        best_counts[max(vals, key=vals.get)] += 1
        for k, v in vals.items():
            results[k].append(v)

    def stats(xs):
        xs = sorted(xs)
        m = len(xs)
        mean = sum(xs) / m
        med = xs[m // 2] if m % 2 else (xs[m // 2 - 1] + xs[m // 2]) / 2
        p05 = xs[max(0, int(0.05 * m) - 1)]
        p95 = xs[min(m - 1, int(0.95 * m))]
        var = sum((x - mean) ** 2 for x in xs) / m
        return {"mean": round(mean, 4), "median": round(med, 4),
                "p05": round(p05, 4), "p95": round(p95, 4), "sd": round(math.sqrt(var), 4)}

    return {
        "seed": SEED, "trials": TRIALS, "horizon_years": HORIZON,
        "unit": "terminal wealth at 2040 per $1.00 of current annual NOI",
        "strategy_stats": {k: stats(v) for k, v in results.items()},
        "best_strategy_share": {k: round(v / TRIALS, 4) for k, v in best_counts.items()},
        "hazard_incidence_over_14y": {k: {"count": v, "share": round(v / TRIALS, 4)}
                                      for k, v in hazard_counts.items()},
        "tail_note": "P05 includes quake/wildfire/tenant-default draws for hold-like "
                     "branches; SELL_NOW leaves the parcel at t=0 but keeps cap and "
                     "reinvestment-rate uncertainty.",
    }


def main():
    det = deterministic()
    mc = monte_carlo()
    out = {
        "meta": {"model": "Session N4 (session-3090b9ed) sell-vs-renew projection",
                 "generated_by": "scripts/model.py", "seed": SEED, "trials": TRIALS,
                 "basis": "per $1 of current annual NOI; no owner-private value used"},
        "assumptions": ASSUMPTIONS,
        "assumption_warning": "EVERY entry in 'assumptions' is illustrative, not "
                              "verified. Verified anchors exist only in data/metrics.json "
                              "with status=verified. Property-specific facts stay blank "
                              "(N90, N91, N104).",
        "deterministic": det, "monte_carlo": mc,
    }
    path = os.path.join(DATA, "model_output.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, sort_keys=False)
    print(f"wrote {path}")
    print(f"  sell-now wealth (c0=6.5%, county): {det['sell_now_wealth']['0.065']['county']}")
    h7 = [r for r in det["hold_wealth_grid"] if r["years_to_expiry"] == 7][0]
    print(f"  hold wealth (n=7, c1=6.5%, county): {h7['by_exit_cap']['0.065']['county']}")
    print(f"  breakeven exit cap (n=7): {det['breakevens']['exit_cap_hold_equals_sell_now']['7']}")
    print(f"  breakeven reinvest yield (n=7): {det['breakevens']['required_reinvest_yield_for_sell_now']['7']}")
    print(f"  MC best-share: {mc['best_strategy_share']}")
    print(f"  MC stats: {mc['strategy_stats']}")


if __name__ == "__main__":
    main()
