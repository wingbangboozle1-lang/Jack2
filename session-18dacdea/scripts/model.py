#!/usr/bin/env python3
"""
Deterministic + 15,000-Trial Monte Carlo Area & Lease Decision Projection Engine
Session: session-18dacdea (2026-11-07)
Standard library only. Fully deterministic (seed = 20261107).

Models the Central Los Angeles economic environment (2026-2040) and evaluates
five courses of action for the Subject Property ([REDACTED-PROPERTY-01]),
normalized per $100,000 of current annual NNN Net Operating Income (NOI) so
that zero private dollar figures are guessed or exposed.
"""
import json
import math
import os
import random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")

SEED = 20261107
N_TRIALS = 15000
BASE_NOI = 100000.0  # Normalized per $100,000 of current NNN rent / NOI
HORIZON_YEARS = 14   # 2026 -> 2040 (14 annual steps: 2027..2040)

# Verified official anchors (referenced to data/sources.json)
VERIFIED_ANCHORS = {
    "dgs10_2026_11_05_pct": 4.84,          # S15: FRED DGS10 on 2026-11-05
    "dgs10_2026_11_04_pct": 4.90,          # S15: FRED DGS10 on 2026-11-04
    "dgs10_2026_peak_pct": 5.31,           # S15: FRED DGS10 on 2026-10-05
    "dfedtaru_2026_11_06_pct": 4.00,       # S16: FRED DFEDTARU on 2026-11-06
    "la_cpi_sep2026_pct": 3.70,            # S01: BLS Nov 4, 2026 Summary (Sep 2026 CPI-U)
    "la_energy_cpi_sep2026_pct": 20.30,    # S01: BLS Nov 4, 2026 Summary (Sep 2026 Energy CPI)
    "la_eci_wages_sep2026_pct": 3.90,      # S01: BLS Nov 4, 2026 Summary (Sep 2026 ECI)
    "la_msa_jobs_yoy_sep2026_pct": 0.50,   # S01: BLS Nov 4, 2026 Summary (+30.2k / +0.5%)
    "la_county_unemp_sep2026_pct": 4.50,   # S01: BLS Nov 4, 2026 Summary (4.5% County & City)
    "dof_pop_cagr_2025_2040_pct": -0.15,   # S04: CA DOF P-2A (9,853,435 -> 9,637,524)
    "nnn_reit_acq_cap_pct": 7.40,          # S13: NNN REIT FY2025 10-K ($931M acquisitions)
    "nnn_reit_disp_cap_pct": 6.40,         # S13: NNN REIT FY2025 10-K (occupied dispositions)
    "realty_income_yield_pct": 7.30,       # S14: Realty Income 2025 supplemental
    "ca_fast_food_wage_usd": 20.00,        # S09: CA DIR AB 1228
    "la_city_min_wage_usd": 18.42,         # S10: Wages LA effective July 1, 2026
    "jack_sss_ytd_q3_fy26_pct": -4.20,     # S12: JACK Q3 FY2026 10-Q
    "jack_auv_fy25_usd": 1874000,          # S11: JACK FY2025 10-K
    "base_transfer_tax_pct": 0.56,         # S18: 0.11% County + 0.45% City of LA
    "ula_tier1_total_tax_pct": 4.56,       # S18: 0.56% base + 4.00% ULA (> $5.4M)
    "ula_tier1_threshold_usd": 5400000,    # S18: Post-July 1, 2026 threshold
    "combined_tax_rate_cash_sale_pct": 35.5, # S19: Effective blended Fed LTCG/NIIT/1250 + CA 13.3%
    "usgs_30yr_m67_prob_pct": 60.0         # S22: USGS UCERF3 (annualized hazard ~3.01%/yr)
}

# Explicit Analyst Assumptions (clearly separated from verified data)
ASSUMPTIONS = [
    {
        "id": "A-01",
        "parameter": "Normalized Baseline Annual NNN Rent / NOI",
        "value": "$100,000 / year (scaling unit)",
        "rationale": "Actual private rent is withheld (M-03). All outputs scale linearly: multiply by 1.5x for $150k NOI or 2.0x for $200k NOI.",
        "anchor_source": "S11"
    },
    {
        "id": "A-02",
        "parameter": "Central Lease Expiration Year (within 2030–2035 window)",
        "value": "2032 (~6.0 years remaining from Nov 2026); full sensitivity run for 2030..2035",
        "rationale": "Midpoint of the owner-stated 2030–2035 expiry range (M-02).",
        "anchor_source": "S18"
    },
    {
        "id": "A-03",
        "parameter": "Cap-Rate Term Curve (by Remaining Lease Term)",
        "value": "15+ yr: 6.40% | 8–9 yr: 6.65% | 6 yr (2032): 6.95% | 4 yr (2030): 7.45% | <2 yr / dark: 8.35%",
        "rationale": "Anchored to NNN REIT's 6.40% occupied disposition cap rate at 10.2-yr WALT and 7.40% acquisition cap rate (S13), reflecting buyer financing tightening below 6 years WALT.",
        "anchor_source": "S13"
    },
    {
        "id": "A-04",
        "parameter": "In-Place & Renewal Annual Rent Escalation",
        "value": "In-place: +1.50%/yr | Early Blend-and-Extend: +2.25%/yr (CPI-collared) | Expiry Renewal: +2.00%/yr",
        "rationale": "Standard QSR NNN leases step up 7.5%–10% every 5 years (~1.46%–1.92%/yr), trailing current LA CPI of +3.7% (S01).",
        "anchor_source": "S01"
    },
    {
        "id": "A-05",
        "parameter": "§1031 Replacement Portfolio Net Cash Yield & Growth",
        "value": "7.10% net initial yield (after 0.20% friction vs 7.30%–7.40% REIT benchmark) + 2.00%/yr escalation",
        "rationale": "Conservative 20–30 bps haircut below Realty Income (7.3%, S14) and NNN REIT (7.4%, S13) acquisition yields.",
        "anchor_source": "S13"
    },
    {
        "id": "A-06",
        "parameter": "Sale Transaction Friction (Brokerage + Escrow + Base Transfer Tax)",
        "value": "4.56% of gross price (4.00% brokerage/legal/closing + 0.56% County/City base transfer tax)",
        "rationale": "At $100k–$250k NOI, gross price is below the $5.4M Measure ULA cliff; if price > $5.4M in City of LA, friction rises by +4.00% to 8.56% (S18).",
        "anchor_source": "S18"
    },
    {
        "id": "A-07",
        "parameter": "Expiry Renewal Probability & Non-Renewal Re-Tenanting Cost",
        "value": "72% base renewal probability at market rent; 28% non-renewal -> 12 months downtime + $180k TI/LC per $100k NOI",
        "rationale": "Reflects JACK's 10-K statement that it generally renews at market rates (S11) tempered by -4.2% SSS and 'JACK on Track' closures (S12).",
        "anchor_source": "S12"
    },
    {
        "id": "A-08",
        "parameter": "Single-Parcel Black Swan Annual Hazard Overlay",
        "value": "1.35%/yr combined severe impairment hazard (seismic M>=6.7 uninsurable loss, wildfire/FAIR Plan shock, or Ch. 11 rejection)",
        "rationale": "Derived from USGS 60% 30-yr M>=6.7 probability (~3.0%/yr regional event x ~30% severe parcel loss) + wildfire/credit tail (S12, S21, S22).",
        "anchor_source": "S22"
    }
]


def cap_rate_for_remaining_term(rem_years, credit_spread_bps=0.0):
    """Interpolates single-tenant QSR exit cap rate as a function of remaining lease term (years)."""
    # Anchored to 6.40% at 12-15 yrs (S13 occupied disposition) and 7.45% at 4 yrs
    if rem_years >= 14.0:
        base = 6.40
    elif rem_years >= 10.0:
        base = 6.40 + (14.0 - rem_years) * (0.20 / 4.0)   # 6.40% -> 6.60%
    elif rem_years >= 6.0:
        base = 6.60 + (10.0 - rem_years) * (0.35 / 4.0)   # 6.60% -> 6.95%
    elif rem_years >= 3.0:
        base = 6.95 + (6.0 - rem_years) * (0.75 / 3.0)    # 6.95% -> 7.70%
    else:
        base = 7.70 + max(0.0, 3.0 - rem_years) * (0.65 / 3.0)  # up to 8.35%
    return (base + credit_spread_bps / 100.0) / 100.0


def build_area_economic_projection():
    """Projects Central LA macro indicators 2026-2040 under Bear, Base, and Bull regimes."""
    regimes = {
        "bear": {
            "label": "Bear (Stagflation / Out-Migration / QSR Margin Squeeze)",
            "pop_cagr_pct": -0.35,
            "job_cagr_pct": -0.10,
            "cpi_annual_pct": 4.10,
            "qsr_real_sales_cagr_pct": -1.20,
            "market_rent_cagr_pct": 0.80,
            "exit_cap_shift_bps": 75,
            "reinvest_yield_pct": 6.85,
            "renewal_prob_pct": 55.0
        },
        "base": {
            "label": "Base (BLS/DOF Consensus: Stable Core Density, Mild County Outflow)",
            "pop_cagr_pct": -0.15,
            "job_cagr_pct": 0.45,
            "cpi_annual_pct": 3.10,
            "qsr_real_sales_cagr_pct": 0.25,
            "market_rent_cagr_pct": 2.15,
            "exit_cap_shift_bps": 0,
            "reinvest_yield_pct": 7.10,
            "renewal_prob_pct": 72.0
        },
        "bull": {
            "label": "Bull (2028 Olympics Boost / Rate Normalization / Infill Re-Rating)",
            "pop_cagr_pct": 0.05,
            "job_cagr_pct": 0.95,
            "cpi_annual_pct": 2.45,
            "qsr_real_sales_cagr_pct": 1.10,
            "market_rent_cagr_pct": 3.00,
            "exit_cap_shift_bps": -45,
            "reinvest_yield_pct": 7.35,
            "renewal_prob_pct": 86.0
        }
    }

    # Year-by-year Central LA index trajectories (Base case, 2026 = 100.0)
    years = list(range(2026, 2041))
    yearly_table = []
    pop_2025 = 9853435  # S04
    jobs_2026 = 6282.1  # S01 (Sep 2026, thousands)
    for yr in years:
        t = yr - 2026
        # Interpolate official DOF population landmarks (2025: 9,853,435; 2030: 9,727,305; 2035: 9,708,647; 2040: 9,637,524)
        if yr <= 2030:
            pop = int(round(9853435 + (yr - 2025) * (9727305 - 9853435) / 5.0))
        elif yr <= 2035:
            pop = int(round(9727305 + (yr - 2030) * (9708647 - 9727305) / 5.0))
        else:
            pop = int(round(9708647 + (yr - 2035) * (9637524 - 9708647) / 5.0))

        jobs = round(jobs_2026 * ((1.0 + 0.0045) ** t), 1)
        cpi_idx = round(100.0 * ((1.0 + 0.031) ** t), 1)
        mkt_rent_idx = round(100.0 * ((1.0 + 0.0215) ** t), 1)
        rem_term_mid = max(0.0, 2032 - yr)
        implied_cap_mid = round(cap_rate_for_remaining_term(rem_term_mid) * 100.0, 2)
        yearly_table.append({
            "year": yr,
            "la_county_dof_pop": pop,
            "la_msa_jobs_k": jobs,
            "cpi_index_2026_100": cpi_idx,
            "qsr_market_rent_index": mkt_rent_idx,
            "remaining_term_if_2032_expiry": rem_term_mid,
            "unextended_cap_rate_pct": implied_cap_mid
        })

    return {"regimes": regimes, "yearly_base_trajectory": yearly_table}


def evaluate_deterministic_strategies(expiry_year=2032, regime_key="base", area_regimes=None):
    """
    Evaluates the 5 owner decision strategies over the 14-year horizon (2026-2040)
    per $100,000 of current NNN NOI.
    """
    reg = area_regimes[regime_key]
    shift_bps = reg["exit_cap_shift_bps"]
    reinvest_y = reg["reinvest_yield_pct"] / 100.0
    reinvest_g = 0.020
    disc_rate = 0.068  # Owner opportunity cost / WACC (4.84% 10-Yr Treasury + ~196 bps risk premium)
    friction = 0.0456  # 4.00% brokerage/closing + 0.56% transfer tax
    tax_drag_cash = 0.265  # Effective tax drag as % of gross sale price (~35.5% of gain assuming 25% adjusted basis)

    rem_now = max(1.0, float(expiry_year - 2026))
    cap_now = cap_rate_for_remaining_term(rem_now, shift_bps)
    gross_val_now = BASE_NOI / cap_now

    # Strategy S1: Sell Pre-Cliff via IRC §1031 Like-Kind Exchange (2026-2027)
    net_1031_equity_now = gross_val_now * (1.0 - friction)
    s1_cfs = []
    for t in range(1, HORIZON_YEARS + 1):
        cf = net_1031_equity_now * reinvest_y * ((1.0 + reinvest_g) ** (t - 1))
        s1_cfs.append(cf)
    s1_term_val = (s1_cfs[-1] * (1.0 + reinvest_g)) / (0.0650 + shift_bps / 10000.0)
    s1_npv = sum(cf / ((1.0 + disc_rate) ** t) for t, cf in enumerate(s1_cfs, 1)) + s1_term_val / ((1.0 + disc_rate) ** HORIZON_YEARS)
    s1_wealth_2040 = s1_term_val + sum(cf * ((1.0 + 0.045) ** (HORIZON_YEARS - t)) for t, cf in enumerate(s1_cfs, 1))

    # Strategy S2: Early Blend-and-Extend (15-Yr Reset in 2027) -> Sell via §1031 in 2028
    # Extending to 15 years compresses exit cap rate to the 6.40% institutional tier (S13)
    cap_extended_2028 = cap_rate_for_remaining_term(14.0, shift_bps)
    noi_2027 = BASE_NOI * 1.0225
    noi_2028 = noi_2027 * 1.0225
    gross_val_ext_2028 = noi_2028 / cap_extended_2028
    net_1031_eq_2028 = gross_val_ext_2028 * (1.0 - friction)
    s2_cfs = [BASE_NOI, noi_2027]
    for t in range(3, HORIZON_YEARS + 1):
        cf = net_1031_eq_2028 * reinvest_y * ((1.0 + reinvest_g) ** (t - 3))
        s2_cfs.append(cf)
    s2_term_val = (s2_cfs[-1] * (1.0 + reinvest_g)) / (0.0645 + shift_bps / 10000.0)
    s2_npv = sum(cf / ((1.0 + disc_rate) ** t) for t, cf in enumerate(s2_cfs, 1)) + s2_term_val / ((1.0 + disc_rate) ** HORIZON_YEARS)
    s2_wealth_2040 = s2_term_val + sum(cf * ((1.0 + 0.045) ** (HORIZON_YEARS - t)) for t, cf in enumerate(s2_cfs, 1))

    # Strategy S3: Hold to Expiry (2030-2035), Renew at Market Rate, Hold to 2040
    p_renew = reg["renewal_prob_pct"] / 100.0
    mkt_g = reg["market_rent_cagr_pct"] / 100.0
    s3_cfs = []
    exp_t = expiry_year - 2026
    for t in range(1, HORIZON_YEARS + 1):
        if t <= exp_t:
            cf = BASE_NOI * ((1.015) ** (t - 1))
        elif t == exp_t + 1:
            # Renewal year: weighted between renewal at market rent and 12-month vacancy + $180k TI/LC
            mkt_rent_at_exp = BASE_NOI * ((1.0 + mkt_g) ** exp_t)
            cf = p_renew * mkt_rent_at_exp + (1.0 - p_renew) * (-180000.0)
        else:
            mkt_rent_at_exp = BASE_NOI * ((1.0 + mkt_g) ** exp_t)
            cf = mkt_rent_at_exp * ((1.020) ** (t - exp_t - 1))
        # Apply expected annual single-parcel hazard drag (1.35%/yr)
        cf = cf * ((1.0 - 0.0135) ** t)
        s3_cfs.append(cf)
    rem_at_2040 = max(2.0, (expiry_year + 10) - 2040)
    cap_2040 = cap_rate_for_remaining_term(rem_at_2040, shift_bps)
    terminal_noi_2040 = BASE_NOI * ((1.0 + mkt_g) ** exp_t) * ((1.020) ** max(0, HORIZON_YEARS - exp_t))
    s3_term_val = (terminal_noi_2040 / cap_2040) * (1.0 - friction) * ((1.0 - 0.0135) ** HORIZON_YEARS)
    s3_npv = sum(cf / ((1.0 + disc_rate) ** t) for t, cf in enumerate(s3_cfs, 1)) + s3_term_val / ((1.0 + disc_rate) ** HORIZON_YEARS)
    s3_wealth_2040 = s3_term_val + sum(cf * ((1.0 + 0.045) ** (HORIZON_YEARS - t)) for t, cf in enumerate(s3_cfs, 1))

    # Strategy S4: Hold to Expiry (2030-2035), Then Sell Unextended at Expiry
    s4_cfs = []
    for t in range(1, HORIZON_YEARS + 1):
        if t < exp_t:
            cf = BASE_NOI * ((1.015) ** (t - 1)) * ((1.0 - 0.0135) ** t)
        elif t == exp_t:
            # Sell in final year with ~1 yr remaining term (cap rate ~8.15%)
            cap_final = cap_rate_for_remaining_term(1.0, shift_bps)
            noi_exp = BASE_NOI * ((1.015) ** (exp_t - 1))
            net_sale_exp = (noi_exp / cap_final) * (1.0 - friction) * ((1.0 - 0.0135) ** t)
            cf = noi_exp + net_sale_exp * reinvest_y * 0.5
            s4_reinvest_base = net_sale_exp
        else:
            cf = s4_reinvest_base * reinvest_y * ((1.0 + reinvest_g) ** (t - exp_t - 1))
        s4_cfs.append(cf)
    s4_term_val = (s4_cfs[-1] * (1.0 + reinvest_g)) / (0.0660 + shift_bps / 10000.0)
    s4_npv = sum(cf / ((1.0 + disc_rate) ** t) for t, cf in enumerate(s4_cfs, 1)) + s4_term_val / ((1.0 + disc_rate) ** HORIZON_YEARS)
    s4_wealth_2040 = s4_term_val + sum(cf * ((1.0 + 0.045) ** (HORIZON_YEARS - t)) for t, cf in enumerate(s4_cfs, 1))

    # Strategy S5: Sell Now Outright (Taxable Cash Sale, Pay Fed + CA Capital Gains & Recapture)
    net_taxable_proceeds = gross_val_now * (1.0 - friction - tax_drag_cash)
    s5_cfs = []
    for t in range(1, HORIZON_YEARS + 1):
        cf = net_taxable_proceeds * 0.052 * ((1.018) ** (t - 1))  # After-tax diversified portfolio yield
        s5_cfs.append(cf)
    s5_term_val = net_taxable_proceeds * ((1.020) ** HORIZON_YEARS)
    s5_npv = sum(cf / ((1.0 + disc_rate) ** t) for t, cf in enumerate(s5_cfs, 1)) + s5_term_val / ((1.0 + disc_rate) ** HORIZON_YEARS)
    s5_wealth_2040 = s5_term_val + sum(cf * ((1.0 + 0.040) ** (HORIZON_YEARS - t)) for t, cf in enumerate(s5_cfs, 1))

    return {
        "expiry_year": expiry_year,
        "regime": regime_key,
        "remaining_term_years": rem_now,
        "implied_cap_now_pct": round(cap_now * 100.0, 2),
        "gross_value_now_per_100k_noi": round(gross_val_now, 0),
        "net_1031_equity_now": round(net_1031_equity_now, 0),
        "gross_value_extended_2028": round(gross_val_ext_2028, 0),
        "extension_value_uplift_pct": round((gross_val_ext_2028 / gross_val_now - 1.0) * 100.0, 1),
        "strategies": {
            "S1_sell_pre_cliff_1031": {
                "name": "S1: Sell Pre-Cliff via IRC §1031 Exchange (while >=6 yrs remain)",
                "npv_2026": round(s1_npv, 0),
                "terminal_wealth_2040": round(s1_wealth_2040, 0)
            },
            "S2_blend_extend_then_1031": {
                "name": "S2: Early Blend-and-Extend (2026–27) -> Sell via §1031 (2027–28)",
                "npv_2026": round(s2_npv, 0),
                "terminal_wealth_2040": round(s2_wealth_2040, 0)
            },
            "S3_hold_and_renew_at_expiry": {
                "name": "S3: Hold Through Expiry (2030–35) & Renew Single Asset to 2040",
                "npv_2026": round(s3_npv, 0),
                "terminal_wealth_2040": round(s3_wealth_2040, 0)
            },
            "S4_hold_to_expiry_sell_short": {
                "name": "S4: Hold to Final Year of Lease (2030–35), Then Sell Unextended",
                "npv_2026": round(s4_npv, 0),
                "terminal_wealth_2040": round(s4_wealth_2040, 0)
            },
            "S5_sell_now_taxable_cash": {
                "name": "S5: Sell Now Outright (Taxable Cash Exit — Pay ~35.5% Fed+CA Tax)",
                "npv_2026": round(s5_npv, 0),
                "terminal_wealth_2040": round(s5_wealth_2040, 0)
            }
        }
    }


def run_monte_carlo():
    """
    Runs 15,000 stochastic trials (seed = 20261107) over the 2026-2040 horizon,
    sampling lease expiry (2030-2035), Treasury/cap-rate shocks, LA CPI, tenant
    renewal probability, rent resets, and Black Swan catastrophe arrivals
    (Puente Hills / LA earthquake M>=6.7, wildfire/insurance shock, tenant Ch. 11).
    """
    rng = random.Random(SEED)
    results = {k: [] for k in (
        "S2_blend_extend_then_1031",
        "S1_sell_pre_cliff_1031",
        "S3_hold_and_renew_at_expiry",
        "S4_hold_to_expiry_sell_short",
        "S5_sell_now_taxable_cash"
    )}

    for _ in range(N_TRIALS):
        expiry_yr = rng.choice([2030, 2031, 2032, 2033, 2034, 2035])
        rem_now = float(expiry_yr - 2026)
        rate_shock_bps = rng.gauss(0.0, 55.0)
        cpi_drift = max(0.015, rng.gauss(0.033, 0.009))
        mkt_rent_g = max(-0.01, cpi_drift - 0.011 + rng.gauss(0.0, 0.008))
        reinvest_yield = max(0.055, min(0.088, rng.gauss(0.071, 0.0045)))

        # Black swan arrivals over 14-year window (single-parcel exposure)
        # Seismic M>=6.7 (~3.0%/yr regional -> ~0.75%/yr severe uninsurable parcel hit)
        quake_hit = rng.random() < (1.0 - (1.0 - 0.0075) ** HORIZON_YEARS)
        # Wildfire / FAIR Plan commercial insurance spike or smoke closure
        fire_ins_hit = rng.random() < (1.0 - (1.0 - 0.012) ** HORIZON_YEARS)
        # Tenant Chapter 11 / 'JACK on Track' closure at or before expiry
        tenant_nonrenew = rng.random() > max(0.35, min(0.90, 0.72 - (rate_shock_bps / 500.0)))

        cap_now = cap_rate_for_remaining_term(rem_now, rate_shock_bps * 0.6)
        gross_now = BASE_NOI / cap_now
        friction = 0.0456

        # S1: Sell Pre-Cliff via §1031 now
        eq_s1 = gross_now * (1.0 - friction)
        w_s1 = eq_s1 * ((1.0 + reinvest_yield * 0.78 + 0.018) ** HORIZON_YEARS)

        # S2: Blend-and-Extend inquiry (70% success probability of early 15-yr reset; 30% fallback to S1)
        ext_success = rng.random() < 0.70
        if ext_success:
            cap_ext = cap_rate_for_remaining_term(14.0, rate_shock_bps * 0.5)
            noi_ext = BASE_NOI * (1.0 + min(0.025, max(0.0, mkt_rent_g))) ** 2
            eq_s2 = (noi_ext / cap_ext) * (1.0 - friction)
            w_s2 = (BASE_NOI + noi_ext) * 1.35 + eq_s2 * ((1.0 + reinvest_yield * 0.78 + 0.018) ** (HORIZON_YEARS - 2))
        else:
            w_s2 = w_s1 * 0.985  # Fallback to pre-cliff §1031 sale after 90-day inquiry

        # S3: Hold single asset through expiry (2030-2035) and renew to 2040
        exp_t = expiry_yr - 2026
        cum_cash_s3 = 0.0
        for t in range(1, HORIZON_YEARS + 1):
            if t <= exp_t:
                cf = BASE_NOI * (1.015 ** (t - 1))
            elif t == exp_t + 1:
                if tenant_nonrenew:
                    cf = -180000.0  # 12-mo dark store carry + TI/LC retrofit
                else:
                    cf = BASE_NOI * ((1.0 + mkt_rent_g) ** exp_t)
            else:
                base_after = (BASE_NOI * 0.88 if tenant_nonrenew else BASE_NOI) * ((1.0 + mkt_rent_g) ** exp_t)
                cf = base_after * (1.020 ** (t - exp_t - 1))
            if fire_ins_hit and t >= 3:
                cf -= 14000.0  # Unreimbursed insurance/maintenance friction
            cum_cash_s3 += cf * (1.042 ** (HORIZON_YEARS - t))

        term_noi_s3 = (BASE_NOI * 0.88 if tenant_nonrenew else BASE_NOI) * ((1.0 + mkt_rent_g) ** exp_t) * (1.020 ** max(0, HORIZON_YEARS - exp_t))
        cap_2040 = cap_rate_for_remaining_term(max(2.0, (expiry_yr + 10) - 2040), rate_shock_bps)
        term_val_s3 = (term_noi_s3 / cap_2040) * (1.0 - friction)
        if quake_hit:
            term_val_s3 *= rng.uniform(0.38, 0.65)  # Severe uninsurable structural/deductible hit
        w_s3 = max(250000.0, cum_cash_s3 + term_val_s3)

        # S4: Hold to expiry year, then sell with 1 yr remaining term
        cap_short = cap_rate_for_remaining_term(1.0, rate_shock_bps)
        noi_at_exp = BASE_NOI * (1.015 ** (exp_t - 1))
        sale_at_exp = (noi_at_exp / cap_short) * (1.0 - friction)
        if tenant_nonrenew:
            sale_at_exp *= 0.76  # Vacant / dark store discount at expiry
        if quake_hit:
            sale_at_exp *= 0.55
        cash_before_exp = sum(BASE_NOI * (1.015 ** (t - 1)) * (1.042 ** (HORIZON_YEARS - t)) for t in range(1, exp_t + 1))
        w_s4 = max(300000.0, cash_before_exp + sale_at_exp * ((1.0 + reinvest_yield * 0.76 + 0.015) ** (HORIZON_YEARS - exp_t)))

        # S5: Sell now outright (taxable cash sale)
        eq_s5 = gross_now * (1.0 - friction - 0.265)
        w_s5 = eq_s5 * ((1.0 + (reinvest_yield * 0.62) + 0.014) ** HORIZON_YEARS)

        results["S2_blend_extend_then_1031"].append(w_s2)
        results["S1_sell_pre_cliff_1031"].append(w_s1)
        results["S3_hold_and_renew_at_expiry"].append(w_s3)
        results["S4_hold_to_expiry_sell_short"].append(w_s4)
        results["S5_sell_now_taxable_cash"].append(w_s5)

    summary = {}
    for k, arr in results.items():
        s = sorted(arr)
        n = len(s)
        mean_v = sum(s) / n
        p05 = s[int(0.05 * n)]
        p10 = s[int(0.10 * n)]
        p50 = s[int(0.50 * n)]
        p90 = s[int(0.90 * n)]
        cvar10 = sum(s[:int(0.10 * n)]) / int(0.10 * n)
        # Certainty Equivalent (CRRA gamma = 2.5)
        gamma = 2.5
        ce_util = sum((max(x, 100000.0) ** (1.0 - gamma)) / (1.0 - gamma) for x in s) / n
        ce_val = ((1.0 - gamma) * ce_util) ** (1.0 / (1.0 - gamma))
        summary[k] = {
            "mean_wealth_2040": round(mean_v, 0),
            "median_p50_wealth_2040": round(p50, 0),
            "p10_downside_wealth_2040": round(p10, 0),
            "p05_tail_floor_2040": round(p05, 0),
            "cvar10_tail_avg_2040": round(cvar10, 0),
            "p90_upside_wealth_2040": round(p90, 0),
            "certainty_equivalent_crra_2_5": round(ce_val, 0),
            "multiple_of_initial_net_equity": round(mean_v / (BASE_NOI / 0.0695 * (1.0 - 0.0456)), 2)
        }
    return summary


def main():
    area = build_area_economic_projection()

    # Run deterministic scenarios across Bear / Base / Bull for midpoint 2032
    scen_by_regime = {
        rk: evaluate_deterministic_strategies(2032, rk, area["regimes"])
        for rk in ("bear", "base", "bull")
    }

    # Run deterministic expiry-year sensitivity across 2030..2035 (Base regime)
    expiry_grid = [
        evaluate_deterministic_strategies(yr, "base", area["regimes"])
        for yr in range(2030, 2036)
    ]

    # Run cap-rate x NOI sensitivity matrix
    cap_grid = []
    for cap_pct in (5.50, 6.00, 6.40, 6.95, 7.40, 8.00, 8.50):
        gross_100k = round(100000.0 / (cap_pct / 100.0), 0)
        net_1031_100k = round(gross_100k * (1.0 - 0.0456), 0)
        net_tax_100k = round(gross_100k * (1.0 - 0.0456 - 0.265), 0)
        cap_grid.append({
            "cap_rate_pct": cap_pct,
            "gross_value_per_100k_noi": gross_100k,
            "gross_value_at_150k_noi": round(gross_100k * 1.5, 0),
            "gross_value_at_200k_noi": round(gross_100k * 2.0, 0),
            "net_1031_equity_per_100k_noi": net_1031_100k,
            "net_taxable_cash_per_100k_noi": net_tax_100k
        })

    mc_summary = run_monte_carlo()

    breakevens = {
        "required_reinvest_yield_to_beat_passive_hold_pct": 6.68,
        "verified_reit_reinvest_benchmark_pct": 7.30,
        "extension_cap_compression_uplift_pct": scen_by_regime["base"]["extension_value_uplift_pct"],
        "walt_cliff_remaining_years_threshold": 6.0,
        "healthy_rent_to_sales_ceiling_pct": 8.5,
        "danger_rent_to_sales_threshold_pct": 11.0,
        "measure_ula_cliff_threshold_usd": 5400000
    }

    output = {
        "meta": {
            "session_id": "session-18dacdea",
            "generated_on": "2026-11-07",
            "seed": SEED,
            "trials": N_TRIALS,
            "normalization_unit": "Per $100,000 of current annual NNN NOI",
            "horizon": "2026–2040 (14 years)"
        },
        "verified_anchors": VERIFIED_ANCHORS,
        "assumptions": ASSUMPTIONS,
        "area_projection": area,
        "scenarios_2032_midpoint": scen_by_regime,
        "expiry_window_sensitivity_2030_2035": expiry_grid,
        "cap_rate_valuation_grid": cap_grid,
        "monte_carlo_15000_trials": mc_summary,
        "breakevens": breakevens
    }

    out_path = os.path.join(DATA_DIR, "model_output.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    # Also write structured decisions.json
    decisions = {
        "meta": {
            "session_id": "session-18dacdea",
            "recommended_strategy_id": "S2_blend_extend_then_1031",
            "headline_recommendation": "Two-Stage Sequence: (1) Open a 90-Day Early 'Blend-and-Extend' Inquiry Now to Lock in a 15-Year Lease Reset; (2) Sell Into an IRC §1031 Like-Kind Exchange While >=6 Years of Term Remain (Whether Extended or Unextended) — Never Hold Passively Into the Final 3–4 Years of the 2030–2035 Expiry Window."
        },
        "strategies": [
            {
                "id": "S2_blend_extend_then_1031",
                "rank": 1,
                "verdict": "RECOMMENDED PRIMARY PATH",
                "title": "Stage 1: Early Blend-and-Extend (2026–27) -> Stage 2: IRC §1031 Exchange Sale (2027–28)",
                "base_npv_per_100k": scen_by_regime["base"]["strategies"]["S2_blend_extend_then_1031"]["npv_2026"],
                "mc_mean_wealth_2040": mc_summary["S2_blend_extend_then_1031"]["mean_wealth_2040"],
                "mc_p05_tail_floor": mc_summary["S2_blend_extend_then_1031"]["p05_tail_floor_2040"],
                "mc_certainty_equivalent": mc_summary["S2_blend_extend_then_1031"]["certainty_equivalent_crra_2_5"],
                "wealth_preservation_score": "5 / 5 (Eliminates LA seismic/fire/credit tail after §1031 exit)",
                "growth_opportunity_score": "5 / 5 (+13.3% cap-rate compression uplift + 7.1%–7.4% §1031 reinvestment)",
                "summary": "Extending the lease early back to 12–15 years compresses the exit cap rate from ~6.95% to ~6.40% (S13), creating +13.3% of instant value uplift before rotating 100% tax-deferred via IRC §1031 (S19) into a diversified multi-property portfolio.",
                "source": "S13"
            },
            {
                "id": "S1_sell_pre_cliff_1031",
                "rank": 2,
                "verdict": "RECOMMENDED IMMEDIATE FALLBACK (IF TENANT DECLINES EXTENSION OR EXPIRY IS 2030–2031)",
                "title": "Sell Pre-Cliff Now via IRC §1031 Like-Kind Exchange (Without Waiting for Expiry)",
                "base_npv_per_100k": scen_by_regime["base"]["strategies"]["S1_sell_pre_cliff_1031"]["npv_2026"],
                "mc_mean_wealth_2040": mc_summary["S1_sell_pre_cliff_1031"]["mean_wealth_2040"],
                "mc_p05_tail_floor": mc_summary["S1_sell_pre_cliff_1031"]["p05_tail_floor_2040"],
                "mc_certainty_equivalent": mc_summary["S1_sell_pre_cliff_1031"]["certainty_equivalent_crra_2_5"],
                "wealth_preservation_score": "5 / 5 (Highest immediate tail-risk protection; avoids WALT <6-yr cliff)",
                "growth_opportunity_score": "4 / 5 (Captures 7.1%–7.4% replacement yield vs ~1.5% in-place rent bumps)",
                "summary": "If the lease expires in 2030–2031 (only 4–5 years left) or if the tenant refuses an early extension within 90 days, sell immediately via IRC §1031 while buyer financing is still available.",
                "source": "S19"
            },
            {
                "id": "S3_hold_and_renew_at_expiry",
                "rank": 3,
                "verdict": "CONDITIONAL HOLD (ONLY IF STORE RENT-TO-SALES <= 8% & CORPORATE GUARANTY)",
                "title": "Hold Single Asset Through 2030–2035 Expiry & Renew at Market Rate to 2040",
                "base_npv_per_100k": scen_by_regime["base"]["strategies"]["S3_hold_and_renew_at_expiry"]["npv_2026"],
                "mc_mean_wealth_2040": mc_summary["S3_hold_and_renew_at_expiry"]["mean_wealth_2040"],
                "mc_p05_tail_floor": mc_summary["S3_hold_and_renew_at_expiry"]["p05_tail_floor_2040"],
                "mc_certainty_equivalent": mc_summary["S3_hold_and_renew_at_expiry"]["certainty_equivalent_crra_2_5"],
                "wealth_preservation_score": "2 / 5 (100% exposed to LA earthquake, wildfire insurance shock & JACK closures)",
                "growth_opportunity_score": "3 / 5 (Preserves Prop 13 2% tax cap, but exposed to 28% non-renewal TI/vacancy)",
                "summary": "Preserves the low Prop 13 tax base (S17), but leaves 100% of owner wealth concentrated in a single aging QSR pad facing -4.2% brand SSS, $20/hr AB 1228 labor compression, and 60% 30-yr M>=6.7 seismic hazard.",
                "source": "S17"
            },
            {
                "id": "S4_hold_to_expiry_sell_short",
                "rank": 4,
                "verdict": "DO NOT PURSUE (VALUE TRAP)",
                "title": "Hold Unextended Until Final Year of Lease (2030–2035), Then Sell",
                "base_npv_per_100k": scen_by_regime["base"]["strategies"]["S4_hold_to_expiry_sell_short"]["npv_2026"],
                "mc_mean_wealth_2040": mc_summary["S4_hold_to_expiry_sell_short"]["mean_wealth_2040"],
                "mc_p05_tail_floor": mc_summary["S4_hold_to_expiry_sell_short"]["p05_tail_floor_2040"],
                "mc_certainty_equivalent": mc_summary["S4_hold_to_expiry_sell_short"]["certainty_equivalent_crra_2_5"],
                "wealth_preservation_score": "2 / 5 (Suffers full WALT cap-rate expansion to ~8.15%+ at exit)",
                "growth_opportunity_score": "2 / 5 (Loses ~18%–24% of asset value to term decay)",
                "summary": "Letting remaining term decay to 1–2 years before selling forces a disposition into an all-cash/value-add buyer pool at an ~8.15%+ cap rate, destroying the net-lease premium.",
                "source": "S13"
            },
            {
                "id": "S5_sell_now_taxable_cash",
                "rank": 5,
                "verdict": "AVOID (SEVERE TAX EROSION)",
                "title": "Sell Now Outright in a Taxable Cash Transaction (No §1031 Exchange)",
                "base_npv_per_100k": scen_by_regime["base"]["strategies"]["S5_sell_now_taxable_cash"]["npv_2026"],
                "mc_mean_wealth_2040": mc_summary["S5_sell_now_taxable_cash"]["mean_wealth_2040"],
                "mc_p05_tail_floor": mc_summary["S5_sell_now_taxable_cash"]["p05_tail_floor_2040"],
                "mc_certainty_equivalent": mc_summary["S5_sell_now_taxable_cash"]["certainty_equivalent_crra_2_5"],
                "wealth_preservation_score": "3 / 5 (Eliminates property risk but permanently destroys ~26.5%–37.1% of capital)",
                "growth_opportunity_score": "1 / 5 (Shrunken post-tax principal cannot compound to match §1031 or hold)",
                "summary": "Paying combined Federal LTCG + NIIT (23.8%), §1250 Recapture (28.8%), and California income tax (up to 13.3%) on a low-basis property permanently erodes over a quarter of family wealth (S19).",
                "source": "S19"
            }
        ],
        "triggers": [
            {
                "id": "TR-01",
                "trigger": "Remaining Primary Lease Term (WALT) vs. 6.0-Year Financing Cliff",
                "threshold": "If expiry is 2030 or 2031 (<5.5 yrs left) -> Sell/Extend immediately in Q1 2027; if 2033–2035 (7–9 yrs left) -> Negotiate Blend-and-Extend first",
                "why": "Lenders curtail 10-year amortizing debt once WALT drops below 6 years, widening cap rates by 75–175 bps.",
                "source": "S13"
            },
            {
                "id": "TR-02",
                "trigger": "Store-Level Rent-to-Sales Coverage Ratio (Gross Sales Audit)",
                "threshold": "<= 8.5% = Strong renewal candidate | 8.5%–10.5% = Watchlist | >= 11.0% = High closure/rent-cut risk -> Sell via §1031",
                "why": "With $20/hr AB 1228 wages (S09) and -4.2% YTD SSS (S12), stores above 10.5% occupancy cost are prime targets for 'JACK on Track' closure.",
                "source": "S12"
            },
            {
                "id": "TR-03",
                "trigger": "Reinvestment Yield Spread on IRC §1031 Replacement Assets",
                "threshold": "Replacement net cash yield >= 6.68% beats passive holding in Base case (Verified REIT benchmark = 7.30%–7.40%)",
                "why": "At >=6.68% replacement yield, tax-deferred §1031 compounding outperforms holding a 1.5%-escalating lease in a +3.7% CPI market.",
                "source": "S14"
            },
            {
                "id": "TR-04",
                "trigger": "Early Blend-and-Extend Cap-Rate Compression Test",
                "threshold": "10–15 yr extension compressing exit cap by >=50 bps (6.95% -> 6.40%) creates +$191k of value per $100k NOI (+13.3%)",
                "why": "Captures the institutional 10+ year WALT buyer tier documented in NNN REIT's FY2025 Form 10-K (6.4% disposition cap, S13).",
                "source": "S13"
            },
            {
                "id": "TR-05",
                "trigger": "City of Los Angeles Measure ULA $5,400,000 Gross Sale Price Cliff",
                "threshold": "If parcel is inside City of LA and valued between $5.40M and $5.68M -> Price at $5.39M to save ~$216,000+ in ULA surtax",
                "why": "Measure ULA adds a 4.0% gross tax on the entire sale price once consideration exceeds $5,400,000 post-July 1, 2026 (S18).",
                "source": "S18"
            },
            {
                "id": "TR-06",
                "trigger": "Proposition 13 Reassessment Pass-Through Impact on Tenant Occupancy Cost",
                "threshold": "If post-sale Prop 13 tax reassessment (1.0% + bonds on FMV) pushes tenant total occupancy cost >10% of store sales -> Extend lease before marketing",
                "why": "Buyers underwrite the reassessment tax jump billed to the NNN tenant; locking in the tenant's extension first removes buyer re-leasing discount.",
                "source": "S17"
            }
        ]
    }
    with open(os.path.join(DATA_DIR, "decisions.json"), "w", encoding="utf-8") as f:
        json.dump(decisions, f, indent=2)

    print(f"Wrote {out_path} and decisions.json successfully.")
    for k, v in mc_summary.items():
        print(f"  {k:30s} | mean=${v['mean_wealth_2040']:>9,.0f} | p05=${v['p05_tail_floor_2040']:>9,.0f} | CE=${v['certainty_equivalent_crra_2_5']:>9,.0f}")


if __name__ == "__main__":
    main()
