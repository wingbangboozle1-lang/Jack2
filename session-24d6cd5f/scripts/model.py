#!/usr/bin/env python3
"""
Quantitative Area, Credit & Lease Decision Engine
Session: session-24d6cd5f (2026-11-08)
Standard library only. Fully deterministic (seed = 20261108, 20,000 trials).

Normalizes all static outcomes per $100,000 of current annual NNN NOI so zero
private rent, tax basis, or parcel values are inferred or exposed.
"""
import json
import math
import os
import random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")

SEED = 20261108
N_TRIALS = 20000
BASE_NOI = 100000.0
HORIZON = 14  # 2026 -> 2040

# Directly observed Tier A / Tier B anchors (2026-11-08)
VERIFIED_ANCHORS = {
    "ust_10yr_nov06_2026_pct": 4.86,           # S20: U.S. Treasury Par Yield Nov 6, 2026
    "ust_10yr_fred_nov05_2026_pct": 4.84,      # S21: FRED DGS10 Nov 5, 2026
    "fed_funds_target_upper_pct": 4.00,        # S22: FRED DFEDTARU Nov 8, 2026
    "fed_funds_effective_pct": 3.88,           # S22: FRED DFF Nov 5, 2026
    "la_cpi_sep2026_pct": 3.70,                # S03: BLS Sep 2026 LA CPI-U
    "la_eci_comp_sep2026_pct": 4.20,           # S04: BLS Sep 2026 LA CSA ECI Total Comp
    "la_county_gdp_2024_usd_b": 810.84,        # S13: BEA/FRED REALGDPALL06037
    "dof_e1_county_yoy_pct": -0.60,            # S07: CA DOF E-1 Jan 2026
    "dof_k12_10yr_change_students": -240800,   # S09: CA DOF Aug 2026 K-12
    "ab1228_fast_food_wage_usd": 20.00,        # S17: CA DIR AB 1228
    "la_city_min_wage_usd": 18.42,             # S18: Wages LA eff Jul 1, 2026
    "nnn_reit_1h26_acq_cap_pct": 7.40,         # S23: NNN REIT Q2 2026 8-K
    "realty_income_1h26_us_yield_pct": 7.50,   # S24: Realty Income Q2 2026 Supp
    "jack_q3_fy26_units": 2115,                # S32: JACK Q3 FY26 10-Q
    "jack_ca_units_fy25": 941,                 # S31: JACK FY25 10-K (44.1%)
    "jack_store_margin_guide_pct": 16.50,      # S32: JACK Aug 12, 2026 guidance cut
    "jack_may2031_ard_coupon_pct": 7.624,      # S33: JACK Jun 23, 2026 8-K ($500M)
    "base_transfer_tax_pct": 0.56,             # S26: 0.11% County + 0.45% City
    "ula_tier1_total_tax_pct": 4.56,           # S27: +4.0% ULA (> $5.4M)
    "ula_tier1_cliff_usd": 5400000,            # S27: Effective Jul 1, 2026
    "combined_ca_fed_tax_pct": 37.10,          # S28/S30: 20% + 3.8% + 13.3% (Prop 3 permanent)
    "usgs_30yr_m67_prob_pct": 60.0             # S34: USGS UCERF3
}

ASSUMPTIONS = [
    {
        "id": "A-01",
        "name": "Normalized Annual NNN NOI Unit",
        "value": "$100,000 / year",
        "detail": "Scales linearly for any private contract rent (e.g., 1.8x for $180k NOI).",
        "source": "S31"
    },
    {
        "id": "A-02",
        "name": "Lease Expiry Window Midpoint & Full Sweep",
        "value": "2032 central (~6.0 yrs remaining); sweeps 2030..2035",
        "detail": "Captures May 2031 $500M 7.624% Class A-2 ARD collision risk inside the expiry window.",
        "source": "S33"
    },
    {
        "id": "A-03",
        "name": "Single-Tenant QSR Exit Cap-Rate Curve",
        "value": "15+ yr: 6.45% | 10 yr: 6.60% | 6 yr (2032): 6.95% | 4 yr (2030): 7.45% | <2 yr / dark: 8.40%",
        "detail": "Anchored to NNN REIT 1H26 7.40% acquisition / 5.60%–7.20% disposition range and Realty Income 7.50% U.S. yield.",
        "source": "S23"
    },
    {
        "id": "A-04",
        "name": "Rent Escalations (In-Place vs. Blend-and-Extend)",
        "value": "In-place: +1.50%/yr | Early Extend: -3% rent reset + 2.25%/yr collared steps | Expiry Reset: -4% avg",
        "detail": "Reflects standard 7.5%–10% 5-year QSR steps lagging +3.70% LA CPI-U (S03) and JACK 16.5% margin squeeze (S32).",
        "source": "S03"
    },
    {
        "id": "A-05",
        "name": "Diversified §1031 Replacement Net Yield & Growth",
        "value": "7.20% net yield (after 30 bps friction vs 7.50% O U.S. / 7.40% NNN) + 2.00%/yr growth",
        "detail": "Multi-tenant / IG net-lease portfolio eliminates single-site JACK credit & Central LA seismic concentration.",
        "source": "S24"
    },
    {
        "id": "A-06",
        "name": "Sale Friction (Base vs. Measure ULA Cliff)",
        "value": "4.56% below $5.4M (4.00% closing + 0.56% DTT) | 8.56% above $5.4M (+4.00% City ULA)",
        "detail": "Measure ULA remains intact following withdrawal of initiative 25-0006A1 and Prop 43 defeat (S27, S28).",
        "source": "S27"
    },
    {
        "id": "A-07",
        "name": "Taxable Sale Effective Tax Drag (Post-Prop 3)",
        "value": "25.0% blended effective tax on gross price (~38.5% combined rate x ~65% gain+§1250 basis ratio)",
        "detail": "Prop 3 (60.3% Yes) permanently preserves 13.30% CA top bracket past 2030 (S28, S30); sensitivity spans 0%–75% gain ratio.",
        "source": "S28"
    },
    {
        "id": "A-08",
        "name": "Single-Parcel Hazard & May 2031 ARD Shock Overlay",
        "value": "1.35%/yr severe LA parcel hazard + 2031 tenant refinancing distress factor",
        "detail": "Calibrated to USGS 60% 30-yr M>=6.7 probability (S34), CDI $1B FAIR Plan pressure (S35), and May 2031 ARD (S33).",
        "source": "S34"
    }
]


def cap_rate_for_term(rem_years, spread_bps=0.0):
    if rem_years >= 14.0:
        base = 6.45
    elif rem_years >= 10.0:
        base = 6.45 + (14.0 - rem_years) * (0.15 / 4.0)   # 6.45 -> 6.60
    elif rem_years >= 6.0:
        base = 6.60 + (10.0 - rem_years) * (0.35 / 4.0)   # 6.60 -> 6.95
    elif rem_years >= 3.0:
        base = 6.95 + (6.0 - rem_years) * (0.65 / 3.0)    # 6.95 -> 7.60
    else:
        base = 7.60 + max(0.0, 3.0 - rem_years) * 0.35    # 7.60 -> 8.65
    return max(5.25, min(11.0, base + spread_bps / 100.0))


def crra_certainty_equivalent(values, gamma=2.0):
    vals = [max(1.0, v) for v in values]
    n = len(vals)
    if gamma == 1.0:
        return math.exp(sum(math.log(v) for v in vals) / n)
    mean_u = sum((v ** (1.0 - gamma)) for v in vals) / n
    return mean_u ** (1.0 / (1.0 - gamma))


def summarize(vals, costs, irrs):
    sv = sorted(vals)
    n = len(sv)
    mean_v = sum(sv) / n
    ce = crra_certainty_equivalent(sv, gamma=2.0)
    var = sum((x - mean_v) ** 2 for x in sv) / n
    sd = math.sqrt(var)
    downside_dev = math.sqrt(sum(min(0.0, x - mean_v) ** 2 for x in sv) / n)
    return {
        "mean_2040": round(mean_v, 0),
        "median_2040": round(sv[int(0.50 * n)], 0),
        "p10_2040": round(sv[int(0.10 * n)], 0),
        "p90_2040": round(sv[int(0.90 * n)], 0),
        "ce_2040": round(ce, 0),
        "std_dev": round(sd, 0),
        "downside_dev": round(downside_dev, 0),
        "median_irr_pct": round(sorted(irrs)[int(0.50 * len(irrs))], 2),
        "sharpe_proxy": round(mean_v / sd, 2) if sd > 0 else 0.0,
        "prob_below_150k": round(100.0 * sum(1 for v in sv if v < 1500000.0) / n, 1),
    }


def simulate_strategies(
    n_trials=N_TRIALS,
    expiry_year=2032,
    guarantor="corporate",
    regime="base",
    ula_applies=False,
    tax_on_gain_ratio=0.65,
    extend_prob_override=None,
):
    rng = random.Random(SEED + expiry_year * 17 + (101 if guarantor == "franchisee" else 0))
    expiry_idx = expiry_year - 2026  # e.g. 2032 -> year 6
    sell_friction = 0.0856 if ula_applies else 0.0456
    stat_tax_rate = 0.386  # Blended 37.1% LTCG/NIIT/CA + 42.1% §1250 slice

    # Regime adjustments
    if regime == "stagflation":
        rate_shift_bps = 125.0
        cpi_drift = 0.044
        reit_yield_shift = 0.0045
        credit_stress_mult = 1.45
        cash_reinv_rate = 0.056
    elif regime == "soft_landing":
        rate_shift_bps = -85.0
        cpi_drift = 0.023
        reit_yield_shift = -0.004
        credit_stress_mult = 0.72
        cash_reinv_rate = 0.0375
    else:  # base
        rate_shift_bps = 0.0
        cpi_drift = 0.032
        reit_yield_shift = 0.0
        credit_stress_mult = 1.0
        cash_reinv_rate = 0.0475

    guarantor_nonrenew_add = 0.09 if guarantor == "franchisee" else 0.0
    guarantor_cap_add_bps = 45.0 if guarantor == "franchisee" else 0.0
    extend_success_prob = 0.58 if guarantor == "corporate" else 0.44
    if extend_prob_override is not None:
        extend_success_prob = extend_prob_override

    strat_keys = [
        "S1_hold_passive",
        "S2_blend_extend_hold",
        "S3_blend_extend_1031",
        "S4_sell_1031_now",
        "S5_sell_taxable_now",
        "S6_hold_reposition_land",
    ]
    results = {k: [] for k in strat_keys}
    irrs = {k: [] for k in strat_keys}

    t0_cap = cap_rate_for_term(expiry_idx, spread_bps=guarantor_cap_add_bps)
    t0_gross = BASE_NOI / (t0_cap / 100.0)

    for _ in range(n_trials):
        # Correlated macro draws
        macro_rate_bps = rng.gauss(rate_shift_bps, 65.0)
        jack_credit_bps = rng.gauss(25.0 * credit_stress_mult, 45.0 * credit_stress_mult)
        ard_2031_hit = rng.random() < (0.14 * credit_stress_mult)
        if ard_2031_hit:
            jack_credit_bps += rng.uniform(60.0, 140.0)

        parcel_shock = rng.random() < (1.0 - (1.0 - 0.0135) ** HORIZON)
        shock_year = rng.randint(1, HORIZON) if parcel_shock else 999
        shock_severity = rng.uniform(0.18, 0.42) if parcel_shock else 0.0

        cpi_realized = max(0.015, rng.gauss(cpi_drift, 0.009))
        reit_reinvest_net = max(0.056, min(0.088, 0.0720 + reit_yield_shift + rng.gauss(0.0, 0.004) + macro_rate_bps * 0.00004))

        # --- S4: Immediate Sale + 1031 Exchange Now ---
        s4_equity_after_friction = t0_gross * (1.0 - sell_friction)
        s4_cash = 0.0
        s4_noi = s4_equity_after_friction * reit_reinvest_net
        for yr in range(1, HORIZON + 1):
            div_shock = rng.uniform(0.0, 0.03)  # Diversified multi-tenant portfolio resilience
            s4_cash = s4_cash * (1.0 + cash_reinv_rate * (1.0 - 0.30)) + s4_noi * (1.0 - div_shock)
            s4_noi *= (1.0 + 0.020)
        exit_reit_cap = max(5.6, min(8.6, 6.70 + macro_rate_bps * 0.0065 + rng.gauss(0.0, 0.35)))
        s4_terminal = (s4_noi / (exit_reit_cap / 100.0)) * (1.0 - 0.025)  # Diversified non-LA exit friction
        s4_wealth = s4_cash + s4_terminal
        results["S4_sell_1031_now"].append(s4_wealth)
        irrs["S4_sell_1031_now"].append(((s4_wealth / t0_gross) ** (1.0 / HORIZON) - 1.0) * 100.0)

        # --- S5: Immediate Taxable Sale -> UST / IG Bond Ladder ---
        tax_bite = t0_gross * tax_on_gain_ratio * stat_tax_rate
        s5_investable = max(10000.0, t0_gross * (1.0 - sell_friction) - tax_bite)
        bond_after_tax = max(0.025, (cash_reinv_rate + macro_rate_bps * 0.00005) * (1.0 - 0.35))
        s5_wealth = s5_investable * ((1.0 + bond_after_tax) ** HORIZON)
        results["S5_sell_taxable_now"].append(s5_wealth)
        irrs["S5_sell_taxable_now"].append(((s5_wealth / t0_gross) ** (1.0 / HORIZON) - 1.0) * 100.0)

        # --- Helper for subject parcel cash flows with in-place / extension ---
        def subject_hold_path(extended=False, flip_1031_yr=None, reposition=False):
            cash = 0.0
            noi = BASE_NOI * (0.97 if extended else 1.0)
            esc = 0.0225 if extended else 0.0150
            renew_prob = 0.90 if extended else max(0.42, 0.72 - guarantor_nonrenew_add - (0.08 if ard_2031_hit else 0.0))
            downtime_cost = 0.0
            non_renewed = False

            for yr in range(1, HORIZON + 1):
                if flip_1031_yr and yr == flip_1031_yr:
                    # Execute 1031 at yr 1 after blend-and-extend
                    rem_after_ext = max(6.0, expiry_idx + (10.0 if extended else 0.0) - yr)
                    ex_cap = cap_rate_for_term(rem_after_ext, spread_bps=macro_rate_bps * 0.55 + jack_credit_bps * 0.65)
                    proceeds = (noi / (ex_cap / 100.0)) * (1.0 - sell_friction)
                    # Roll into diversified 1031 portfolio for remainder
                    p_noi = proceeds * reit_reinvest_net
                    p_cash = cash * (1.0 + cash_reinv_rate * 0.70)
                    for ryr in range(yr + 1, HORIZON + 1):
                        p_cash = p_cash * (1.0 + cash_reinv_rate * 0.70) + p_noi * 0.985
                        p_noi *= 1.020
                    term_val = (p_noi / (exit_reit_cap / 100.0)) * (1.0 - 0.025)
                    return p_cash + term_val

                # Check expiry rollover if not extended
                if (not extended) and yr == expiry_idx + 1:
                    if rng.random() > renew_prob:
                        non_renewed = True
                        if reposition:
                            # Hold & ground lease / adaptive reuse
                            downtime_cost = BASE_NOI * rng.uniform(1.15, 1.55)
                            capex_ti = BASE_NOI * rng.uniform(1.60, 2.50)
                            cash -= (downtime_cost + capex_ti)
                            noi = BASE_NOI * rng.uniform(1.06, 1.24)
                            esc = 0.025
                        else:
                            downtime_cost = BASE_NOI * rng.uniform(0.95, 1.35)
                            capex_ti = BASE_NOI * rng.uniform(1.50, 2.25)
                            cash -= (downtime_cost + capex_ti)
                            noi = BASE_NOI * rng.uniform(0.84, 1.02)
                            esc = 0.020
                    else:
                        # Renew at market reset
                        noi *= rng.uniform(0.90, 1.03)
                        esc = 0.019

                yr_rent = noi
                if yr >= shock_year:
                    yr_rent *= (1.0 - shock_severity * 0.55)
                cash = cash * (1.0 + cash_reinv_rate * 0.70) + yr_rent * 0.96
                noi *= (1.0 + esc)

            # Terminal value at 2040
            if extended:
                rem_2040 = max(2.0, (expiry_idx + 10.0) - HORIZON)
                term_cap = cap_rate_for_term(rem_2040, spread_bps=macro_rate_bps * 0.6 + jack_credit_bps * 0.7)
            elif non_renewed and reposition:
                term_cap = cap_rate_for_term(9.0, spread_bps=macro_rate_bps * 0.55)
            elif non_renewed:
                term_cap = cap_rate_for_term(7.0, spread_bps=macro_rate_bps * 0.65)
            else:
                # Renewed once in early 2030s -> 2-5 yrs left by 2040
                term_cap = cap_rate_for_term(4.0, spread_bps=macro_rate_bps * 0.6 + jack_credit_bps * 0.7)

            terminal = (noi / (term_cap / 100.0)) * (1.0 - sell_friction)
            if parcel_shock:
                terminal *= (1.0 - shock_severity)
            return cash + terminal

        # S1: Hold Passive
        w1 = subject_hold_path(extended=False)
        results["S1_hold_passive"].append(w1)
        irrs["S1_hold_passive"].append(((max(10000.0, w1) / t0_gross) ** (1.0 / HORIZON) - 1.0) * 100.0)

        # S2: Blend-and-Extend (or fallback to passive if tenant rejects)
        ext_ok = rng.random() < extend_success_prob
        w2 = subject_hold_path(extended=ext_ok)
        results["S2_blend_extend_hold"].append(w2)
        irrs["S2_blend_extend_hold"].append(((max(10000.0, w2) / t0_gross) ** (1.0 / HORIZON) - 1.0) * 100.0)

        # S3: Blend-and-Extend + Sell via 1031 in Year 1 (fallback to S4 immediate 1031 if rejected)
        if ext_ok:
            w3 = subject_hold_path(extended=True, flip_1031_yr=1)
        else:
            w3 = s4_wealth * rng.uniform(0.96, 0.995)  # Minor delay friction if extension fails
        results["S3_blend_extend_1031"].append(w3)
        irrs["S3_blend_extend_1031"].append(((max(10000.0, w3) / t0_gross) ** (1.0 / HORIZON) - 1.0) * 100.0)

        # S6: Hold to Expiry & Reposition / Re-Tenant Urban Drive-Thru
        w6 = subject_hold_path(extended=False, reposition=True)
        results["S6_hold_reposition_land"].append(w6)
        irrs["S6_hold_reposition_land"].append(((max(10000.0, w6) / t0_gross) ** (1.0 / HORIZON) - 1.0) * 100.0)

    meta_labels = {
        "S1_hold_passive": "Hold Passive Through 2030–2035 Expiry",
        "S2_blend_extend_hold": "Early Blend-and-Extend (10 Yr), Hold to 2040",
        "S3_blend_extend_1031": "Blend-and-Extend + §1031 Exchange at 10+ Yr WALT",
        "S4_sell_1031_now": "Immediate Sale + §1031 Into IG Net-Lease Now",
        "S5_sell_taxable_now": "Immediate Taxable Cash Sale -> Treasury/IG Bonds",
        "S6_hold_reposition_land": "Hold to Expiry & Reposition Drive-Thru Parcel",
    }
    summaries = []
    for k in strat_keys:
        s = summarize(results[k], sell_friction, irrs[k])
        s["id"] = k
        s["label"] = meta_labels[k]
        summaries.append(s)
    summaries.sort(key=lambda x: x["ce_2040"], reverse=True)
    return {
        "t0_cap_pct": round(t0_cap, 2),
        "t0_gross_value": round(t0_gross, 0),
        "sell_friction_pct": round(sell_friction * 100.0, 2),
        "strategies": summaries,
    }


def main():
    base_corp = simulate_strategies(n_trials=N_TRIALS, expiry_year=2032, guarantor="corporate", regime="base", ula_applies=False)
    base_fran = simulate_strategies(n_trials=8000, expiry_year=2032, guarantor="franchisee", regime="base", ula_applies=False)
    base_ula = simulate_strategies(n_trials=8000, expiry_year=2032, guarantor="corporate", regime="base", ula_applies=True)
    stagflation = simulate_strategies(n_trials=8000, expiry_year=2032, guarantor="corporate", regime="stagflation", ula_applies=False)
    soft_landing = simulate_strategies(n_trials=8000, expiry_year=2032, guarantor="corporate", regime="soft_landing", ula_applies=False)

    expiry_sweep = []
    for yr in range(2030, 2036):
        res = simulate_strategies(n_trials=5000, expiry_year=yr, guarantor="corporate", regime="base", ula_applies=False)
        by_id = {s["id"]: s for s in res["strategies"]}
        expiry_sweep.append({
            "expiry_year": yr,
            "rem_years": yr - 2026,
            "t0_cap_pct": res["t0_cap_pct"],
            "t0_gross_value": res["t0_gross_value"],
            "S3_blend_extend_1031_ce": by_id["S3_blend_extend_1031"]["ce_2040"],
            "S4_sell_1031_now_ce": by_id["S4_sell_1031_now"]["ce_2040"],
            "S2_blend_extend_hold_ce": by_id["S2_blend_extend_hold"]["ce_2040"],
            "S1_hold_passive_ce": by_id["S1_hold_passive"]["ce_2040"],
            "S5_sell_taxable_now_ce": by_id["S5_sell_taxable_now"]["ce_2040"],
        })

    basis_sweep = []
    for gain_pct in (0, 25, 50, 65, 80):
        res = simulate_strategies(n_trials=5000, expiry_year=2032, guarantor="corporate", regime="base", ula_applies=False, tax_on_gain_ratio=gain_pct / 100.0)
        by_id = {s["id"]: s for s in res["strategies"]}
        basis_sweep.append({
            "gain_ratio_pct": gain_pct,
            "S4_sell_1031_now_ce": by_id["S4_sell_1031_now"]["ce_2040"],
            "S5_sell_taxable_now_ce": by_id["S5_sell_taxable_now"]["ce_2040"],
            "S1_hold_passive_ce": by_id["S1_hold_passive"]["ce_2040"],
            "tax_savings_advantage": round(by_id["S4_sell_1031_now"]["ce_2040"] - by_id["S5_sell_taxable_now"]["ce_2040"], 0),
        })

    # Cap rate term curve table
    term_curve = [
        {"rem_years": y, "corp_cap_pct": round(cap_rate_for_term(y, 0.0), 2), "fran_cap_pct": round(cap_rate_for_term(y, 45.0), 2)}
        for y in (15, 12, 10, 8, 6, 5, 4, 3, 2, 1)
    ]

    output = {
        "meta": {
            "session": "session-24d6cd5f",
            "generated_at": "2026-11-08",
            "seed": SEED,
            "trials": N_TRIALS,
            "horizon_years": HORIZON,
            "normalized_noi_usd": BASE_NOI,
        },
        "verified_anchors": VERIFIED_ANCHORS,
        "assumptions": ASSUMPTIONS,
        "base_corporate": base_corp,
        "base_franchisee": base_fran,
        "base_ula_over_5_4m": base_ula,
        "scenarios": {
            "base": base_corp,
            "stagflation": stagflation,
            "soft_landing": soft_landing,
        },
        "expiry_sweep": expiry_sweep,
        "basis_sweep": basis_sweep,
        "term_curve": term_curve,
    }

    out_path = os.path.join(DATA_DIR, "model_output.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"Wrote {out_path} ({N_TRIALS} trials, seed={SEED})")
    for row in base_corp["strategies"]:
        print(f"  {row['id']:25s} CE=${row['ce_2040']:>10,.0f}  Mean=${row['mean_2040']:>10,.0f}  P10=${row['p10_2040']:>10,.0f}  IRR={row['median_irr_pct']:.2f}%")


if __name__ == "__main__":
    main()
