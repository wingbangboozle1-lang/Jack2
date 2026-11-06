#!/usr/bin/env python3
"""
Jack2 — Projection engine for PROP-001
(single-tenant NNN Jack in the Box, central Los Angeles, lease expiring 2030-2035).

PURPOSE
    Rank five mutually exclusive courses of action by expected wealth to the Owner,
    under explicit, published assumptions with a Monte-Carlo overlay for
    business-as-usual and black-swan events.

DESIGN RULES
    1. Nothing here is a fact about the property. Every input is either
         (T) traceable to a verified official source listed in research/, or
         (D) arithmetic on T inputs, or
         (A) an assumption, explicitly labelled and published on the Method page.
    2. Results are normalised to CURRENT ANNUAL NOI = 1.00 so the Owner's actual rent
       is never disclosed. Multiply any output by actual NOI to obtain dollars.
    3. Tax symmetry is enforced: a strategy that defers tax carries a *contingent tax
       liability* which is deducted from economic net worth. Otherwise deferral would
       masquerade as free money.
    4. Deterministic: standard library only, fixed seed => identical output.

RUN
    python3 model/projection_model.py            # writes docs/data/projections.json
"""

from __future__ import annotations

import json
import math
import os
import random
import statistics

SEED = 20261106
AS_OF = 2026.85                 # 2026-11-06 as a decimal year
# Midpoint of the Owner-stated expiry range 2030-01-01 .. 2035-12-31, expressed as a date.
EXPIRY_MIDPOINT = 2032.997      # 2032-12-31
TERM_NOW = round(EXPIRY_MIDPOINT - AS_OF, 2)   # remaining term today at the midpoint, in years
YEARS_SALE = 2040               # common terminal date: all strategies exit by 2040
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "data")

# ==================================================================================
# 1. VERIFIED ANCHORS (T / D) — do not edit without re-verifying the source
# ==================================================================================
ANCHORS = {
    "tsy10_2026_11_04_pct": 4.90,                  # FRED DGS10
    "tsy10_2026_10_05_peak_pct": 5.31,             # FRED DGS10
    "tsy10_oct2025_avg_pct": 4.06,                 # FRED GS10
    "tsy10_oct2026_avg_pct": 5.13,                 # FRED GS10
    "tsy10_2020_low_avg_pct": 0.62,                # FRED GS10
    "mortgage30_2026_11_05_pct": 7.18,             # FRED MORTGAGE30US
    "fed_funds_2026_09_17_pct": 3.88,              # FRED DFF
    "cpi_yoy_sep2026_pct": round((336.298 / 324.245 - 1.0) * 100.0, 4),   # FRED CPIAUCSL, D
    "qsr_franchisee_cap_q2_2026_pct": 6.85,        # Boulder Group Q2 2026 (T3)
    "qsr_corporate_cap_q2_2026_pct": 5.85,         # Boulder Group Q2 2026 (T3)
    "stnl_all_cap_q3_2026_pct": 6.92,              # Boulder Group Q3 2026 (T3)
    "stnl_all_cap_q2_2026_pct": 6.82,              # Boulder Group Q2 2026 (T3)
    "la_metro_payrolls_sep2026_k": 6282.1,         # FRED SMU06310800000000001
    "la_metro_payrolls_sep2019_k": 6236.7,         # FRED SMU06310800000000001
    "la_metro_payrolls_peak_oct2024_k": 6359.6,    # FRED SMU06310800000000001
    "la_county_u3_sep2026_pct": 4.5,               # FRED CALOSA7URN
    "la_county_pop_chg_2020_2025_pct": -3.2,       # Census QuickFacts V2025
    "unrecaptured_1250_max_pct": 25.0,             # IRS Topic 409
    "fed_ltcg_top_pct": 20.0,                      # IRS Topic 409
    "niit_pct": 3.8,                               # IRS Topic 409 / Topic 559
}

# ==================================================================================
# 2. CAP-RATE TERM CURVE (D — derived from T3 observations; research/03 §3.4)
# ==================================================================================
CAP_TERM_CURVE = [
    (0.0, 10.50),    # (A) vacant / no lease
    (3.0, 9.00),     # (D) near-expiry short-term paper
    (7.0, 7.75),     # (D) the subject asset's current position
    (10.0, 6.85),    # T3 Boulder Group franchisee-QSR average — direct anchor
    (15.0, 6.40),    # (D) full-term franchisee QSR, weaker brand than premium comps
    (30.0, 6.20),    # (D) asymptotic floor
]


def cap_for_term(term_years: float) -> float:
    """Piecewise-linear interpolation of the cap-rate term curve, in percent."""
    if term_years <= CAP_TERM_CURVE[0][0]:
        return CAP_TERM_CURVE[0][1]
    for (x0, y0), (x1, y1) in zip(CAP_TERM_CURVE, CAP_TERM_CURVE[1:]):
        if x0 <= term_years <= x1:
            w = (term_years - x0) / (x1 - x0)
            return y0 + w * (y1 - y0)
    return CAP_TERM_CURVE[-1][1]


# ==================================================================================
# 3. ASSUMPTIONS (A) — every one is published on the Method page
# ==================================================================================
BASE = {
    # --- lease (Owner-stated, document not supplied) ---
    "expiry_year_low": 2030,
    "expiry_year_high": 2035,
    "escalation_pct": 1.5,              # typical NNN fixed bump
    "renewal_prob": 0.70,               # franchised JACK unit in a viable trade area
    "renewal_term_years": 10,
    "renewal_rent_haircut_pct": 4.0,    # concession extracted for signing
    # --- market ---
    "market_rent_growth_pct": 2.5,
    "vacancy_years_if_not_renewed": 1.5,
    "releasing_cost_pct_of_new_rent": 6.0,
    "free_rent_months_if_not_renewed": 3,
    "sale_cost_pct": 3.0,               # commission + closing + transfer tax
    "cap_beta_to_tsy": 0.55,            # bps of cap per 100 bps of 10-yr Treasury
    "tsy_terminal_pct": 4.60,
    "tsy_converge_year": 2030,
    # --- owner / capital ---
    "discount_rate_pct": 8.0,           # after-tax opportunity cost
    "reinvest_return_pct": 8.0,         # equal to discount rate: no free lunch
    # --- tax basis (A: no basis data supplied) ---
    "basis_multiple": 6.0,              # original basis as multiple of current NOI
    "accum_depr_pct_of_basis": 22.0,
    "ca_state_rate_pct": 13.3,
    # --- extension strategy ---
    "extend_target_term_years": 15,
    "extend_term_sd_years": 2.0,
    "extend_rent_change_pct": -2.0,     # concession the franchisor typically extracts
    "extend_rent_change_sd_pct": 2.5,
    "extend_prob": 0.55,                # will the franchisor actually sign 10-15 yrs now?
    "extend_cost_pct": 1.0,             # legal / negotiation / estoppel cost
    # --- land / vacant value ---
    "land_value_multiple": 8.0,         # vacant+shell value as multiple of current NOI (A)
    "land_value_growth_pct": 2.5,
}

HAZARD = {
    "wildfire_annual_prob": 0.04,
    "wildfire_noi_hit": (0.05, 0.25),
    "wildfire_cap_add_bp": (50, 150),
    "seismic_annual_prob": 0.03,
    "seismic_abate_share": (0.20, 0.60),
    "seismic_months": (3, 12),
    "insurance_shock_annual_prob": 0.06,
    "insurance_shock_cap_add_bp": 60,
    "tenant_default_annual_rate": 0.035,
}

# ==================================================================================
# 4. TAX MODULE  (T: IRS Topic 409 rates; A: basis assumptions)
# ==================================================================================
def tax_on_sale(price: float, cfg: dict) -> tuple[float, dict]:
    """Federal + California tax on sale of a depreciated investment property.

    Federal : unrecaptured IRC s.1250 gain up to 25 % (IRS Topic 409);
              remaining long-term capital gain 20 % + 3.8 % NIIT.
    CA      : gain taxed at the top marginal rate; no preferential rate.
    """
    basis = cfg["basis_multiple"]
    accum_depr = basis * cfg["accum_depr_pct_of_basis"] / 100.0
    adj_basis = basis - accum_depr
    total_gain = max(price - adj_basis, 0.0)
    recapture = min(accum_depr, total_gain)
    appreciation = max(total_gain - recapture, 0.0)

    fed_recap = recapture * ANCHORS["unrecaptured_1250_max_pct"] / 100.0
    fed_apprec = appreciation * (ANCHORS["fed_ltcg_top_pct"] + ANCHORS["niit_pct"]) / 100.0
    ca = total_gain * cfg["ca_state_rate_pct"] / 100.0
    tax = fed_recap + fed_apprec + ca
    return tax, {
        "price": round(price, 4),
        "adjusted_basis": round(adj_basis, 4),
        "total_gain": round(total_gain, 4),
        "recapture_1250": round(recapture, 4),
        "appreciation_gain": round(appreciation, 4),
        "fed_recapture_tax": round(fed_recap, 4),
        "fed_appreciation_tax": round(fed_apprec, 4),
        "ca_tax": round(ca, 4),
        "total_tax": round(tax, 4),
        "effective_rate_on_price_pct": round(100.0 * tax / price, 2) if price else 0.0,
    }


# ==================================================================================
# 5. SINGLE-TRIAL ENGINE
# ==================================================================================
STRATS = ["A_sell_now", "A1_sell_now_1031", "B_expire_sell_vacant",
          "C_renew_hold", "D_extend_sell_2028"]
LABELS = {
    "A_sell_now": "A · Sell now, pay tax",
    "A1_sell_now_1031": "A1 · Sell now via §1031",
    "B_expire_sell_vacant": "B · Hold to expiry, sell vacant",
    "C_renew_hold": "C · Renew at expiry, hold to 2040",
    "D_extend_sell_2028": "D · Extend now, sell 2028",
}


def cap_at(year: int, term: float, cfg: dict) -> float:
    """Cap rate (%) in a given year for a given remaining term, after rate drift."""
    converge = cfg["tsy_converge_year"]
    t0 = ANCHORS["tsy10_2026_11_04_pct"]
    if year >= converge:
        tsy = cfg["tsy_terminal_pct"]
    else:
        w = (year - 2026) / max(converge - 2026, 1)
        tsy = t0 + w * (cfg["tsy_terminal_pct"] - t0)
    drift_pct = cfg["cap_beta_to_tsy"] * (tsy - t0)   # bp of cap per 100bp of tsy, in %
    return max(cap_for_term(term) + drift_pct, 3.0)


def sample_params(rng: random.Random, cfg: dict) -> dict:
    """Draw the uncertain market inputs for one Monte-Carlo path (Tier A distributions)."""
    c = dict(cfg)
    # 10-yr Treasury terminal level: base value with 90 bp standard deviation
    c["tsy_terminal_pct"] = max(2.5, min(9.0, rng.gauss(cfg["tsy_terminal_pct"], 0.90)))
    # cap-rate beta to rates: empirical range 0.35-0.75
    c["cap_beta_to_tsy"] = rng.uniform(0.35, 0.75)
    # market rent growth post-expiry
    c["market_rent_growth_pct"] = max(-2.0, rng.gauss(cfg["market_rent_growth_pct"], 1.0))
    # lease escalation is UNKNOWN (document not supplied): draw from plausible set
    c["escalation_pct"] = rng.choice([0.0, 0.0, 1.0, 1.5, 2.0, 2.5, 3.0])
    # transaction costs
    c["sale_cost_pct"] = rng.uniform(2.5, 4.5)
    # land / vacant value multiple
    c["land_value_multiple"] = max(4.0, rng.uniform(6.0, 10.0))
    # extension: term actually achievable and rent actually conceded
    c["extend_target_term_years"] = max(8.0, min(20.0, rng.gauss(cfg["extend_target_term_years"],
                                                                 cfg["extend_term_sd_years"])))
    c["extend_rent_change_pct"] = rng.gauss(cfg["extend_rent_change_pct"], cfg["extend_rent_change_sd_pct"])
    return c


def run_trial(rng: random.Random, cfg: dict, hazards: bool = True, resample: bool = True) -> dict:
    if resample:
        cfg = sample_params(rng, cfg)
    disc = cfg["discount_rate_pct"] / 100.0
    reinv = cfg["reinvest_return_pct"] / 100.0
    sc = cfg["sale_cost_pct"] / 100.0
    esc = cfg["escalation_pct"] / 100.0
    mg = cfg["market_rent_growth_pct"] / 100.0
    expiry = rng.uniform(cfg["expiry_year_low"], cfg["expiry_year_high"]) + rng.random()
    renewed = rng.random() < cfg["renewal_prob"]

    # ---- hazard overlay ------------------------------------------------------
    noi_hit: dict[int, float] = {}
    cap_add: dict[int, float] = {}
    default_year = None
    if hazards:
        if rng.random() < HAZARD["wildfire_annual_prob"]:
            y = rng.randint(2027, 2039)
            noi_hit[y] = 1.0 - rng.uniform(*HAZARD["wildfire_noi_hit"])
            cap_add[y] = rng.uniform(*HAZARD["wildfire_cap_add_bp"]) / 100.0
        if rng.random() < HAZARD["seismic_annual_prob"]:
            y = rng.randint(2027, 2039)
            abate = rng.uniform(*HAZARD["seismic_abate_share"])
            months = rng.randint(*HAZARD["seismic_months"])
            noi_hit[y] = noi_hit.get(y, 1.0) * (1.0 - abate * months / 12.0)
        if rng.random() < HAZARD["insurance_shock_annual_prob"]:
            y = rng.randint(2027, 2039)
            cap_add[y] = cap_add.get(y, 0.0) + HAZARD["insurance_shock_cap_add_bp"] / 100.0
        for y in range(2027, int(min(expiry, 2039)) + 1):
            if rng.random() < HAZARD["tenant_default_annual_rate"]:
                default_year = y
                break

    # ---- contracted rent while the lease is live -----------------------------
    rent: dict[int, float] = {}
    live_rent_at_expiry = 1.0 * (1 + esc) ** (expiry - 2026)
    for y in range(2026, 2041):
        if y <= expiry and (default_year is None or y < default_year):
            rent[y] = (1 + esc) ** (y - 2026)
        elif y > expiry:
            break
        else:
            rent[y] = 0.0

    # ---- post-expiry rent for the "renew and hold" strategy ------------------
    rent_c: dict[int, float] = {}
    for y in range(2026, 2041):
        if y <= expiry and (default_year is None or y < default_year):
            rent_c[y] = (1 + esc) ** (y - 2026)
        elif y > expiry and renewed and default_year is None:
            base = live_rent_at_expiry * (1 - cfg["renewal_rent_haircut_pct"] / 100.0)
            rent_c[y] = base * (1 + mg) ** (y - expiry)
        else:
            rent_c[y] = 0.0

    def hazardised(path: dict[int, float]) -> dict[int, float]:
        return {y: path.get(y, 0.0) * noi_hit.get(y, 1.0) for y in range(2026, 2041)}

    cf_base = hazardised(rent)
    cf_c = hazardised(rent_c)
    sale_costs = sc

    def value_from(noi: float, year: int, term: float) -> float:
        cap = cap_at(year, term, cfg) + cap_add.get(year, 0.0)
        return max(noi, 1e-6) / (cap / 100.0)

    def pv_flows(cf: dict[int, float], upto: int) -> float:
        return sum(cf[y] / (1 + disc) ** (y - 2026) for y in cf if y <= upto)

    # ---------------- A: SELL NOW, PAY TAX ----------------
    price_a = value_from(cf_base[2026], 2026, expiry - AS_OF)
    net_a = price_a * (1 - sale_costs)
    tax_a, detail_a = tax_on_sale(net_a, cfg)
    wealth_a = (net_a - tax_a) * (1 + reinv) ** (YEARS_SALE - 2026)
    npv_a = cf_base[2026] + wealth_a / (1 + disc) ** (YEARS_SALE - 2026)

    # ---------------- A1: SELL NOW VIA 1031, DEFER ----------------
    # Deferred tax liability is deducted so deferral is not free money.
    dti_a1 = tax_a * (1 + 0.02) ** (YEARS_SALE - 2026)     # liability carried forward (A)
    wealth_a1 = (net_a * (1 + reinv) ** (YEARS_SALE - 2026)) - dti_a1
    npv_a1 = cf_base[2026] + wealth_a1 / (1 + disc) ** (YEARS_SALE - 2026)

    # ---------------- B: HOLD TO EXPIRY, SELL VACANT ----------------
    sale_b = int(round(expiry))
    cf_b = pv_flows(cf_base, sale_b)
    land_b = cfg["land_value_multiple"] * (1 + cfg["land_value_growth_pct"] / 100.0) ** (sale_b - 2026)
    net_b = land_b * (1 - sale_costs)
    tax_b, _ = tax_on_sale(net_b, cfg)
    wealth_b = (net_b - tax_b) * (1 + reinv) ** (YEARS_SALE - sale_b)
    npv_b = cf_b + wealth_b / (1 + disc) ** (YEARS_SALE - 2026)

    # ---------------- C: RENEW AT EXPIRY, HOLD TO 2040 ----------------
    cf_c_pv = pv_flows(cf_c, YEARS_SALE)
    term_at_2040 = max(expiry + cfg["renewal_term_years"] - YEARS_SALE, 0.25)
    price_c = value_from(cf_c[YEARS_SALE], YEARS_SALE, term_at_2040)
    net_c = price_c * (1 - sale_costs)
    tax_c, _ = tax_on_sale(net_c, cfg)
    wealth_c = net_c - tax_c
    npv_c = cf_c_pv + wealth_c / (1 + disc) ** (YEARS_SALE - 2026)

    # ---------------- D: EXTEND NOW, SELL 2028 ----------------
    # Extension is NOT certain: if the franchisor declines, the Owner falls back to
    # selling an unextended asset (i.e. essentially strategy A).
    agreed = rng.random() < cfg["extend_prob"]
    if agreed:
        rent_d = 1.0 * (1 + cfg["extend_rent_change_pct"] / 100.0)
        ext_term = cfg["extend_target_term_years"]
    else:
        rent_d = 1.0
        ext_term = max(expiry - AS_OF, 0.25)
    ev = 2028
    remaining_d = max(ext_term - (ev - 2026), 0.25)
    price_d = value_from(rent_d, ev, remaining_d)
    net_d = price_d * (1 - sale_costs)
    net_d *= (1 - (cfg["extend_cost_pct"] / 100.0 if agreed else 0.0))
    tax_d, _ = tax_on_sale(net_d, cfg)
    cf_d = pv_flows(cf_base, ev - 1) + cf_base[ev] / (1 + disc) ** (ev - 2026)
    wealth_d = (net_d - tax_d) * (1 + reinv) ** (YEARS_SALE - ev)
    npv_d = cf_d + wealth_d / (1 + disc) ** (YEARS_SALE - 2026)

    return {
        "expiry": expiry, "renewed": renewed, "defaulted": default_year is not None,
        "cap_now_pct": cap_at(2026, expiry - AS_OF, cfg),
        "A_sell_now": npv_a, "A1_sell_now_1031": npv_a1,
        "B_expire_sell_vacant": npv_b, "C_renew_hold": npv_c, "D_extend_sell_2028": npv_d,
        "w_A": wealth_a, "w_A1": wealth_a1, "w_B": wealth_b, "w_C": wealth_c, "w_D": wealth_d,
        "detail_A": detail_a, "extend_agreed": agreed,
    }


# ==================================================================================
# 6. AGGREGATION
# ==================================================================================
def summarise(samples: list[dict], noi_for_dollars: float = 200_000.0) -> dict:
    n = len(samples)
    out: dict = {}
    for k in STRATS:
        v = sorted(s[k] for s in samples)
        out[k] = {
            "label": LABELS[k],
            "mean": statistics.fmean(v),
            "p10": v[int(0.10 * n)], "p50": v[int(0.50 * n)], "p90": v[int(0.90 * n)],
            "min": v[0], "max": v[-1],
            "win_rate_pct": 100.0 * sum(1 for s in samples if s[k] == max(s[j] for j in STRATS)) / n,
            "beat_A_pct": 100.0 * sum(1 for s in samples if s[k] > s["A_sell_now"]) / n,
        }
    # ---- risk-adjusted statistics ----
    for k in STRATS:
        v = sorted(s[k] for s in samples)
        mu = statistics.fmean(v)
        sd = statistics.pstdev(v)
        tail = v[: max(1, int(0.10 * n))]
        cvar10 = statistics.fmean(tail)
        # certainty equivalent under CRRA utility U(w)=w^(1-g)/(1-g), normalised
        gamma = 3.0
        # E[w^(1-g)] ; CE = E[w^(1-g)]^(1/(1-g))  (positive for g>1)
        acc = math.fsum(max(w, 0.05) ** (1 - gamma) for w in v) / n
        ce = acc ** (1.0 / (1 - gamma))
        out[k].update({
            "stdev": sd,
            "cvar_10pct": cvar10,
            "return_over_sd": mu / sd if sd else 0.0,
            "certainty_equiv_crra3": ce,
            "downside_vs_A_worst10": cvar10 - out["A_sell_now"]["cvar_10pct"] if "cvar_10pct" in out["A_sell_now"] else None,
        })
    # second pass for the A-relative downside now that cvar exists
    a_cvar = out["A_sell_now"]["cvar_10pct"]
    a_ce = out["A_sell_now"]["certainty_equiv_crra3"]
    for k in STRATS:
        out[k]["cvar_vs_A_pct"] = 100.0 * (out[k]["cvar_10pct"] / a_cvar - 1.0)
        out[k]["ce_vs_A_pct"] = 100.0 * (out[k]["certainty_equiv_crra3"] / a_ce - 1.0)

    a_mean = out["A_sell_now"]["mean"]
    for k in STRATS:
        out[k]["vs_A_pct"] = 100.0 * (out[k]["mean"] / a_mean - 1.0)
        out[k]["dollars_mean"] = out[k]["mean"] * noi_for_dollars
        out[k]["dollars_cvar10"] = out[k]["cvar_10pct"] * noi_for_dollars
    out["_meta"] = {"trials": n, "seed": SEED, "as_of": "2026-11-06",
                    "noi_illustrative": noi_for_dollars,
                    "units": "multiples of current annual NOI, after all taxes"}
    return out


def main() -> None:
    rng = random.Random(SEED)
    samples = [run_trial(rng, BASE) for _ in range(20000)]
    results = summarise(samples)

    # ---- deterministic scenarios ----
    scen_defs = {
        "base": {},
        "upside_for_holding": {"tsy_terminal_pct": 3.80, "market_rent_growth_pct": 3.5, "renewal_prob": 0.85},
        "downside": {"tsy_terminal_pct": 6.50, "market_rent_growth_pct": 1.0, "renewal_prob": 0.45},
        "black_swan": {"tsy_terminal_pct": 6.90, "market_rent_growth_pct": 0.0, "renewal_prob": 0.25,
                       "sale_cost_pct": 4.5, "land_value_multiple": 6.5},
    }
    scenarios = {}
    for name, ov in scen_defs.items():
        cfg = dict(BASE); cfg.update(ov)
        r = random.Random(SEED + 7)
        ss = [run_trial(r, cfg) for _ in range(5000)]
        s = summarise(ss)
        scenarios[name] = {"overrides": ov,
                           "mean": {k: round(s[k]["mean"], 3) for k in STRATS},
                           "vs_A_pct": {k: round(s[k]["vs_A_pct"], 1) for k in STRATS}}

    # ---- hazard on/off control ----
    r = random.Random(SEED + 11)
    ss = [run_trial(r, BASE, hazards=False) for _ in range(8000)]
    no_haz = summarise(ss)

    # ---- discount-rate sensitivity ----
    disc_sens = []
    for d in [6.0, 7.0, 8.0, 9.0, 10.0]:
        cfg = dict(BASE); cfg["discount_rate_pct"] = d; cfg["reinvest_return_pct"] = d
        r = random.Random(SEED + 13)
        ss = [run_trial(r, cfg) for _ in range(4000)]
        s = summarise(ss)
        disc_sens.append({"discount_rate_pct": d,
                          **{k: round(s[k]["mean"], 3) for k in STRATS},
                          "best": max(STRATS, key=lambda k: s[k]["mean"])})

    # ---- expiry-date sensitivity ----
    expiry_sens = []
    for y in range(2030, 2036):
        cfg = dict(BASE); cfg["expiry_year_low"] = y; cfg["expiry_year_high"] = y
        term = y + 1.0 - AS_OF
        cap = cap_for_term(term)
        r = random.Random(SEED + 17)
        ss = [run_trial(r, cfg) for _ in range(3000)]
        s = summarise(ss)
        expiry_sens.append({
            "expiry_year": y, "remaining_term_years": round(term, 2),
            "cap_now_pct": round(cap, 2),
            "value_now_per_1_noi": round(1 / (cap / 100), 2),
            "mean": {k: round(s[k]["mean"], 3) for k in STRATS},
        })

    # ---- term decay ----
    term_decay = []
    for y in range(2026, 2036):
        term = max(EXPIRY_MIDPOINT - (AS_OF if y == 2026 else y), 0.25)
        cap = cap_for_term(term)
        term_decay.append({"year": y, "remaining_term_years": round(term, 2),
                           "cap_pct": round(cap, 2),
                           "value_per_1_noi": round(1 / (cap / 100), 2)})

    # ---- extension uplift (central case uses TERM_NOW, the midpoint of the stated range) ----
    base_cap = cap_for_term(TERM_NOW)
    ext_cap = cap_for_term(BASE["extend_target_term_years"])
    uplift = {
        "cap_now_pct": round(base_cap, 2),
        "cap_after_extension_pct": round(ext_cap, 2),
        "value_now_per_1_noi": round(1 / (base_cap / 100), 2),
        "value_after_per_1_noi": round(1 / (ext_cap / 100), 2),
        "uplift_pct": round(100 * ((1 / (ext_cap / 100)) / (1 / (base_cap / 100)) - 1), 1),
        "uplift_dollars_at_200k_noi": round((1 / (ext_cap / 100) - 1 / (base_cap / 100)) * 200_000),
    }

    # ---- central case: every headline figure derived from one place ----
    cap_now = cap_for_term(TERM_NOW)
    cap_ext = cap_for_term(BASE["extend_target_term_years"])
    cap_end = cap_for_term(0.25)
    val_now = 1 / (cap_now / 100)
    val_ext = 1 / (cap_ext / 100)
    val_end = 1 / (cap_end / 100)
    central = {
        "term_now_years": TERM_NOW,
        "expiry_midpoint": "2032-12-31",
        "cap_now_pct": round(cap_now, 2),
        "value_now_per_1_noi": round(val_now, 2),
        "cap_extended_pct": round(cap_ext, 2),
        "value_extended_per_1_noi": round(val_ext, 2),
        "uplift_pct": round(100 * (val_ext / val_now - 1), 1),
        "uplift_dollars_at_200k_noi": round((val_ext - val_now) * 200_000),
        "cap_final_year_pct": round(cap_end, 2),
        "value_final_year_per_1_noi": round(val_end, 2),
        "term_decay_pct": round(100 * (val_end / val_now - 1), 1),
        "value_lost_to_decay_dollars_at_200k_noi": round((val_end - val_now) * 200_000),
        "value_per_bp_of_cap_dollars_at_200k_noi": round((1 / ((cap_now + 0.55) / 100) - val_now) * 200_000),
        "pct_value_per_55bp_of_cap": round(100 * ((1 / ((cap_now + 0.55) / 100)) / val_now - 1), 1),
    }

    # ---- break-even Treasury level ----
    breakeven = []
    for tsy in [3.5, 4.0, 4.6, 5.0, 5.5, 6.0, 6.5, 7.0]:
        cfg = dict(BASE); cfg["tsy_terminal_pct"] = tsy
        r = random.Random(SEED + 19)
        ss = [run_trial(r, cfg) for _ in range(2500)]
        s = summarise(ss)
        breakeven.append({
            "tsy_terminal_pct": tsy,
            "implied_cap_shift_bp": round(BASE["cap_beta_to_tsy"] * (tsy - 4.90) * 100, 1),
            "A_sell_now": round(s["A_sell_now"]["mean"], 3),
            "C_renew_hold": round(s["C_renew_hold"]["mean"], 3),
            "D_extend_sell_2028": round(s["D_extend_sell_2028"]["mean"], 3),
            "best": max(STRATS, key=lambda k: s[k]["mean"]),
        })

    # ---- illustrative tax waterfall on a sale now ----
    ex = samples[0]["detail_A"]

    extend_rate = 100.0 * sum(1 for x in samples if x.get("extend_agreed")) / len(samples)
    voi = {
        "extend_agreement_rate_pct": round(extend_rate, 1),
        "value_spread_from_expiry_per_1_noi": round(
            expiry_sens[-1]["value_now_per_1_noi"] - expiry_sens[0]["value_now_per_1_noi"], 2),
        "value_spread_from_expiry_pct_of_value": round(
            100 * (expiry_sens[-1]["value_now_per_1_noi"] / expiry_sens[0]["value_now_per_1_noi"] - 1), 1),
        "value_spread_from_expiry_dollars_at_200k_noi": round(
            (expiry_sens[-1]["value_now_per_1_noi"] - expiry_sens[0]["value_now_per_1_noi"]) * 200_000),
    }

    payload = {
        "anchors": ANCHORS,
        "assumptions": BASE,
        "hazard_assumptions": {k: (list(v) if isinstance(v, tuple) else v) for k, v in HAZARD.items()},
        "results": results,
        "scenarios": scenarios,
        "no_hazard": {k: round(no_haz[k]["mean"], 3) for k in STRATS},
        "no_hazard_vs_A_pct": {k: round(no_haz[k]["vs_A_pct"], 1) for k in STRATS},
        "discount_sensitivity": disc_sens,
        "expiry_sensitivity": expiry_sens,
        "term_decay": term_decay,
        "extension_uplift": uplift,
        "central": central,
        "breakeven": breakeven,
        "tax_waterfall_example": ex,
        "value_of_information": voi,
        "cap_term_curve": [{"term_years": t, "cap_pct": round(cap_for_term(t), 2),
                            "value_per_1_noi": round(1 / (cap_for_term(t) / 100), 2)}
                           for t in [0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30]],
        "constants": {"as_of": "2026-11-06", "terminal_year": YEARS_SALE,
                      "noi_illustrative": 200_000},
    }

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "projections.json"), "w") as f:
        json.dump(payload, f, indent=1)

    # ---------- console report ----------
    print("=" * 92)
    print(f"Jack2 projection engine | seed {SEED} | {results['_meta']['trials']} trials | NPV in multiples of current NOI, after ALL taxes")
    print("=" * 92)
    print(f"{'strategy':34s}{'mean':>8s}{'p10':>8s}{'p50':>8s}{'p90':>8s}{'CVaR10':>8s}{'CE':>8s}{'win%':>7s}")
    for k in STRATS:
        x = results[k]
        print(f"{x['label']:34s}{x['mean']:8.3f}{x['p10']:8.3f}{x['p50']:8.3f}{x['p90']:8.3f}{x['cvar_10pct']:8.3f}{x['certainty_equiv_crra3']:8.3f}{x['win_rate_pct']:6.1f}%")
    print()
    print("Risk-adjusted ranking (CRRA=3 certainty equivalent, higher is better):")
    for k in sorted(STRATS, key=lambda z: -results[z]["certainty_equiv_crra3"]):
        print(f"   {results[k]['label']:34s} CE={results[k]['certainty_equiv_crra3']:7.3f}  "
              f"vs A {results[k]['ce_vs_A_pct']:+6.1f}%   worst-10% avg={results[k]['cvar_10pct']:6.3f}")
    print()
    print("Central case:", central)
    print("Extension uplift:", uplift)
    print("Value of resolving the expiry date:", voi)
    print()
    print("Hazard overlay OFF:", {k: round(no_haz[k]['mean'], 3) for k in STRATS})
    print()
    print("Discount-rate sensitivity:")
    for d in disc_sens:
        print(f"  {d['discount_rate_pct']:.0f}%  ->  best = {d['best']}")
    print()
    print("Expiry sensitivity (mean):")
    for e in expiry_sens:
        print(f"  {e['expiry_year']}  term={e['remaining_term_years']:5.2f}  cap={e['cap_now_pct']:5.2f}%  "
              f"A={e['mean']['A_sell_now']:.2f}  C={e['mean']['C_renew_hold']:.2f}  D={e['mean']['D_extend_sell_2028']:.2f}")
    print()
    print("Break-even (Treasury terminal -> best strategy):")
    for b in breakeven:
        print(f"  10y={b['tsy_terminal_pct']:.1f}%  capShift={b['implied_cap_shift_bp']:+.0f}bp  best={b['best']}")
    print()
    print("Wrote", os.path.join(OUT_DIR, "projections.json"))


if __name__ == "__main__":
    main()
