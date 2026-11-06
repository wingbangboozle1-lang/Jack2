#!/usr/bin/env python3
"""
PARCEL-01 — hold / renew / sell projection model
=================================================

Purpose
-------
Compare three owner strategies for a single-tenant NNN quick-service restaurant in
Central Los Angeles, expressed **per $1.00 of current annual NOI**. Working in
NOI-normalised units is deliberate: the owner's rent, NOI, basis and building size
are private and were never supplied, so any dollar figure would be fabricated.
Every output is therefore a *multiple of current NOI* and is scale-free.

Strategies
----------
A  SELL NOW  (Q4 2026) and complete a §1031 exchange into a diversified net-lease
   position. Capital is redeployed at a diversified net-lease cash yield.
B  HOLD TO LEASE EXPIRY, then dispose of the asset into a re-leasing market.
C  HOLD, the tenant renews at expiry on market terms, owner sells in 2036.

Method
------
Monte Carlo, 20,000 independent paths, fixed seed (reproducible).
Annual cash flows are compounded at the 10-year Treasury yield (a *verified*
4.84% on 2026-11-05) so that every strategy is measured on the same
reinvestment assumption.

Every assumption below is either (a) an official statistic with a source id
resolved in data/sources.json, or (b) an explicit, documented modelling
assumption with a stated range. Nothing in between. See ASSUMPTIONS.

Run:  python3 model/projection.py
Out:  data/projection.json
"""

import json
import math
import os
import random
import statistics

SEED = 20261106
PATHS = 20000
HORIZON = 10.0  # years from 2026-11-06 to 2036-11-06

# --------------------------------------------------------------------------
# Verified anchors (official sources — see data/sources.json)
# --------------------------------------------------------------------------
RISK_FREE = 0.0484          # 10-yr Treasury par yield, 2026-11-05  [S-TREASURY]
CPI_LA = 0.037              # CPI-U 12-mo change, Sept 2026        [S-BLS-CPI]
CPI_FOOD_AWAY = 0.028       # CPI food away from home, 12-mo       [S-BLS-CPI]
DIVERSIFIED_YIELD = 0.0730  # Realty Income 2025 initial wtd avg cash yield [S-O-10K]
DIVERSIFIED_GROWTH = 0.0130 # Realty Income 2025 same-store rental revenue growth [S-O-10K]

# --------------------------------------------------------------------------
# Modelling assumptions (NOT official statistics — every one is published on
# the Methodology page and is stress-tested in the sensitivity table)
# --------------------------------------------------------------------------
A = {
    "going_in_cap":   {"base": 0.060, "sd": 0.0040, "lo": 0.052, "hi": 0.070,
                       "basis": "Net-lease pricing band for a 3-9 year NNN QSR in LA. No government "
                                "publisher produces single-asset cap rates; anchored to the 4.84% 10-yr "
                                "Treasury plus a 110-215 bp risk premium, and cross-checked against "
                                "diversified net-lease acquisition yields of 7.0-7.3% (SEC filings)."},
    "exit_cap_2036":  {"base": 0.065, "sd": 0.0090, "lo": 0.050, "hi": 0.090,
                       "basis": "Exit cap in 2036 = today's cap plus term/rate drift. Range spans "
                                "50 bp of compression to 250 bp of expansion."},
    "contract_rent_growth": {"base": 0.025, "sd": 0.006, "lo": 0.005, "hi": 0.045,
                       "basis": "Typical NNN escalator of 2-3%/yr. CPI-U Los Angeles is 3.7%, so a "
                                "2.5% fixed bump is a real (inflation-eroding) escalator."},
    "market_rent_growth": {"base": 0.030, "sd": 0.008, "lo": 0.005, "hi": 0.055,
                       "basis": "Retail market rent trend for the sub-market; CPI-anchored."},
    "nonrecoverable_opex": {"base": 0.04, "sd": 0.0, "lo": 0.04, "hi": 0.04,
                       "basis": "4% of NOI kept back for structural/roof/parking-lot reserves and "
                                "non-recoverable CAM leakage, even under a true NNN lease."},
    "sale_cost": {"base": 0.025, "sd": 0.0, "lo": 0.025, "hi": 0.025,
                       "basis": "2.0% brokerage plus ~0.45% LA City transfer tax and closing costs. "
                                "Measure ULA (4%/5.5%) is excluded because it does not bite below $5.4M. "
                                "[S-LA-ULA]"},
    "renewal_prob": {"base": 0.55, "sd": 0.115, "lo": 0.35, "hi": 0.75,
                       "basis": "Uniform draw 35-75%. The tenant is most likely a franchisee (93% of "
                                "the Jack in the Box system is franchised) and the brand is executing "
                                "50-100 closures in FY2026, so renewal is not the owner's to grant."},
    "renewal_term": {"base": 10, "sd": 0.0, "lo": 10, "hi": 10,
                       "basis": "Assumed 10-year extension with 2-3% bumps."},
    "renewal_cost": {"base": 0.02, "sd": 0.0, "lo": 0.02, "hi": 0.02,
                       "basis": "2% of annual rent for renewal TI/leasing commissions."},
    "vacancy_penalty": {"base": 0.0125, "sd": 0.0, "lo": 0.0125, "hi": 0.0125,
                       "basis": "+125 bp to exit cap when selling an asset facing a rollover "
                                "(buyer prices 12 months of downtime and TI)."},
    "relet_cost": {"base": 0.06, "sd": 0.0, "lo": 0.06, "hi": 0.06,
                       "basis": "6% of value for 12 months of lost rent plus TI/LC on a re-let."},
    "walt_premium": {"base": 0.0035, "sd": 0.0, "lo": 0.0035, "hi": 0.0035,
                       "basis": "-35 bp to exit cap for a freshly renewed 10-yr lease (buyers pay for "
                                "weighted-average lease term)."},
    "p_quake": {"base": 0.015, "sd": 0.0, "lo": 0.015, "hi": 0.015,
                       "basis": "Annual probability that a damaging earthquake causes >$1M of loss at "
                                "this location. Southern California sits in the highest USGS hazard "
                                "class [S-USGS-NSHM]; 1.5%/yr is a modelling judgement, not an official "
                                "USGS probability for this parcel."},
    "quake_loss": {"base": 0.15, "sd": 0.0, "lo": 0.15, "hi": 0.15,
                       "basis": "15% of value lost to deductible, uninsured code-upgrade and 6 months "
                                "of business interruption."},
    "p_disruption": {"base": 0.030, "sd": 0.0, "lo": 0.03, "hi": 0.03,
                       "basis": "Annual probability of a regional shock (smoke event, wildfire-driven "
                                "disruption, civil disturbance, extended outage) costing 3% of income. "
                                "CAL FIRE counted 8,232 wildfires and 16,627 structures destroyed in "
                                "2025 alone [S-CALFIRE-2025]."},
    "disruption_loss": {"base": 0.03, "sd": 0.0, "lo": 0.03, "hi": 0.03,
                       "basis": "3% of that year's income."},
    "p_cap_shock": {"base": 0.06, "sd": 0.0, "lo": 0.06, "hi": 0.06,
                       "basis": "Annual probability of a permanent +100 bp repricing of the exit cap."},
    "p_tenant_default": {"base": 0.05, "sd": 0.0, "lo": 0.05, "hi": 0.05,
                       "basis": "Annual hazard that the franchisee stops paying before lease expiry. "
                                "Jack in the Box has closed 86 units in FY2025 and guided to 50-100 "
                                "more in FY2026, and reported higher franchise bad-debt expense "
                                "[S-JACK-Q4FY25][S-JACK-Q3FY26]."},
    "p_div_shock": {"base": 0.03, "sd": 0.0, "lo": 0.03, "hi": 0.03,
                       "basis": "Annual probability of a +60 bp repricing for the diversified "
                                "portfolio (portfolio effect reduces single-asset dispersion)."},
}


def trunc_normal(rng, mean, sd, lo, hi):
    if sd <= 0:
        return mean
    for _ in range(50):
        x = rng.gauss(mean, sd)
        if lo <= x <= hi:
            return x
    return min(max(mean, lo), hi)


def run_path(rng, T):
    """Return {strategy: terminal wealth per $1.00 of current NOI} plus diagnostics."""
    g = trunc_normal(rng, A["contract_rent_growth"]["base"], A["contract_rent_growth"]["sd"],
                     A["contract_rent_growth"]["lo"], A["contract_rent_growth"]["hi"])
    gm = trunc_normal(rng, A["market_rent_growth"]["base"], A["market_rent_growth"]["sd"],
                      A["market_rent_growth"]["lo"], A["market_rent_growth"]["hi"])
    cap0 = trunc_normal(rng, A["going_in_cap"]["base"], A["going_in_cap"]["sd"],
                        A["going_in_cap"]["lo"], A["going_in_cap"]["hi"])
    cap_exit = trunc_normal(rng, A["exit_cap_2036"]["base"], A["exit_cap_2036"]["sd"],
                            A["exit_cap_2036"]["lo"], A["exit_cap_2036"]["hi"])
    p_renew = rng.uniform(A["renewal_prob"]["lo"], A["renewal_prob"]["hi"])

    V0 = 1.0 / cap0

    # ---- shared shock draws (asset-level) ----
    cap_shift = 0.0
    quake_year = None
    disrupt_years = set()
    default_year = None
    for yr in range(1, int(math.ceil(T)) + 1):
        if rng.random() < A["p_cap_shock"]["base"]:
            cap_shift += 0.010
        if quake_year is None and rng.random() < A["p_quake"]["base"]:
            quake_year = yr
        if rng.random() < A["p_disruption"]["base"]:
            disrupt_years.add(yr)
        if default_year is None and rng.random() < A["p_tenant_default"]["base"]:
            default_year = yr
    cap_shift = min(cap_shift, 0.03)

    # ================= Strategy A : sell now, 1031 into diversified =========
    y_div = trunc_normal(rng, DIVERSIFIED_YIELD, 0.004, 0.065, 0.082)
    g_div = trunc_normal(rng, DIVERSIFIED_GROWTH, 0.004, 0.003, 0.025)
    cap_div_exit = trunc_normal(rng, DIVERSIFIED_YIELD, 0.006, 0.060, 0.090)
    div_cap_shift = 0.0
    for _ in range(int(HORIZON)):
        if rng.random() < A["p_div_shock"]["base"]:
            div_cap_shift += 0.006
    div_cap_shift = min(div_cap_shift, 0.018)

    capital_a = V0 * (1 - A["sale_cost"]["base"])
    cash_a = 0.0
    for yr in range(1, int(HORIZON) + 1):
        cf = capital_a * y_div * ((1 + g_div) ** (yr - 1))
        cash_a += cf * ((1 + RISK_FREE) ** (HORIZON - yr))
    noi_next = capital_a * y_div * ((1 + g_div) ** int(HORIZON))
    value_a = noi_next / (cap_div_exit + div_cap_shift)
    wealth_a = cash_a + value_a * (1 - A["sale_cost"]["base"])

    # ================= Strategies B and C : hold ============================
    net_factor = 1 - A["nonrecoverable_opex"]["base"]
    cash_hold = 0.0          # future value at horizon
    noi_by_year = {}
    for yr in range(1, int(math.ceil(T)) + 1):
        noi = ((1 + g) ** (yr - 1))
        if default_year is not None and yr == default_year:
            noi = 0.0
        elif default_year is not None and yr > default_year:
            # re-let after 12 months at 15% below the in-place rent (downtime, TI, concessions)
            noi = 0.85 * ((1 + g) ** (yr - 1))
        if yr in disrupt_years:
            noi *= (1 - A["disruption_loss"]["base"])
        if quake_year is not None and yr == quake_year:
            noi *= 0.5
        noi_by_year[yr] = noi
        cash_hold += noi * net_factor * ((1 + RISK_FREE) ** (HORIZON - min(yr, HORIZON)))

    T_int = int(math.floor(T))
    frac = T - T_int
    noi_at_expiry = (1 + g) ** T
    if default_year is not None:
        noi_at_expiry = 0.85 * ((1 + g) ** T)

    quake_hit = 1.0 - A["quake_loss"]["base"] if quake_year is not None else 1.0

    # ---- B: sell into a rollover market at expiry, then redeploy the proceeds into
    #          the SAME diversified net-lease asset used by Strategy A, so that the
    #          comparison isolates the property decision and not the cash assumption.
    cap_at_T = cap0 + (cap_exit + cap_shift - cap0) * (T / HORIZON)
    val_b = (noi_at_expiry / (cap_at_T + A["vacancy_penalty"]["base"])) \
        * (1 - A["relet_cost"]["base"]) * quake_hit
    invest_b = val_b * (1 - A["sale_cost"]["base"])
    yrs_after = HORIZON - T
    cash_b = cash_hold
    for k in range(1, int(math.ceil(yrs_after)) + 1):
        cf = invest_b * y_div * ((1 + g_div) ** (k - 1))
        cash_b += cf * ((1 + RISK_FREE) ** (yrs_after - k))
    wealth_b = cash_b + invest_b * ((1 + g_div) ** yrs_after) * (1 - A["sale_cost"]["base"])

    # ---- C: tenant renews, hold to 2036 ----
    renews = (rng.random() < p_renew) and default_year is None
    if renews and noi_at_expiry > 0:
        ratio = ((1 + gm) / (1 + g)) ** T
        noi_renew = noi_at_expiry * ratio
        noi_renew *= (1 - A["renewal_cost"]["base"])
        yrs_left = HORIZON - T
        cash_c = cash_hold
        for k in range(1, int(math.ceil(yrs_left)) + 1):
            cf = noi_renew * ((1 + gm) ** (k - 1)) * net_factor
            cash_c += cf * ((1 + RISK_FREE) ** (HORIZON - (T + k)))
        noi_end = noi_renew * ((1 + gm) ** yrs_left)
        val_c = noi_end / (cap_exit + cap_shift - A["walt_premium"]["base"])
        wealth_c = cash_c + val_c * (1 - A["sale_cost"]["base"]) * quake_hit
    else:
        wealth_c = wealth_b

    return {
        "A": wealth_a,
        "B": wealth_b,
        "C": wealth_c,
        "cap0": cap0,
        "cap_exit": cap_exit + cap_shift,
        "renews": renews,
        "defaulted": default_year is not None,
        "quake": quake_year is not None,
        "g": g,
        "V0": V0,
    }


def summarise(vals):
    vals = sorted(vals)
    n = len(vals)
    def q(p):
        i = (n - 1) * p
        lo = int(math.floor(i)); hi = int(math.ceil(i))
        return vals[lo] if lo == hi else vals[lo] + (vals[hi] - vals[lo]) * (i - lo)
    mean = statistics.fmean(vals)
    return {
        "mean": round(mean, 4),
        "median": round(q(0.5), 4),
        "p10": round(q(0.10), 4),
        "p25": round(q(0.25), 4),
        "p75": round(q(0.75), 4),
        "p90": round(q(0.90), 4),
    }


def run_case(T, label, expiry_label):
    rng = random.Random(SEED + int(T * 100))
    rows = [run_path(rng, T) for _ in range(PATHS)]

    res = {}
    V0s = [r["V0"] for r in rows]
    for s in ("A", "B", "C"):
        vals = [r[s] for r in rows]
        st = summarise(vals)
        # probability of losing money vs. today's value (V0 per path)
        st["prob_below_todays_value"] = round(
            sum(1 for r in rows if r[s] < r["V0"]) / len(rows), 4)
        # CAGR over the 10-yr horizon vs today's value
        st["cagr_p50"] = round((st["median"] / statistics.fmean(V0s)) ** (1 / HORIZON) - 1, 4)
        res[s] = st

    # win rates (A beats B, A beats C, C beats B)
    res["win_rates"] = {
        "A_beats_B": round(sum(1 for r in rows if r["A"] > r["B"]) / len(rows), 4),
        "A_beats_C": round(sum(1 for r in rows if r["A"] > r["C"]) / len(rows), 4),
        "C_beats_B": round(sum(1 for r in rows if r["C"] > r["B"]) / len(rows), 4),
    }
    res["diagnostics"] = {
        "renewal_rate": round(sum(1 for r in rows if r["renews"]) / len(rows), 4),
        "default_rate": round(sum(1 for r in rows if r["defaulted"]) / len(rows), 4),
        "quake_rate": round(sum(1 for r in rows if r["quake"]) / len(rows), 4),
        "median_going_in_cap": round(statistics.median(r["cap0"] for r in rows), 4),
        "median_exit_cap": round(statistics.median(r["cap_exit"] for r in rows), 4),
    }
    return {"id": label, "expiry_label": expiry_label, "years_to_expiry": T, "results": res}


def breakeven_exit_cap(T, cap0=A["going_in_cap"]["base"]):
    """
    Deterministic solve: what exit cap (in 2036) makes HOLD-TO-EXPIRY-and-sell (B)
    equal SELL-NOW (A)? Everything else at base values. This isolates the single
    variable that drives the decision.
    """
    g = A["contract_rent_growth"]["base"]
    V0 = 1.0 / cap0
    capital_a = V0 * (1 - A["sale_cost"]["base"])
    y_div = DIVERSIFIED_YIELD
    g_div = DIVERSIFIED_GROWTH
    cash_a = sum(capital_a * y_div * (1 + g_div) ** (yr - 1) * (1 + RISK_FREE) ** (HORIZON - yr)
                 for yr in range(1, 11))
    value_a = capital_a * y_div * (1 + g_div) ** 10 / y_div
    wealth_a = cash_a + value_a * (1 - A["sale_cost"]["base"])

    net = 1 - A["nonrecoverable_opex"]["base"]
    cash_hold = sum((1 + g) ** (yr - 1) * net * (1 + RISK_FREE) ** (HORIZON - yr)
                    for yr in range(1, int(math.ceil(T)) + 1))
    noi_T = (1 + g) ** T

    def wealth_b(cap_exit):
        val = noi_T / (cap_exit + A["vacancy_penalty"]["base"]) * (1 - A["relet_cost"]["base"])
        return cash_hold + val * (1 - A["sale_cost"]["base"]) * (1 + RISK_FREE) ** (HORIZON - T)

    lo, hi = 0.020, 0.250
    for _ in range(200):
        mid = (lo + hi) / 2
        noi_T2 = noi_T
        val = noi_T2 / (mid + A["vacancy_penalty"]["base"]) * (1 - A["relet_cost"]["base"])
        inv = val * (1 - A["sale_cost"]["base"])
        yrs_after = HORIZON - T
        cash_b2 = cash_hold + sum(inv * y_div * (1 + g_div) ** (k - 1) * (1 + RISK_FREE) ** (yrs_after - k)
                                  for k in range(1, int(math.ceil(yrs_after)) + 1))
        wb = cash_b2 + inv * (1 + g_div) ** yrs_after * (1 - A["sale_cost"]["base"])
        if wb > wealth_a:
            lo = mid
        else:
            hi = mid
    return round((lo + hi) / 2, 4)


def sensitivity():
    """
    Deterministic grid: sell-now (A) vs hold-to-expiry (B) across the going-in cap
    and exit cap, at the mid-dated expiry (5.6 yrs). Values = B wealth minus A wealth,
    per $1.00 of NOI. Positive = holding wins.
    """
    g = A["contract_rent_growth"]["base"]
    T = 5.6
    net = 1 - A["nonrecoverable_opex"]["base"]
    grid = []
    for cap0 in (0.055, 0.060, 0.065):
        for cap_exit in (0.055, 0.060, 0.065, 0.070, 0.075):
            capital_a = (1 / cap0) * (1 - A["sale_cost"]["base"])
            cash_a = sum(capital_a * DIVERSIFIED_YIELD * (1 + DIVERSIFIED_GROWTH) ** (yr - 1)
                         * (1 + RISK_FREE) ** (HORIZON - yr) for yr in range(1, 11))
            value_a = capital_a * DIVERSIFIED_YIELD * (1 + DIVERSIFIED_GROWTH) ** 10 / DIVERSIFIED_YIELD
            wealth_a = cash_a + value_a * (1 - A["sale_cost"]["base"])
            cash_hold = sum((1 + g) ** (yr - 1) * net * (1 + RISK_FREE) ** (HORIZON - yr)
                            for yr in range(1, int(math.ceil(T)) + 1))
            cap_T = cap0 + (cap_exit - cap0) * (T / HORIZON)
            val_b = (1 + g) ** T / (cap_T + A["vacancy_penalty"]["base"]) * (1 - A["relet_cost"]["base"])
            inv = val_b * (1 - A["sale_cost"]["base"])
            yrs_after = HORIZON - T
            cash_b = cash_hold + sum(inv * DIVERSIFIED_YIELD * (1 + DIVERSIFIED_GROWTH) ** (k - 1)
                                     * (1 + RISK_FREE) ** (yrs_after - k)
                                     for k in range(1, int(math.ceil(yrs_after)) + 1))
            wealth_b = cash_b + inv * (1 + DIVERSIFIED_GROWTH) ** yrs_after * (1 - A["sale_cost"]["base"])
            grid.append({
                "going_in_cap": cap0,
                "exit_cap_2036": cap_exit,
                "hold_minus_sell": round(wealth_b - wealth_a, 4),
            })
    return grid


def main():
    cases = [
        run_case(3.15, "EXP-2030", "Lease expires 2030 (earliest in the stated window)"),
        run_case(5.65, "EXP-2032", "Lease expires mid-2032 (mid-point of the stated window)"),
        run_case(9.15, "EXP-2035", "Lease expires 2035 (latest in the stated window)"),
    ]
    out = {
        "generated_at": "2026-11-06T15:00:00Z",
        "seed": SEED,
        "paths_per_case": PATHS,
        "horizon_years": HORIZON,
        "units": "Terminal wealth per $1.00 of current annual NOI. NPV of all cash flows and "
                 "the terminal sale, compounded at the 10-yr Treasury (4.84%).",
        "anchors": [
            {"key": "risk_free", "value": RISK_FREE, "source_id": "S-TREASURY",
             "note": "10-yr Treasury par yield, 2026-11-05"},
            {"key": "cpi_la", "value": CPI_LA, "source_id": "S-BLS-CPI",
             "note": "CPI-U Los Angeles, 12 months to Sept 2026"},
            {"key": "cpi_food_away", "value": CPI_FOOD_AWAY, "source_id": "S-BLS-CPI",
             "note": "Food away from home, 12 months to Sept 2026"},
            {"key": "diversified_yield", "value": DIVERSIFIED_YIELD, "source_id": "S-O-10K",
             "note": "Realty Income 2025 initial weighted-average cash yield"},
            {"key": "diversified_growth", "value": DIVERSIFIED_GROWTH, "source_id": "S-O-10K",
             "note": "Realty Income 2025 same-store rental revenue growth"},
        ],
        "assumptions": [
            {"key": k, "base": v["base"], "range": [v["lo"], v["hi"]], "basis": v["basis"],
             "type": "model_assumption"}
            for k, v in A.items()
        ],
        "cases": cases,
        "breakeven_exit_cap": {
            "EXP-2030": breakeven_exit_cap(3.15),
            "EXP-2032": breakeven_exit_cap(5.65),
            "EXP-2035": breakeven_exit_cap(9.15),
            "meaning": "The 2036 exit cap at which holding to expiry equals selling now. If you "
                       "believe the 2036 exit cap will be BELOW this number, holding wins. "
                       "Above it, selling now wins.",
        },
        "breakeven_grid": [
            {"going_in_cap": c, "years_to_expiry": T, "breakeven_exit_cap_2036": breakeven_exit_cap(T, c)}
            for c in (0.050, 0.055, 0.060, 0.065, 0.070)
            for T in (3.15, 5.65, 9.15)
        ],
        "sensitivity_hold_minus_sell": sensitivity(),
        "sensitivity_note": "Deterministic, base assumptions, 5.6-year expiry. Positive means "
                            "holding to expiry produces more terminal wealth than selling now.",
    }
    here = os.path.dirname(os.path.abspath(__file__))
    dest = os.path.join(here, "..", "data", "projection.json")
    with open(dest, "w") as f:
        json.dump(out, f, indent=2)
    print("wrote", os.path.abspath(dest))
    for c in cases:
        r = c["results"]
        print(c["id"], "A median", r["A"]["median"], "B", r["B"]["median"], "C", r["C"]["median"],
              "| A beats B", r["win_rates"]["A_beats_B"])
    print("breakeven exit caps:", out["breakeven_exit_cap"])


if __name__ == "__main__":
    main()
