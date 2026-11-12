#!/usr/bin/env python3
"""
Session P (session-7663f9db) Normalized Valuation & Dual-Regime Monte Carlo Model.

All dollar figures are normalized strictly per $1.00 of current NNN Net Operating Income (NOI),
because subject parcel rent, lease expiry date, tax basis, and appraisal are private/blank.

Live primary anchors verified 2026-11-12:
  - 10Y Treasury Par Yield (Nov 10, 2026, U.S. Treasury): 4.98%
  - Realty Income Q3 2026 Initial Cash Yield (Nov 2, 2026 8-K): 6.80%
  - Los Angeles Sep 2026 CPI-U YoY (BLS Nov 4, 2026): 3.70%
  - LA City + County Transfer Tax + Measure ULA (post-6/30/2026):
      * County-only (unincorporated): 0.11%
      * City <= $5.4M: 0.56% (0.45% City + 0.11% County)
      * City > $5.4M to < $10.9M (ULA Tier 1): 4.56%
      * City >= $10.9M (ULA Tier 2): 6.06%
  - Federal + CA Combined Top Long-Term Capital Gains Rate (2026):
      * 20.0% Fed LTCG + 3.8% NIIT + 13.3% CA (Prop 3 leading 60.7%) = 37.1% (plus 25% Sec. 1250 on depreciation)
  - USGS UCERF3 LA Area Earthquake Probability (M >= 6.7): 60% over 30 years -> 3.01%/year annualized hazard.

Seed: 20261112 (15,000 trials per regime)
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / "data" / "model_output.json"

SEED = 20261112
TRIALS = 15000

ANCHORS = {
    "access_date": "2026-11-12",
    "treasury_10y": 0.0498,
    "treasury_30y": 0.0535,
    "fed_funds_upper": 0.0400,
    "reit_cash_yield": 0.0680,
    "reit_spread_bps": 182,
    "la_cpi_yoy": 0.0370,
    "la_eci_yoy": 0.0390,
    "prop13_cap": 0.0200,
    "broker_closing_cost": 0.0300,
    "dtt_regimes": {
        "county_only": 0.0011,
        "city_sub_5_4m": 0.0056,
        "city_ula_t1": 0.0456,
        "city_ula_t2": 0.0606,
    },
    "tax_rates": {
        "fed_ltcg": 0.200,
        "fed_niit": 0.038,
        "fed_sec1250": 0.250,
        "ca_top": 0.133,
        "combined_marginal": 0.371,
    },
    "uceref3_annual_m67": 0.0301,
}


def pv_growing_annuity(pmt1: float, growth: float, disc: float, n: int) -> float:
    pv = 0.0
    for t in range(1, n + 1):
        pv += pmt1 * ((1.0 + growth) ** (t - 1)) / ((1.0 + disc) ** t)
    return pv


def percentile(sorted_vals: list[float], p: float) -> float:
    if not sorted_vals:
        return 0.0
    k = (len(sorted_vals) - 1) * p
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_vals[int(k)]
    return sorted_vals[f] * (c - k) + sorted_vals[c] * (k - f)


def summarize(vals: list[float]) -> dict[str, float]:
    s = sorted(vals)
    n = len(s)
    mean = sum(s) / n
    var = sum((x - mean) ** 2 for x in s) / n
    return {
        "mean": round(mean, 4),
        "median": round(percentile(s, 0.50), 4),
        "sd": round(math.sqrt(var), 4),
        "p05": round(percentile(s, 0.05), 4),
        "p10": round(percentile(s, 0.10), 4),
        "p25": round(percentile(s, 0.25), 4),
        "p75": round(percentile(s, 0.75), 4),
        "p90": round(percentile(s, 0.90), 4),
        "p95": round(percentile(s, 0.95), 4),
    }


def deterministic_strategies(
    exit_cap: float,
    horizon_yrs: int,
    dtt_rate: float,
    gain_ratio: float = 0.50,
    escalator: float = 0.020,
    disc: float = 0.0680,
    ti_downtime_expected: float = 0.45,
) -> dict[str, float]:
    """
    Compare 4 normalized strategies per $1.00 initial NOI over horizon_yrs:
      - hold_as_is: hold through expiry; terminal cap suffers +85 bps short-WALT cliff + expected downtime/TI
      - sell_1031: sell now, pay broker + DTT, reinvest 100% into 6.80% NNN replacement (2.0% growth, 6.80% exit)
      - blend_extend: extend lease +10 yrs today (-75 bps cap compression, 0.25x NOI TI/free rent, 2.25% escalators)
      - sell_taxable: sell now, pay broker + DTT + 37.1% tax on embedded gain_ratio, reinvest in 4.98% Treasury / 6.0% blend
    """
    gross_price = 1.0 / exit_cap

    # 1) Hold As-Is
    cf_hold = pv_growing_annuity(0.995, escalator, disc, horizon_yrs)
    term_noi_hold = 0.995 * ((1.0 + escalator) ** horizon_yrs)
    # Short-WALT cliff at expiry: +85 bps cap widening + expected downtime/TI deduction
    term_cap_hold = exit_cap + 0.0085
    term_val_hold = max(0.0, (term_noi_hold / term_cap_hold) - ti_downtime_expected)
    npv_hold = cf_hold + term_val_hold / ((1.0 + disc) ** horizon_yrs)

    # 2) Sell Now + IRC 1031
    net_proceeds_1031 = gross_price * (1.0 - ANCHORS["broker_closing_cost"] - dtt_rate)
    rep_noi1 = net_proceeds_1031 * ANCHORS["reit_cash_yield"]
    cf_1031 = pv_growing_annuity(rep_noi1, 0.020, disc, horizon_yrs)
    term_noi_1031 = rep_noi1 * ((1.0 + 0.020) ** horizon_yrs)
    term_val_1031 = term_noi_1031 / ANCHORS["reit_cash_yield"]
    npv_1031 = cf_1031 + term_val_1031 / ((1.0 + disc) ** horizon_yrs)

    # 3) Blend & Extend (+10 yrs today, 0.25x NOI TI concession, 2.25% rent escalator, -75 bps cap compression)
    ext_escalator = 0.0225
    cf_be = pv_growing_annuity(0.995, ext_escalator, disc, horizon_yrs) - 0.25
    term_noi_be = 0.995 * ((1.0 + ext_escalator) ** horizon_yrs)
    # Still retains ~10 yrs WALT at Year n -> trades near institutional parity minus modest age discount (+15 bps)
    term_cap_be = max(0.0525, exit_cap - 0.0040)
    term_val_be = term_noi_be / term_cap_be
    npv_be = cf_be + term_val_be / ((1.0 + disc) ** horizon_yrs)

    # 4) Taxable Sale -> 50% 10Y Treasury (4.98% CA exempt) / 50% Diversified Equity (7.5% pre-tax, 6.2% after-tax blend = 5.6% after-tax)
    pre_tax_net = net_proceeds_1031
    tax_drag = gross_price * gain_ratio * ANCHORS["tax_rates"]["combined_marginal"]
    after_tax_proceeds = max(0.0, pre_tax_net - tax_drag)
    # Total return portfolio blend ~5.65% net of ongoing tax drag -> NPV discounted at disc
    after_tax_yield = 0.0565
    npv_taxable = (
        pv_growing_annuity(after_tax_proceeds * after_tax_yield, 0.0, disc, horizon_yrs)
        + after_tax_proceeds / ((1.0 + disc) ** horizon_yrs)
    )

    return {
        "gross_price": round(gross_price, 4),
        "hold_npv": round(npv_hold, 4),
        "sell_1031_npv": round(npv_1031, 4),
        "blend_extend_npv": round(npv_be, 4),
        "sell_taxable_npv": round(npv_taxable, 4),
        "year1_income_hold": 0.995,
        "year1_income_1031": round(rep_noi1, 4),
        "year1_income_taxable": round(after_tax_proceeds * after_tax_yield, 4),
        "spread_1031_minus_hold": round(npv_1031 - npv_hold, 4),
        "spread_be_minus_hold": round(npv_be - npv_hold, 4),
    }


def compute_breakeven_exit_cap(horizon_yrs: int, dtt_rate: float) -> dict[str, float]:
    # Year-1 Cash Flow breakeven: (1 / c) * (1 - bc - dtt) * reit_yield = 0.995 -> c = reit_yield * net_factor / 0.995
    net_factor = 1.0 - ANCHORS["broker_closing_cost"] - dtt_rate
    y1_cf_be = (ANCHORS["reit_cash_yield"] * net_factor) / 0.995

    # Binary search multi-year NPV breakeven where sell_1031_npv == hold_npv
    lo, hi = 0.035, 0.095
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        res = deterministic_strategies(mid, horizon_yrs, dtt_rate)
        if res["sell_1031_npv"] > res["hold_npv"]:
            lo = mid
        else:
            hi = mid
    npv_be = 0.5 * (lo + hi)
    return {
        "year1_cash_breakeven_cap": round(y1_cf_be, 5),
        "npv_breakeven_cap": round(npv_be, 5),
    }


def run_monte_carlo(
    regime: str,
    trials: int = TRIALS,
    base_cap: float = 0.0625,
    horizon_yrs: int = 6,
    dtt_rate: float = 0.0056,
    gain_ratio: float = 0.50,
    seed_offset: int = 0,
) -> dict:
    rng = random.Random(SEED + seed_offset)
    disc = ANCHORS["reit_cash_yield"]

    hold_vals: list[float] = []
    s1031_vals: list[float] = []
    be_vals: list[float] = []
    tax_vals: list[float] = []

    win_1031_vs_hold = 0
    win_be_vs_hold = 0
    win_tax_vs_hold = 0
    win_1031_vs_be = 0

    is_swan = regime == "black_swan"

    for _ in range(trials):
        # 1) Macro rate & cap shock
        if not is_swan:
            rate_shock = rng.gauss(0.0, 0.0065)
            reit_yield = max(0.056, min(0.084, 0.0680 + rng.gauss(0.0, 0.0045)))
            inflation = max(0.015, min(0.060, 0.037 + rng.gauss(0.0, 0.008)))
            p_nonrenew = 0.22
            p_default_yr = 0.015
            p_quake_yr = 0.0301
            p_wildfire_shock = 0.04
            ti_months_base = rng.uniform(0.30, 0.90)
        else:
            rate_shock = rng.gauss(0.0110, 0.0095)
            reit_yield = max(0.058, min(0.095, 0.0735 + rng.gauss(0.0, 0.0065)))
            inflation = max(0.025, min(0.085, 0.052 + rng.gauss(0.0, 0.012)))
            p_nonrenew = 0.48
            p_default_yr = 0.045
            p_quake_yr = 0.0450
            p_wildfire_shock = 0.14
            ti_months_base = rng.uniform(0.75, 1.85)

        going_in_cap = max(0.048, min(0.090, base_cap + rng.gauss(0.0, 0.0035)))
        gross_price = 1.0 / going_in_cap
        net_1031_proc = gross_price * (1.0 - ANCHORS["broker_closing_cost"] - dtt_rate)

        # Hold Cash Flows
        hold_cf = 0.0
        cur_noi = 0.995
        defaulted = False
        quake_hit = False
        ins_hit = rng.random() < p_wildfire_shock
        for t in range(1, horizon_yrs + 1):
            if t > 1:
                cur_noi *= 1.020
            # Franchisee default event
            if not defaulted and rng.random() < p_default_yr:
                defaulted = True
                # 1 year downtime + re-tenant at -12% rent
                yr_cf = -0.35
                cur_noi *= 0.88
            else:
                yr_cf = cur_noi
            # Insurance leakage shock (uninsured DIC / FAIR Plan friction)
            if ins_hit:
                yr_cf -= (0.04 if not is_swan else 0.10)
            # Seismic event (self-insured gap / downtime)
            if not quake_hit and rng.random() < p_quake_yr:
                quake_hit = True
                yr_cf -= (0.35 if not is_swan else 1.25)
            hold_cf += yr_cf / ((1.0 + disc) ** t)

        nonrenewed = defaulted or (rng.random() < p_nonrenew)
        cliff_bps = (0.0135 if nonrenewed else 0.0055) + max(-0.004, rate_shock)
        term_cap_hold = max(0.050, going_in_cap + cliff_bps)
        ti_cost = ti_months_base if nonrenewed else 0.10
        term_val_hold = max(0.0, (cur_noi / term_cap_hold) - ti_cost)
        hold_npv = hold_cf + term_val_hold / ((1.0 + disc) ** horizon_yrs)

        # Sell + 1031 (diversified investment-grade net lease)
        rep_noi = net_1031_proc * reit_yield
        cf_1031 = 0.0
        for t in range(1, horizon_yrs + 1):
            if t > 1:
                rep_noi *= 1.020
            # Very low diversified default drag (~0.4% BAU, ~1.2% Swan)
            drag = 0.996 if not is_swan else 0.985
            cf_1031 += (rep_noi * drag) / ((1.0 + disc) ** t)
        term_cap_1031 = max(0.052, reit_yield + max(-0.005, rate_shock * 0.75))
        s1031_npv = cf_1031 + (rep_noi / term_cap_1031) / ((1.0 + disc) ** horizon_yrs)

        # Blend & Extend (success probability 72% BAU / 45% Swan; if fails reverts near Hold minus negotiation cost)
        be_accept = rng.random() < (0.72 if not is_swan else 0.45)
        if be_accept:
            be_noi = 0.995
            be_cf = -0.25  # TI/free-rent upfront
            for t in range(1, horizon_yrs + 1):
                if t > 1:
                    be_noi *= 1.0225
                be_yr = be_noi - (0.03 if ins_hit else 0.0)
                if quake_hit and t == 2:
                    be_yr -= (0.25 if not is_swan else 0.95)
                be_cf += be_yr / ((1.0 + disc) ** t)
            term_cap_be = max(0.050, going_in_cap - 0.0035 + max(-0.004, rate_shock * 0.85))
            be_npv = be_cf + (be_noi / term_cap_be) / ((1.0 + disc) ** horizon_yrs)
        else:
            be_npv = hold_npv - 0.08

        # Taxable Sale -> Treasury/Diversified Portfolio (uncorrelated with LA retail)
        tax_drag = gross_price * gain_ratio * ANCHORS["tax_rates"]["combined_marginal"]
        at_proc = max(0.0, net_1031_proc - tax_drag)
        port_ret = (0.0565 + rng.gauss(0.0, 0.018)) if not is_swan else (0.0480 + rng.gauss(0.0, 0.030))
        port_bal = at_proc
        tax_cf = 0.0
        for t in range(1, horizon_yrs + 1):
            # Take 4.5% distribution + grow remainder
            dist = port_bal * 0.048
            port_bal = max(0.0, port_bal * (1.0 + port_ret) - dist)
            tax_cf += dist / ((1.0 + disc) ** t)
        tax_npv = tax_cf + port_bal / ((1.0 + disc) ** horizon_yrs)

        # Adjust slight real-inflation purchasing-power normalization indicator? Keep nominal NPV consistently discounted at 6.80%
        _ = inflation

        hold_vals.append(hold_npv)
        s1031_vals.append(s1031_npv)
        be_vals.append(be_npv)
        tax_vals.append(tax_npv)

        if s1031_npv > hold_npv:
            win_1031_vs_hold += 1
        if be_npv > hold_npv:
            win_be_vs_hold += 1
        if tax_npv > hold_npv:
            win_tax_vs_hold += 1
        if s1031_npv > be_npv:
            win_1031_vs_be += 1

    return {
        "regime": regime,
        "trials": trials,
        "base_cap": base_cap,
        "horizon_yrs": horizon_yrs,
        "dtt_rate": dtt_rate,
        "gain_ratio": gain_ratio,
        "strategies": {
            "hold": summarize(hold_vals),
            "sell_1031": summarize(s1031_vals),
            "blend_extend": summarize(be_vals),
            "sell_taxable": summarize(tax_vals),
        },
        "win_probabilities": {
            "p_1031_beats_hold": round(win_1031_vs_hold / trials, 4),
            "p_blend_extend_beats_hold": round(win_be_vs_hold / trials, 4),
            "p_taxable_beats_hold": round(win_tax_vs_hold / trials, 4),
            "p_1031_beats_blend_extend": round(win_1031_vs_be / trials, 4),
        },
    }


def main() -> None:
    caps = [0.055, 0.060, 0.0625, 0.065, 0.070, 0.075]
    horizons = [4, 6, 8]
    dtt_cases = [
        ("city_sub_5_4m", "City <= $5.4M (0.56% DTT)", 0.0056),
        ("city_ula_t1", "City > $5.4M-$10.9M ULA (4.56% DTT)", 0.0456),
        ("city_ula_t2", "City >= $10.9M ULA (6.06% DTT)", 0.0606),
    ]

    det_grid = []
    for dtt_key, dtt_label, dtt_rate in dtt_cases:
        for h in horizons:
            for c in caps:
                res = deterministic_strategies(c, h, dtt_rate)
                det_grid.append({
                    "dtt_key": dtt_key,
                    "dtt_label": dtt_label,
                    "dtt_rate": dtt_rate,
                    "horizon_yrs": h,
                    "exit_cap": c,
                    **res,
                })

    breakevens = {}
    for dtt_key, dtt_label, dtt_rate in dtt_cases:
        breakevens[dtt_key] = {
            "label": dtt_label,
            "dtt_rate": dtt_rate,
            "h4": compute_breakeven_exit_cap(4, dtt_rate),
            "h6": compute_breakeven_exit_cap(6, dtt_rate),
            "h8": compute_breakeven_exit_cap(8, dtt_rate),
        }

    # Term structure (Year-by-Year Hold vs 1031 vs Blend-Extend at base 6.25% cap, Sub-$5.4M)
    term_curve = []
    for h in [4, 5, 6, 7, 8, 9]:
        sub = deterministic_strategies(0.0625, h, 0.0056)
        ula = deterministic_strategies(0.0625, h, 0.0456)
        term_curve.append({
            "horizon_yrs": h,
            "expiry_year": 2026 + h,
            "hold_npv": sub["hold_npv"],
            "sell_1031_sub54_npv": sub["sell_1031_npv"],
            "sell_1031_ula_npv": ula["sell_1031_npv"],
            "blend_extend_npv": sub["blend_extend_npv"],
            "sell_taxable_npv": sub["sell_taxable_npv"],
        })

    # Sensitivity tornado around Base Case (c=6.25%, n=6, sub-$5.4M, gain=50%)
    base_res = deterministic_strategies(0.0625, 6, 0.0056, gain_ratio=0.50)
    base_diff = base_res["sell_1031_npv"] - base_res["hold_npv"]
    tornado = [
        {
            "driver": "Going-In Exit Cap (5.50% vs 7.00%)",
            "low_spread": round(
                deterministic_strategies(0.0700, 6, 0.0056)["spread_1031_minus_hold"], 4
            ),
            "high_spread": round(
                deterministic_strategies(0.0550, 6, 0.0056)["spread_1031_minus_hold"], 4
            ),
        },
        {
            "driver": "Transfer Tax / ULA (6.06% vs 0.11%)",
            "low_spread": round(
                deterministic_strategies(0.0625, 6, 0.0606)["spread_1031_minus_hold"], 4
            ),
            "high_spread": round(
                deterministic_strategies(0.0625, 6, 0.0011)["spread_1031_minus_hold"], 4
            ),
        },
        {
            "driver": "Expiry Horizon (9 yrs vs 4 yrs)",
            "low_spread": round(
                deterministic_strategies(0.0625, 9, 0.0056)["spread_1031_minus_hold"], 4
            ),
            "high_spread": round(
                deterministic_strategies(0.0625, 4, 0.0056)["spread_1031_minus_hold"], 4
            ),
        },
        {
            "driver": "Re-leasing TI / Downtime (1.2x vs 0.1x)",
            "low_spread": round(
                deterministic_strategies(0.0625, 6, 0.0056, ti_downtime_expected=0.10)[
                    "spread_1031_minus_hold"
                ],
                4,
            ),
            "high_spread": round(
                deterministic_strategies(0.0625, 6, 0.0056, ti_downtime_expected=1.20)[
                    "spread_1031_minus_hold"
                ],
                4,
            ),
        },
        {
            "driver": "Lease Rent Escalator (3.0% vs 0.0%)",
            "low_spread": round(
                deterministic_strategies(0.0625, 6, 0.0056, escalator=0.030)[
                    "spread_1031_minus_hold"
                ],
                4,
            ),
            "high_spread": round(
                deterministic_strategies(0.0625, 6, 0.0056, escalator=0.000)[
                    "spread_1031_minus_hold"
                ],
                4,
            ),
        },
    ]

    # Four 15,000-trial Monte Carlo packages: BAU & Black Swan across Sub-$5.4M & ULA Tier 1
    mc_bau_sub54 = run_monte_carlo("bau", dtt_rate=0.0056, seed_offset=0)
    mc_swan_sub54 = run_monte_carlo("black_swan", dtt_rate=0.0056, seed_offset=100)
    mc_bau_ula = run_monte_carlo("bau", dtt_rate=0.0456, seed_offset=200)
    mc_swan_ula = run_monte_carlo("black_swan", dtt_rate=0.0456, seed_offset=300)

    # Basis sensitivity for Taxable Exit vs Hold
    tax_basis_table = []
    for gr in [0.15, 0.30, 0.50, 0.75]:
        r_sub = deterministic_strategies(0.0625, 6, 0.0056, gain_ratio=gr)
        r_ula = deterministic_strategies(0.0625, 6, 0.0456, gain_ratio=gr)
        tax_basis_table.append({
            "gain_ratio": gr,
            "hold_npv": r_sub["hold_npv"],
            "sell_1031_sub54_npv": r_sub["sell_1031_npv"],
            "sell_taxable_sub54_npv": r_sub["sell_taxable_npv"],
            "sell_taxable_ula_npv": r_ula["sell_taxable_npv"],
            "tax_drag_pct_of_price_sub54": round(gr * ANCHORS["tax_rates"]["combined_marginal"] * 100, 2),
        })

    output = {
        "meta": {
            "seed": SEED,
            "trials_per_regime": TRIALS,
            "normalized_unit": "Per $1.00 of initial Net Operating Income (NOI)",
            "anchors": ANCHORS,
        },
        "breakevens": breakevens,
        "base_case_summary": {
            "assumption": "Going-in cap 6.25%, 2032 expiry (n=6), Sub-$5.4M (0.56% DTT), 50% embedded gain",
            **base_res,
            "spread_1031_minus_hold": round(base_diff, 4),
        },
        "deterministic_grid": det_grid,
        "term_curve": term_curve,
        "tornado": tornado,
        "tax_basis_sensitivity": tax_basis_table,
        "monte_carlo": {
            "bau_sub54": mc_bau_sub54,
            "black_swan_sub54": mc_swan_sub54,
            "bau_ula_t1": mc_bau_ula,
            "black_swan_ula_t1": mc_swan_ula,
        },
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_PATH}")
    print("Breakevens (n=6):")
    for k, v in breakevens.items():
        print(f"  {k}: Y1 Cash BE = {v['h6']['year1_cash_breakeven_cap']:.2%}, NPV BE = {v['h6']['npv_breakeven_cap']:.2%}")
    print("MC BAU Sub-$5.4M:", mc_bau_sub54["win_probabilities"])
    print("MC Swan Sub-$5.4M:", mc_swan_sub54["win_probabilities"])
    print("MC BAU ULA-T1:", mc_bau_ula["win_probabilities"])
    print("MC Swan ULA-T1:", mc_swan_ula["win_probabilities"])


if __name__ == "__main__":
    main()
