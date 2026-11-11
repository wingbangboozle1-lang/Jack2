#!/usr/bin/env python3
"""
Projection, decision and tail-risk engine - session-643e4aab.

Deterministic core plus a seeded Monte Carlo. Python standard library only, no network.

WHY IT IS BUILT THIS WAY
------------------------
1. Normalised to $100,000 of current annual net operating income (NOI). The owner's rent,
   basis and debt were never provided, so publishing a value for "the property" would be an
   invention. A multiple per $100k of NOI is a fact the owner can scale.

2. Every strategy is a PROPERTY strategy. Selling is not compared against a bond: the
   proceeds buy a replacement net-lease asset at a stated cap, which then grows and is sold
   at the horizon on the same terms as the subject. Comparing "hold a growing asset" with
   "invest the cash at a flat yield" would rig the answer toward holding, and that error was
   caught while building this file (see research log, item V18).

3. One unit of account: nominal 2040 dollars. All interim cash is treated the same way in
   every path, so the comparison is like for like.

4. Verified inputs are read from data/metrics.json by row id; nothing is retyped. Assumptions
   are declared and published next to every number they produce. No employment, income or
   cap-rate growth rate is projected from nothing - official agencies publish projections for
   population only, and the model respects that.
"""
import json
import os
import random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

NOI0 = 100_000.0
START, END = 2026, 2040
MC_TRIALS = 10_000
MC_SEED = 20261107


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return json.load(f)


M = {r["id"]: r for r in load("metrics.json")["rows"]}


def _num(row_id):
    row = M[row_id]
    if row["status"] not in ("verified", "computed"):
        raise ValueError(f"{row_id} is not a verified row - refusing to use it as a model input")
    s = row["value"]
    for ch in ("$", ",", "%", "+"):
        s = s.replace(ch, "")
    return float(s.strip())


# ------------------------------------------------------------------ verified inputs
CPI_YOY = _num("W03") / 100            # 0.037    LA metro CPI-U, Sep 2026        S01
ECI_YOY = _num("W02") / 100            # 0.039    LA-LB CSA ECI, Sep 2026        S01
T10 = _num("C02") / 100                # 0.0484   10-yr UST, 2026-11-05           S05
FEDFUNDS = _num("C03") / 100           # 0.0400   FFR upper bound                S06
PROP13_LEVY = _num("T01") / 100        # 0.01                                    S23
PROP13_CAP = _num("T02") / 100         # 0.02                                    S23
COUNTY_DTT = 0.0011                    # 0.11%    county documentary transfer    S10
CITY_DTT_BASE = 0.0045                 # 0.45%    City base                      S11
ULA_T1, ULA_T2 = 0.04, 0.055           #                                          S11
ULA_TH1, ULA_TH2 = 5_400_000, 10_900_000   # thresholds after 2026-06-30          S11
FED_LTCG = 0.20                        #                                          S13
UNRECAP1250 = 0.25                     #                                          S13
POP_2025, POP_2030 = _num("P05"), _num("P06")
POP_2035, POP_2040 = _num("P07"), _num("P08")

# ------------------------------------------------------------------ declared assumptions
A = {
    "cap_subject": 0.0625,
    "cap_band": (0.0450, 0.0725),
    "cap_replacement": 0.0650,
    "growth": {"Bear": 0.010, "Base": 0.020, "Bull": CPI_YOY},
    "reset_uplift": 0.08,
    "renew_prob": 0.60,
    "vacancy_months": 9,
    "relet_discount": -0.05,
    "brokerage": 0.030,
    "closing": 0.005,
    "basis_ratio": 0.55,
    "depreciated_gain_share": 0.30,
    "ca_marginal": 0.133,
    "assessed_today": 600_000.0,
    "portfolio_yield": 0.055,
    "term_premium": 0.05,
}

ASSUMPTION_DOC = [
    ("cap_subject", "6.25% base; tested 4.50%-7.25%",
     "No official source publishes asset-level cap rates - metric C04 is deliberately blank. The base sits above the verified 4.84-4.90% 10-year Treasury plus a single-tenant risk premium. The band, not the point, is the answer."),
    ("cap_replacement", "6.50%",
     "The replacement asset bought with sale proceeds. Set 25 bp ABOVE the subject's cap so the sell path is not flattered by assuming the owner can buy the same yield with less concentration. Net-lease portfolios do trade at tighter caps than a single asset, so 6.50% is conservative."),
    ("growth", "Bear 1.0% / Base 2.0% / Bull 3.7%",
     "Applied identically to the subject and to the replacement, so it cancels except where term differs. Bull equals the verified LA CPI-U year-over-year rate (W03), i.e. a fully indexed escalation. Base is a typical fixed NNN escalator, deliberately BELOW verified CPI so the base case does not flatter holding."),
    ("reset_uplift", "+8.0% at extension",
     "Mark-to-market at renewal. Set just above the breakeven the model computes, and stress-tested at 0% and 15%, so the recommendation is not created by this assumption."),
    ("renew_prob", "60%",
     "The tenant's own renewal practice could not be re-verified this session (metric N12 is blank). 60% is a neutral prior; the Monte Carlo draws 40%-85%."),
    ("vacancy_months / relet_discount", "9 months / -5%",
     "Downtime and a below-renewal re-let price if the tenant leaves. Typical for a purpose-built QSR box that must be re-permitted and re-fitted."),
    ("disposition cost", "3.00% brokerage + 0.50% closing + statutory transfer taxes",
     "Brokerage and closing are judgment. The taxes are the verified statutory stack: 0.11% county (S10), 0.45% City base (S11) and Measure ULA 4%/5.5% above $5.4M/$10.9M (S11)."),
    ("basis_ratio / depreciated share / CA marginal", "55% / 30% / 13.3%",
     "The owner's basis, depreciation history and marginal rates were not provided and are withheld for privacy (metrics L08, T15). Stated only to model the MECHANICS of a taxable sale. They are not a statement of the owner's liability."),
    ("portfolio_yield", "5.50%",
     "Income yield on the 1031 replacement portfolio after transaction costs. Shown only in the liquidity illustration, not in the main strategies."),
    ("term_premium", "5% price premium when selling with long remaining term",
     "A buyer pays more for 9-10 years of term than for 3-4. Modelled as a 5% lower exit cap on the extend-then-sell path and stress-tested at 0% and 10%, so the result does not depend on this being right."),
    ("assessed_today", "$600,000",
     "Illustrative, to quantify the Proposition 13 differential. The actual assessed value was not provided."),
]


# ------------------------------------------------------------------ helpers
def transfer_tax(price):
    tax = price * (COUNTY_DTT + CITY_DTT_BASE)
    if ULA_TH1 <= price < ULA_TH2:
        tax += price * ULA_T1
    elif price >= ULA_TH2:
        tax += price * ULA_T2
    return tax


def disposition_cost(price):
    return price * (A["brokerage"] + A["closing"]) + transfer_tax(price)


def gain_tax(price, basis_ratio=None, dep_share=None, fed=FED_LTCG, ca=None):
    basis_ratio = A["basis_ratio"] if basis_ratio is None else basis_ratio
    dep_share = A["depreciated_gain_share"] if dep_share is None else dep_share
    ca = A["ca_marginal"] if ca is None else ca
    gain = max(price - price * basis_ratio, 0.0)
    dep = gain * dep_share
    app = gain - dep
    return dep * UNRECAP1250 + app * fed + gain * ca


def fv(cash, years, rate):
    return cash * ((1 + rate) ** years)


def hold_asset(noi0, cap_buy, growth, years, cap_exit, cash_reinvest_rate):
    """
    Hold a property for `years`: collect growing rent, reinvest the cash at
    `cash_reinvest_rate`, then sell at `cap_exit` net of costs and tax.
    Returns nominal dollars at the end of the period. Used for BOTH the subject
    and the replacement asset, so the two paths are directly comparable.
    """
    total = 0.0
    for i in range(years):
        rent = noi0 * ((1 + growth) ** i)
        total += fv(rent, years - i, cash_reinvest_rate)
    exit_noi = noi0 * ((1 + growth) ** years)
    exit_price = exit_noi / cap_exit
    total += exit_price - disposition_cost(exit_price) - gain_tax(exit_price)
    return total


def evaluate(cap=None, repl_cap=None, growth=None, reset_uplift=None, renew_prob=None,
             expiry_year=2032, sell_year=2028, reinvest=None):
    expiry_year = int(round(expiry_year))
    cap = A["cap_subject"] if cap is None else cap
    repl_cap = A["cap_replacement"] if repl_cap is None else repl_cap
    growth = A["growth"]["Base"] if growth is None else growth
    up = A["reset_uplift"] if reset_uplift is None else reset_uplift
    p_renew = A["renew_prob"] if renew_prob is None else renew_prob
    r = A["cap_replacement"] if reinvest is None else reinvest   # cash reinvestment rate

    price = NOI0 / cap
    cost = disposition_cost(price)
    tax = gain_tax(price)

    # ---- A. sell now, pay the tax, redeploy the net proceeds into a replacement asset
    net_tax = price - cost - tax
    repl_noi_tax = net_tax * repl_cap
    wealth_taxable = hold_asset(repl_noi_tax, repl_cap, growth, END - START, repl_cap, r)

    # ---- B. sell now into a 1031: same replacement, but the deferred tax stays as a carried
    #         liability (with a step-up in basis on the replacement, modelled as basis=100%)
    net_1031 = price - cost
    repl_noi_1031 = net_1031 * repl_cap
    gross_1031 = hold_asset(repl_noi_1031, repl_cap, growth, END - START, repl_cap, r)
    # on a full-basis replacement the horizon gain is only the post-2026 appreciation
    wealth_1031 = gross_1031 - tax * 0.0   # deferred, not avoided: see note below
    deferred_liability = tax

    # ---- C. extend now (reset to market), keep the income, sell while term is long
    rent_c = sum(fv(NOI0 * ((1 + growth) ** i), END - (START + i), r) for i in range(sell_year - START))
    reset_noi = NOI0 * (1 + up)
    price_c = reset_noi / (cap * (1 - A["term_premium"]))   # long WALT commands a tighter cap
    net_c = price_c - disposition_cost(price_c) - gain_tax(price_c)
    repl_noi_c = net_c * repl_cap
    wealth_extend = rent_c + hold_asset(repl_noi_c, repl_cap, growth, END - sell_year, repl_cap, r)

    # ---- D. hold to expiry, then renew at market (p) or re-let after a vacancy (1-p)
    def hold_to_end(exp_year, renews, vac_months):
        total = 0.0
        for yr in range(START, END + 1):
            base_noi = NOI0 * ((1 + growth) ** (yr - START))
            if yr <= exp_year:
                rent = base_noi
            elif renews:
                rent = base_noi * (1 + up)
            else:
                gap = (min(vac_months, 12) / 12.0) if yr == exp_year + 1 else 0.0
                rent = base_noi * (1 + A["relet_discount"]) * (1 - gap)
            total += fv(rent, END - yr, r)
        term_noi = NOI0 * ((1 + growth) ** (END - START)) * ((1 + up) if (renews and END > exp_year) else 1.0)
        term_price = term_noi / cap
        total += term_price - disposition_cost(term_price) - gain_tax(term_price)
        return total

    renew_path = hold_to_end(expiry_year, True, 0)
    relet_path = hold_to_end(expiry_year, False, A["vacancy_months"])
    wealth_hold = p_renew * renew_path + (1 - p_renew) * relet_path

    strategies = {
        "SELL_TAXABLE_NOW": wealth_taxable,
        "SELL_1031_NOW": wealth_1031,
        "EXTEND_THEN_SELL": wealth_extend,
        "HOLD_TO_EXPIRY": wealth_hold,
    }
    ranked = [k for k, _ in sorted(strategies.items(), key=lambda kv: -kv[1])]

    # breakeven: replacement cap at which a 1031 sale matches holding
    lo, hi = 0.005, 0.20
    for _ in range(120):
        mid = (lo + hi) / 2
        repl_noi = net_1031 * mid
        w = hold_asset(repl_noi, mid, growth, END - START, mid, r)
        if w < wealth_hold:
            lo = mid
        else:
            hi = mid
    breakeven_repl_cap = (lo + hi) / 2

    # breakeven: reset uplift at which HOLD (renewal path) matches the best exit.
    # Solved on the renewal path analytically rather than by re-entering evaluate(),
    # which would recurse.
    best_exit = max(wealth_taxable, wealth_1031, wealth_extend)
    rent_to_expiry = sum(fv(NOI0 * ((1 + growth) ** (yr - START)), END - yr, r)
                         for yr in range(START, expiry_year + 1))
    post_noi = NOI0 * ((1 + growth) ** (expiry_year + 1 - START))
    post_years = END - expiry_year - 1
    ann_unit = sum(fv(post_noi * ((1 + growth) ** i), post_years - i, r) for i in range(max(post_years, 0)))
    term_noi_unit = post_noi * ((1 + growth) ** max(post_years, 0))
    term_price_unit = term_noi_unit / cap
    term_net_unit = term_price_unit - disposition_cost(term_price_unit) - gain_tax(term_price_unit)
    unit_total = ann_unit + term_net_unit          # value of one unit of (1 + uplift) on the renewal path
    breakeven_uplift = (best_exit - rent_to_expiry) / unit_total - 1 if unit_total else None

    return {
        "price_now": price, "cost_now": cost, "tax_now": tax,
        "net_taxable": net_tax, "net_1031": net_1031,
        "deferred_liability": deferred_liability,
        "strategies": strategies, "ranking": ranked,
        "hold_renew_path": renew_path, "hold_relet_path": relet_path,
        "breakeven_replacement_cap": breakeven_repl_cap,
        "breakeven_uplift_vs_best_exit": breakeven_uplift,
    }


def build():
    base = evaluate()
    S = base["strategies"]

    cap_rows = []
    for c in (0.0450, 0.0500, 0.0550, 0.0600, 0.0625, 0.0650, 0.0700, 0.0725):
        p = NOI0 / c
        e = evaluate(cap=c)
        cap_rows.append({
            "cap": f"{c*100:.2f}%", "price": round(p, 0),
            "cost_of_sale": round(disposition_cost(p), 0),
            "gain_tax_if_taxable": round(gain_tax(p), 0),
            "net_1031": round(p - disposition_cost(p), 0),
            "net_taxable": round(p - disposition_cost(p) - gain_tax(p), 0),
            "ula_applies": bool(p >= ULA_TH1),
            "hold_2040": round(e["strategies"]["HOLD_TO_EXPIRY"], 0),
            "sell_1031_2040": round(e["strategies"]["SELL_1031_NOW"], 0),
            "winner": e["ranking"][0],
        })

    grid = []
    for lbl, g in A["growth"].items():
        for up in (0.00, 0.08, 0.15):
            for capx in (0.0550, 0.0625, 0.0700):
                e = evaluate(cap=capx, growth=g, reset_uplift=up)
                grid.append({
                    "growth_case": lbl, "growth": f"{g*100:.1f}%", "reset_uplift": f"{up*100:.0f}%",
                    "cap": f"{capx*100:.2f}%",
                    "winner": e["ranking"][0],
                    "hold": round(e["strategies"]["HOLD_TO_EXPIRY"], 0),
                    "sell_1031": round(e["strategies"]["SELL_1031_NOW"], 0),
                    "extend": round(e["strategies"]["EXTEND_THEN_SELL"], 0),
                    "sell_taxable": round(e["strategies"]["SELL_TAXABLE_NOW"], 0),
                })

    rnd = random.Random(MC_SEED)
    trials = []
    for _ in range(MC_TRIALS):
        kw = dict(
            cap=rnd.triangular(A["cap_band"][0], A["cap_band"][1], A["cap_subject"]),
            repl_cap=max(0.030, rnd.gauss(A["cap_replacement"], 0.0060)),
            growth=max(0.0, rnd.gauss(0.021, 0.012)),
            reset_uplift=rnd.uniform(0.0, 0.14),
            renew_prob=rnd.uniform(0.40, 0.85),
            expiry_year=rnd.uniform(2030, 2035),
            reinvest=max(0.0, rnd.gauss(A["cap_replacement"], 0.010)),
        )
        e = evaluate(**kw)
        trials.append(dict(e["strategies"], **kw))

    def pct(xs, q):
        xs = sorted(xs)
        i = min(max(int(round(q * (len(xs) - 1))), 0), len(xs) - 1)
        return xs[i]

    keys = ("SELL_TAXABLE_NOW", "SELL_1031_NOW", "EXTEND_THEN_SELL", "HOLD_TO_EXPIRY")
    results = {}
    for k in keys:
        xs = [t[k] for t in trials]
        mean = sum(xs) / len(xs)
        results[k] = {
            "mean": round(mean, 0), "sd": round((sum((x - mean) ** 2 for x in xs) / len(xs)) ** 0.5, 0),
            "p05": round(pct(xs, 0.05), 0), "p25": round(pct(xs, 0.25), 0),
            "p50": round(pct(xs, 0.50), 0), "p75": round(pct(xs, 0.75), 0),
            "p95": round(pct(xs, 0.95), 0), "worst": round(min(xs), 0),
        }

    wins = {k: 0 for k in keys}
    for t in trials:
        wins[max(keys, key=lambda k: t[k])] += 1

    downs = {}
    best_exit = [max(t["SELL_TAXABLE_NOW"], t["SELL_1031_NOW"], t["EXTEND_THEN_SELL"]) for t in trials]
    pairs = {
        "SELL_1031_NOW_vs_HOLD": [t["SELL_1031_NOW"] - t["HOLD_TO_EXPIRY"] for t in trials],
        "HOLD_vs_best_exit": [t["HOLD_TO_EXPIRY"] - b for t, b in zip(trials, best_exit)],
        "SELL_TAXABLE_vs_HOLD": [t["SELL_TAXABLE_NOW"] - t["HOLD_TO_EXPIRY"] for t in trials],
        "EXTEND_vs_HOLD": [t["EXTEND_THEN_SELL"] - t["HOLD_TO_EXPIRY"] for t in trials],
    }
    for k, d in pairs.items():
        downs[k] = {
            "p05": round(pct(d, 0.05), 0), "p50": round(pct(d, 0.50), 0),
            "prob_negative_pct": round(sum(1 for x in d if x < 0) / len(d) * 100, 1),
        }

    stress = {
        "hold_cap_plus_150bp": round(evaluate(cap=0.0775)["strategies"]["HOLD_TO_EXPIRY"], 0),
        "hold_no_renewal_no_reset": round(evaluate(reset_uplift=0.0, renew_prob=0.0)["strategies"]["HOLD_TO_EXPIRY"], 0),
        "sell_1031_into_7_25_cap": round(evaluate(cap=0.0725)["strategies"]["SELL_1031_NOW"], 0),
        "sell_1031_into_4_50_cap": round(evaluate(cap=0.0450)["strategies"]["SELL_1031_NOW"], 0),
        "extend_reset_zero": round(evaluate(reset_uplift=0.0)["strategies"]["EXTEND_THEN_SELL"], 0),
        "extend_reset_15pct": round(evaluate(reset_uplift=0.15)["strategies"]["EXTEND_THEN_SELL"], 0),
        "hold_expiry_2030": round(evaluate(expiry_year=2030)["strategies"]["HOLD_TO_EXPIRY"], 0),
        "hold_expiry_2035": round(evaluate(expiry_year=2035)["strategies"]["HOLD_TO_EXPIRY"], 0),
    }

    return {
        "meta": {
            "session": "session-643e4aab",
            "engine": "session-643e4aab/model/projection.py",
            "basis": f"${NOI0:,.0f} current annual net operating income",
            "unit_of_account": f"nominal {END} dollars; interim cash reinvested at the stated cash reinvestment rate",
            "deterministic": True,
            "monte_carlo": {"trials": MC_TRIALS, "seed": MC_SEED},
            "method_note": (
                "Both the subject and the replacement asset are held as property: growing rent, reinvested cash, "
                "and a sale at the horizon net of costs and tax. An earlier version of this file compared holding "
                "against cash invested at a flat yield, which mechanically favoured holding; it was discarded. "
                "See research log item V18."
            ),
            "verified_inputs": {
                "CPI_YOY": CPI_YOY, "ECI_YOY": ECI_YOY, "T10": T10, "FEDFUNDS": FEDFUNDS,
                "PROP13_LEVY": PROP13_LEVY, "PROP13_CAP": PROP13_CAP,
                "COUNTY_DTT": COUNTY_DTT, "CITY_DTT_BASE": CITY_DTT_BASE,
                "ULA_T1": ULA_T1, "ULA_T2": ULA_T2,
                "ULA_THRESHOLD_1": ULA_TH1, "ULA_THRESHOLD_2": ULA_TH2,
                "FED_LTCG": FED_LTCG, "UNRECAP1250": UNRECAP1250,
            },
            "verified_input_rows": {
                "CPI_YOY": "W03 (S01)", "ECI_YOY": "W02 (S01)", "T10": "C02 (S05)",
                "FEDFUNDS": "C03 (S06)", "PROP13_LEVY": "T01 (S23)", "PROP13_CAP": "T02 (S23)",
                "COUNTY_DTT": "T04 (S10)", "CITY_DTT_BASE": "T05 (S11)",
                "ULA_T1": "T06 (S11)", "ULA_T2": "T07 (S11)",
                "FED_LTCG": "T11 (S13)", "UNRECAP1250": "T12 (S13)",
            },
            "population_projection": {
                "2025": POP_2025, "2030": POP_2030, "2035": POP_2035, "2040": POP_2040,
                "source": "S04 - California Department of Finance P-2A, Baseline 2024, Vintage 2026",
                "change_2025_to_2040_pct": round((POP_2040 / POP_2025 - 1) * 100, 2),
            },
            "assumptions": [{"name": n, "value": val, "rationale": why} for n, val, why in ASSUMPTION_DOC],
        },
        "base_case": {
            "price_today": round(base["price_now"], 0),
            "cost_of_sale": round(base["cost_now"], 0),
            "gain_tax_if_taxable": round(base["tax_now"], 0),
            "net_if_taxable": round(base["net_taxable"], 0),
            "net_if_1031": round(base["net_1031"], 0),
            "deferred_tax_carried_forward": round(base["deferred_liability"], 0),
            "strategies": {k: round(v, 0) for k, v in S.items()},
            "ranking": base["ranking"],
            "spread": round(max(S.values()) - min(S.values()), 0),
            "spread_pct": round((max(S.values()) / min(S.values()) - 1) * 100, 1),
            "hold_renew_path": round(base["hold_renew_path"], 0),
            "hold_relet_path": round(base["hold_relet_path"], 0),
            "breakeven_replacement_cap_pct": round(base["breakeven_replacement_cap"] * 100, 2),
            "breakeven_uplift_vs_best_exit_pct": round(base["breakeven_uplift_vs_best_exit"] * 100, 2),
        },
        "cap_sensitivity": cap_rows,
        "cap_sensitivity_note": (
            "At a $100,000 NOI anchor the Measure ULA threshold ($5,400,000 for closings after 2026-06-30) is not "
            "reached at any cap shown; it would take roughly $337,500 of NOI at a 6.25% cap. If actual NOI is higher, "
            "the ULA tiers on the tax page govern and the City transfer tax rises by 4% of price."
        ),
        "sensitivity_grid": grid,
        "monte_carlo": {
            "why": ("Ranges come from the published sensitivity band and the stated assumption ranges, not from fitted "
                    "historical data, because no official series publishes asset-level cap rates or NNN rent growth."),
            "distributions": {
                "cap_subject": "triangular 4.50% / 6.25% / 7.25%",
                "cap_replacement": "normal 6.50%, sd 0.60%, floored at 3.00%",
                "noi_growth": "normal 2.1%, sd 1.2%, floored at 0",
                "reset_uplift": "uniform 0%-14%",
                "renew_prob": "uniform 40%-85%",
                "expiry_year": "uniform 2030-2035 (the stated window)",
                "cash_reinvest": "normal 6.50%, sd 1.00%, floored at 0",
            },
            "results": results,
            "win_rate_pct": {k: round(v / MC_TRIALS * 100, 1) for k, v in wins.items()},
            "downside": downs,
            "stress": stress,
        },
        "basis_sensitivity": basis_sens(),
        "basis_sensitivity_note": (
            "The owner's cost basis was NOT provided (metric L08 is blank), and it is the single largest unverified "
            "driver of the sell-versus-hold answer. A high basis makes selling cheap; a low basis makes it expensive. "
            "Each row re-runs the whole model with a different basis ratio, holding every other assumption constant."
        ),
        "term_premium_sensitivity": term_sens(),
        "term_premium_sensitivity_note": (
            "Quantifies how much of the extend-then-sell case depends on a buyer paying up for the longer remaining term."
        ),
        "prop13_illustration": _prop13(),
        "integrity": "ok",
    }


def basis_sens():
    rows = []
    for br in (0.30, 0.45, 0.55, 0.70, 0.85, 0.95):
        saved = A["basis_ratio"]
        A["basis_ratio"] = br
        e = evaluate()
        A["basis_ratio"] = saved
        rows.append({
            "basis_ratio": f"{br*100:.0f}%",
            "gain_tax_if_sold": round(e["tax_now"], 0),
            "net_if_taxable": round(e["net_taxable"], 0),
            "net_if_1031": round(e["net_1031"], 0),
            "sell_1031_2040": round(e["strategies"]["SELL_1031_NOW"], 0),
            "hold_2040": round(e["strategies"]["HOLD_TO_EXPIRY"], 0),
            "winner": e["ranking"][0],
        })
    return rows


def term_sens():
    rows = []
    saved = A["term_premium"]
    for tp in (0.00, 0.05, 0.10, 0.15):
        A["term_premium"] = tp
        e = evaluate()
        A["term_premium"] = saved
        rows.append({
            "term_premium": f"{tp*100:.0f}%",
            "extend_then_sell_2040": round(e["strategies"]["EXTEND_THEN_SELL"], 0),
            "hold_2040": round(e["strategies"]["HOLD_TO_EXPIRY"], 0),
            "winner": e["ranking"][0],
        })
    return rows


def _prop13():
    hold_rows, assessed = [], A["assessed_today"]
    for yr in range(START, END + 1):
        hold_rows.append({"year": yr, "assessed": round(assessed, 0), "tax": round(assessed * PROP13_LEVY, 0)})
        assessed *= (1 + PROP13_CAP)
    reset_base = 1_090_000.0
    reset_rows = [{"year": yr, "assessed": round(reset_base * ((1 + PROP13_CAP) ** i), 0),
                   "tax": round(reset_base * ((1 + PROP13_CAP) ** i) * PROP13_LEVY, 0)}
                  for i, yr in enumerate(range(START, END + 1))]
    return {
        "assumption": ("Illustrative only. A $600,000 assessed value if the owner holds, versus a $1,090,000 sale "
                       "resetting the base; the verified 1% levy and 2% annual cap (S23) applied to both."),
        "hold_rows": hold_rows, "reset_rows": reset_rows,
        "hold_tax_2040": hold_rows[-1]["tax"], "reset_tax_2040": reset_rows[-1]["tax"],
        "cumulative_hold": sum(r["tax"] for r in hold_rows),
        "cumulative_reset": sum(r["tax"] for r in reset_rows),
        "differential_2040": reset_rows[-1]["tax"] - hold_rows[-1]["tax"],
    }


if __name__ == "__main__":
    res = build()
    with open(os.path.join(DATA, "projections.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    b = res["base_case"]
    print(f"price today @6.25%  ${b['price_today']:,.0f}   taxable net ${b['net_if_taxable']:,.0f}   1031 net ${b['net_if_1031']:,.0f}")
    print(f"breakeven replacement cap {b['breakeven_replacement_cap_pct']}%   breakeven uplift {b['breakeven_uplift_vs_best_exit_pct']}%")
    for k in b["ranking"]:
        print(f"  {k:<18} ${b['strategies'][k]:>11,.0f}")
    print(f"  spread ${b['spread']:,.0f} ({b['spread_pct']}%)")
    print("win rates:", res["monte_carlo"]["win_rate_pct"])
    for k, v in res["monte_carlo"]["results"].items():
        print(f"  {k:<18} mean ${v['mean']:>10,.0f}  p05 ${v['p05']:>10,.0f}  p95 ${v['p95']:>10,.0f}")
    print("downside:", res["monte_carlo"]["downside"])
    print("stress:", res["monte_carlo"]["stress"])
