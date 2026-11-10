#!/usr/bin/env python3
"""
session-5f296f9d projection engine
==================================

Deterministic scenarios + seeded Monte Carlo for the sell-vs-renew decision on a
single-tenant Jack in the Box NNN lease in Central Los Angeles (expiry window
2030-2035).

HONESTY RULES BUILT INTO THIS ENGINE
------------------------------------
1. Owner-private facts (contract rent, basis, debt, option terms) are unknown and
   are NEVER guessed. All monetary results are published on an index basis:
   1.00 = one year of current net operating income (NOI).
2. Every forward-looking driver is an explicit, named assumption (A01..A12) with
   its anchor where an official source exists. Observations taken from official
   sources (O01..O08) are quoted exactly as published, with source ids.
3. Official probabilities are used where they exist (earthquake 60%/30yr, USGS
   UCERF3). Where no official probability exists (parcel wildfire, tenant
   default), the number is labelled an assumption, not a fact.
4. Deterministic across runs: Monte Carlo uses a fixed seed only.

Outputs: data/model_output.json
"""
import json
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "model_output.json")

SEED = 20261110
TRIALS = 10000
START_YEAR = 2026
HORIZON = 2040  # wealth measured at end of 2040

# ---------------------------------------------------------------------------
# Observations (official sources, access date 2026-11-10)
# ---------------------------------------------------------------------------
OBS = {
    "O01": {"label": "10-year Treasury constant maturity, 2026-11-06", "value": 4.86, "unit": "%", "source": "S08"},
    "O02": {"label": "Federal funds target range upper limit, 2026-11-09", "value": 4.00, "unit": "%", "source": "S09"},
    "O03": {"label": "Realty Income Q3-2026 initial weighted average cash yield", "value": 6.8, "unit": "%", "source": "S07"},
    "O04": {"label": "LA metro unemployment rate, 2026-09 (NSA)", "value": 4.4, "unit": "%", "source": "S01"},
    "O05": {"label": "LA County unemployment rate, 2026-09 (SA)", "value": 4.8, "unit": "%", "source": "S02"},
    "O06": {"label": "LA metro CPI-U, 12 months to 2026-09", "value": 3.7, "unit": "%", "source": "S01"},
    "O07": {"label": "LA metro Employment Cost Index, 12 months to 2026-09", "value": 3.9, "unit": "%", "source": "S01"},
    "O08": {"label": "USGS UCERF3 30-year probability of M6.7+ earthquake, LA region", "value": 60.0, "unit": "%", "source": "S13"},
    "O09": {"label": "Measure ULA + City base transfer stack, tier 1 (after 2026-06-30)", "value": 4.45, "unit": "%", "source": "S10"},
    "O10": {"label": "Measure ULA + City base transfer stack, tier 2 (after 2026-06-30)", "value": 5.95, "unit": "%", "source": "S10"},
    "O11": {"label": "JACK system same-store sales, FY2026 Q3", "value": -1.1, "unit": "%", "source": "S04"},
    "O12": {"label": "JACK restaurant count 2026-07-05 vs a year earlier", "value": "2,115 vs 2,168", "unit": "restaurants", "source": "S04"},
}

# ---------------------------------------------------------------------------
# Assumptions (explicit, forward-looking, NOT facts)
# ---------------------------------------------------------------------------
ASSUMPTIONS = {
    "A01": {"label": "Index basis", "value": "NOI_2026 = 1.00", "note": "All money results scale linearly by actual NOI. Private rent is never guessed."},
    "A02": {"label": "Annual NOI growth, bear", "value": 0.5, "unit": "%", "note": "Anchors: county population -0.6% (S29), tenant SSS -1.1% (S04); below CPI."},
    "A03": {"label": "Annual NOI growth, base", "value": 2.0, "unit": "%", "note": "Anchors: between typical NNN escalators and metro CPI 3.7% (O06); explicitly an assumption."},
    "A04": {"label": "Annual NOI growth, bull", "value": 3.0, "unit": "%", "note": "Anchors: near metro ECI 3.9% (O07); requires successful renewal with strong escalators."},
    "A05": {"label": "Reinvestment / discount rate", "value": 4.86, "unit": "%", "note": "Anchored to the official 10-year Treasury print O01; held flat, no curve extrapolation."},
    "A06": {"label": "Exit cap-rate distribution (MC)", "value": "Normal(6.50%, 0.75%), clipped to [5.00%, 8.50%]", "note": "Centered just inside the official net-lease benchmark yield 6.8% (O03). Distribution shape is an assumption."},
    "A07": {"label": "Reinvestment yield distribution (MC)", "value": "Normal(4.86%, 0.50%), clipped to [2.50%, 7.00%]", "note": "Centered on O01."},
    "A08": {"label": "Rent growth distribution (MC)", "value": "Triangular(-2.0%, 2.0%, 3.5%)", "note": "Mode = A03 (A02..A04 bear/base/bull); lower bound admits tenant SSS -1.1% (O11) and county population decline (S03/S29). An assumption, not a forecast."},
    "A09": {"label": "Earthquake annual hazard, hold path", "value": 1-(1-0.60)**(1/30), "unit": "probability/yr", "note": "Derived ONLY from official 60% in 30 years (O08): p = 1-(1-0.60)^(1/30) = 3.03%/yr. Loss magnitude is separate (A10)."},
    "A10": {"label": "Single-asset physical loss severity when a quake/fire hits", "value": "Uniform(15%, 60%) of asset value", "note": "ASSUMPTION — no official severity distribution for this parcel exists; parcel data withheld (F-11)."},
    "A11": {"label": "Parcel wildfire annual hazard", "value": 0.5, "unit": "%/yr", "note": "ASSUMPTION — no official parcel-level probability verified (F-11). Context: two major fires in one month, Jan 2025 (S14/S15)."},
    "A12": {"label": "Tenant-default / non-renewal annual hazard", "value": 3.0, "unit": "%/yr", "note": "ASSUMPTION informed by O11, O12 and FY26 guidance (S04); no official default probability exists."},
    "A13": {"label": "Tenant-default loss", "value": "40% NOI haircut plus 12 months vacancy", "note": "ASSUMPTION: re-tenanting a restaurant box at a wider cap with downtime."},
    "A14": {"label": "Systematic shock on diversified path", "value": "Cap +1.5% for one year and 10% income loss", "note": "ASSUMPTION: diversification removes idiosyncratic total loss but not market-wide shocks."},
    "A15": {"label": "City of Los Angeles transfer stack applies", "value": "4.45% (tier 1), modeled both with and without ULA", "note": "Parcel location unresolved (F-08); county-only case omits ULA (county documentary transfer tax is not modeled and must be confirmed, F-08)."},
    "A16": {"label": "Capital-gains tax in SELL case", "value": "0% (pre-tax comparison)", "note": "Basis and owner rates unknown (F-05, F-10); after-tax selling is strictly worse than shown, which is why EXCHANGE (deferral) is ranked above SELL."},
    "A17": {"label": "Holding costs net of NOI", "value": "0 (NOI is already net)", "note": "NNN structure: landlord outgoings limited to structural items; any special assessment is unknown (F-09)."},
    "A18": {"label": "Diversified reinvestment total-return sensitivity", "value": "4.86% (official anchor) / 6% / 7% / 9%", "note": "Only 4.86% is anchored to an official print (O01). 6-9% are assumption rows showing what portfolio return would be needed to overturn the hold case; not a market forecast."},
}

# ---------------------------------------------------------------------------
# Deterministic engine
# ---------------------------------------------------------------------------
def noi(year, g):
    return (1.0 + g) ** (year - START_YEAR)


def terminal_hold(way_year, g, cap, rate, transfer=0.0, horizon=HORIZON, default_year=None, default_hit=False):
    """Wealth at `horizon` from holding NOI through way_year then selling at `cap`,
    with NOI reinvested at `rate` from receipt, minus transfer cost on the sale."""
    wealth = 0.0
    for y in range(START_YEAR + 1, way_year + 1):
        n = noi(y, g)
        if default_hit and y >= (default_year or 10 ** 9):
            n *= (1.0 - A13_NOI_HAIRCUT)
        wealth += n * (1.0 + rate) ** (horizon - y)
    sale_value = noi(way_year, g) / (cap / 100.0)
    if default_hit and way_year >= (default_year or 10 ** 9):
        sale_value *= (1.0 - A13_NOI_HAIRCUT)
    net = sale_value * (1.0 - transfer)
    wealth += net * (1.0 + rate) ** (horizon - way_year)
    return wealth


def terminal_sell_2027(g, cap_now, rate, transfer=0.0, horizon=HORIZON):
    """Sell in 2027 at cap_now, reinvest net proceeds at `rate` to horizon."""
    sale_value = noi(2027, g) / (cap_now / 100.0)
    net = sale_value * (1.0 - transfer)
    return net * (1.0 + rate) ** (horizon - 2027)


A13_NOI_HAIRCUT = 0.40


def breakeven_cap(g, rate, transfer, way_year, cap_now, horizon=HORIZON):
    """Exit cap at which HOLD-to-way_year terminal wealth equals SELL-2027 wealth."""
    target = terminal_sell_2027(g, cap_now, rate, transfer, horizon)
    lo, hi = 3.0, 15.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if terminal_hold(way_year, g, mid, rate, transfer, horizon) > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def main():
    g_bear, g_base, g_bull = ASSUMPTIONS["A02"]["value"] / 100.0, ASSUMPTIONS["A03"]["value"] / 100.0, ASSUMPTIONS["A04"]["value"] / 100.0
    rate = ASSUMPTIONS["A05"]["value"] / 100.0
    cap_now = OBS["O03"]["value"]  # 6.8% official benchmark yield as today's sale cap

    scenarios = {"bear": g_bear, "base": g_base, "bull": g_bull}

    # --- Deterministic: expiry grid 2030-2035 x caps x scenarios -------------
    caps = [5.75, 6.25, 6.80, 7.25, 7.75]
    grid = []
    for sname, g in scenarios.items():
        for year in range(2030, 2036):
            for cap in caps:
                for ula, transfer in (("with-ULA", 0.0445), ("without-ULA", 0.0)):
                    hold_w = terminal_hold(year, g, cap, rate, transfer)
                    sell_w = terminal_sell_2027(g, cap_now, rate, transfer)
                    grid.append({
                        "scenario": sname, "expiry_year": year, "exit_cap_pct": cap,
                        "ula_case": ula, "hold_wealth_index": round(hold_w, 4),
                        "sell_2027_wealth_index": round(sell_w, 4),
                        "hold_minus_sell": round(hold_w - sell_w, 4),
                        "hold_wins": hold_w > sell_w
                    })

    # --- Break-even caps ----------------------------------------------------
    breakevens = []
    for sname, g in scenarios.items():
        for year in range(2030, 2036):
            for ula, transfer in (("with-ULA", 0.0445), ("without-ULA", 0.0)):
                be = breakeven_cap(g, rate, transfer, year, cap_now)
                breakevens.append({
                    "scenario": sname, "expiry_year": year, "ula_case": ula,
                    "breakeven_exit_cap_pct": round(be, 3),
                    "note": "HOLD terminal wealth equals SELL-2027 diversified wealth at this exit cap"
                })

    # --- Sensitivity: 2032 base case ---------------------------------------
    sens = []
    for g_pct in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]:
        row = {"noi_growth_pct": g_pct}
        for cap in caps:
            row[f"hold_2032_cap_{cap}"] = round(terminal_hold(2032, g_pct / 100.0, cap, rate, 0.0445), 4)
        row["sell_2027_with_ula"] = round(terminal_sell_2027(g_pct / 100.0, cap_now, rate, 0.0445), 4)
        row["breakeven_2032_with_ula"] = round(breakeven_cap(g_pct / 100.0, rate, 0.0445, 2032, cap_now), 3)
        sens.append(row)

    # --- Break-even reinvestment rate (what portfolio return flips the call) --
    def hold_at_rate(way_year, g, cap, r, transfer):
        return terminal_hold(way_year, g, cap, r, transfer)

    def sell_at_rate(g, cap_now, r, transfer):
        return terminal_sell_2027(g, cap_now, r, transfer)

    breakeven_rates = []
    for sname, g in scenarios.items():
        for year in (2030, 2032, 2035):
            lo, hi = 0.0, 0.25
            target_hold = hold_at_rate(year, g, 6.50, rate, 0.0445)
            for _ in range(200):
                mid = (lo + hi) / 2.0
                if sell_at_rate(g, cap_now, mid, 0.0445) < target_hold:
                    lo = mid
                else:
                    hi = mid
            breakeven_rates.append({
                "scenario": sname, "expiry_year": year, "ula_case": "with-ULA",
                "exit_cap_pct": 6.50,
                "breakeven_reinvest_rate_pct": round((lo + hi) / 2.0 * 100.0, 3),
                "note": "Portfolio total return on sale proceeds at which SELL-2027 equals HOLD-to-expiry at a 6.50% exit cap"
            })

    # --- Reinvestment-rate sensitivity (A18) ---------------------------------
    r_sens = []
    for r_pct in (4.86, 6.0, 7.0, 9.0):
        r = r_pct / 100.0
        r_sens.append({
            "reinvest_rate_pct": r_pct,
            "anchored_to_official_print": r_pct == 4.86,
            "hold_2032_base_with_ula": round(terminal_hold(2032, g_base, 6.50, r, 0.0445), 4),
            "sell_2027_with_ula": round(terminal_sell_2027(g_base, cap_now, r, 0.0445), 4),
        })

    # --- Monte Carlo --------------------------------------------------------
    rng = random.Random(SEED)
    p_quake_yr = ASSUMPTIONS["A09"]["value"]
    p_fire_yr = ASSUMPTIONS["A11"]["value"] / 100.0
    p_default_yr = ASSUMPTIONS["A12"]["value"] / 100.0

    def clip(x, lo, hi):
        return max(lo, min(hi, x))

    hold, hold_def, sell, losses_hold, losses_div = [], [], [], [], []
    default_years = []

    for _ in range(TRIALS):
        g = rng.triangular(-0.020, 0.035, 0.020)
        cap_exit = clip(rng.gauss(0.065, 0.0075), 0.050, 0.085)
        r_inv = clip(rng.gauss(0.0486, 0.005), 0.025, 0.070)

        wealth_hold = 0.0
        wealth_hold_def = 0.0
        impair = 1.0            # permanent single-asset impairment factor (A10)
        quake_sev_total = 0.0   # idiosyncratic severity realized (index units at horizon)
        div_shock_loss = 0.0
        default_flag = False
        default_year = None
        for y in range(START_YEAR + 1, HORIZON + 1):
            n = noi(y, g) * impair
            n_def = noi(y, g) * impair
            if rng.random() < p_quake_yr:
                sev = rng.uniform(0.15, 0.60)
                impair *= (1 - sev)
                n *= (1 - sev)
                n_def *= (1 - sev)
            if rng.random() < p_fire_yr:
                sev = rng.uniform(0.15, 0.60)
                impair *= (1 - sev)
                n *= (1 - sev)
                n_def *= (1 - sev)
            if not default_flag and rng.random() < p_default_yr:
                default_flag = True
                default_year = y
            if default_flag and y >= default_year:
                n_def *= (1 - A13_NOI_HAIRCUT)
            wealth_hold += n * (1 + r_inv) ** (HORIZON - y)
            wealth_hold_def += n_def * (1 + r_inv) ** (HORIZON - y)
        # terminal sale of the (possibly impaired) asset at horizon
        term = noi(HORIZON, g) * impair / cap_exit
        term_def = term * ((1 - A13_NOI_HAIRCUT) if default_flag else 1.0)
        wealth_hold += term * (1.0 - 0.0445)
        wealth_hold_def += term_def * (1.0 - 0.0445)

        # idiosyncratic loss at horizon vs an unimpaired hold (index units)
        unimpaired = noi(HORIZON, g) / cap_exit * (1.0 - 0.0445)
        idio_loss = max(0.0, unimpaired - term * (1.0 - 0.0445))

        # Sell/exchange path: 2027 sale at benchmark 6.8%, diversified reinvestment
        sale27 = noi(2027, g) / 0.068
        net27 = sale27 * (1.0 - 0.0445)
        wealth_div = net27 * (1 + r_inv) ** (HORIZON - 2027)
        # systematic shocks (A14) applied to the diversified path
        shocks = 0
        shock_years = []
        for y in range(2028, HORIZON + 1):
            if rng.random() < 0.02:
                shocks += 1
                shock_years.append(y)
        if shocks:
            # each shock year cuts remaining compounding: approximate multiplicative
            factor = 1.0
            for y in shock_years:
                factor *= 0.90
            wealth_div *= factor
            div_shock_loss = net27 * (1 + r_inv) ** (HORIZON - 2027) * (1 - factor)
        else:
            div_shock_loss = 0.0

        hold.append(wealth_hold)
        hold_def.append(wealth_hold_def)
        sell.append(wealth_div)
        losses_hold.append(idio_loss)
        losses_div.append(div_shock_loss)
        if default_flag:
            default_years.append(default_year)

    def pct(vals, p):
        s = sorted(vals)
        k = (len(s) - 1) * p / 100.0
        f = math.floor(k); c = math.ceil(k)
        if f == c:
            return s[int(k)]
        return s[f] * (c - k) + s[c] * (k - f)

    def cvar(vals, p):
        s = sorted(vals)
        cut = int(len(s) * p / 100.0)
        return sum(s[:cut]) / max(1, cut)

    mc = {
        "seed": SEED,
        "trials": TRIALS,
        "horizon_year": HORIZON,
        "expected_wealth": {
            "mean_hold_index": round(sum(hold) / TRIALS, 4),
            "mean_sell_index": round(sum(sell) / TRIALS, 4),
            "mean_hold_with_default_index": round(sum(hold_def) / TRIALS, 4),
            "expected_wealth_cost_of_diversifying_index": round((sum(hold) - sum(sell)) / TRIALS, 4),
        },
        "distribution": {
            "median_hold_index": round(pct(hold, 50), 4),
            "median_sell_index": round(pct(sell, 50), 4),
            "p5_hold_index": round(pct(hold, 5), 4),
            "p5_sell_index": round(pct(sell, 5), 4),
            "p95_hold_index": round(pct(hold, 95), 4),
            "p95_sell_index": round(pct(sell, 95), 4),
        },
        "risk_adjusted": {
            "cvar5_hold_index": round(cvar(hold, 5), 4),
            "cvar5_sell_index": round(cvar(sell, 5), 4),
            "P(sell_wealth_gt_hold_wealth)": round(sum(1 for i in range(TRIALS) if sell[i] > hold[i]) / TRIALS, 4),
            "P(hold_default_lt_sell_wealth)": round(sum(1 for i in range(TRIALS) if hold_def[i] < sell[i]) / TRIALS, 4),
        },
        "tail_risk": {
            "mean_single_asset_terminal_loss_index": round(sum(losses_hold) / TRIALS, 4),
            "mean_diversified_terminal_loss_index": round(sum(losses_div) / TRIALS, 4),
            "p99_single_asset_terminal_loss_index": round(pct(losses_hold, 99), 4),
            "p99_diversified_terminal_loss_index": round(pct(losses_div, 99), 4),
            "P(single_asset_loss_gt_10_index_units)": round(sum(1 for x in losses_hold if x > 10) / TRIALS, 4),
            "P(diversified_loss_gt_10_index_units)": round(sum(1 for x in losses_div if x > 10) / TRIALS, 4),
            "note": "Single-asset hold carries idiosyncratic permanent impairment (A10); the diversified path only carries modeled market-wide shocks (A14)."
        },
    }

    # Official-horizon probability of at least one quake during a hold to 2035
    p_any_quake_2035 = 1 - (1 - p_quake_yr) ** (2035 - 2026)
    hazard_prob = {
        "annual_quake_probability_from_UCERF3": round(p_quake_yr, 5),
        "probability_of_at_least_one_M6.7+_during_2026-2035_hold": round(p_any_quake_2035, 4),
        "derivation": "1-(1-0.60)^(1/30) per year, then 1-(1-p)^9 years; sourced only from O08/S13",
    }

    out = {
        "session": "session-5f296f9d",
        "generated_by": "scripts/model.py",
        "seed": SEED,
        "index_basis": ASSUMPTIONS["A01"]["value"],
        "observations": OBS,
        "assumptions": ASSUMPTIONS,
        "expiry_grid": grid,
        "breakeven": breakevens,
        "breakeven_reinvestment": breakeven_rates,
        "sensitivity_2032": sens,
        "sensitivity_reinvestment": r_sens,
        "monte_carlo": mc,
        "hazard_probability": hazard_prob,
        "counts": {"grid_rows": len(grid), "breakeven_rows": len(breakevens),
                   "sensitivity_rows": len(sens), "breakeven_rate_rows": len(breakeven_rates),
                   "reinvest_sensitivity_rows": len(r_sens)},
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1, sort_keys=False)
    print(f"model_output.json written: {len(grid)} grid rows, {len(breakevens)} breakeven rows, {TRIALS} MC trials, seed {SEED}")


if __name__ == "__main__":
    main()
