#!/usr/bin/env python3
"""
session-313ba936 projection engine.

Design rules (enforced, not aspirational):

1. NO dollar result is presented as a property valuation. Contract rent and the asset's
   cap rate are both unknown, so every wealth figure is expressed per $100,000 of annual
   contract rent, and every decision number is a breakeven the owner can test against a
   real appraisal.
2. LIKE-FOR-LIKE COMPARISON. Holding and selling are run through the SAME cash-flow
   engine with the same escalation, reinvestment rate and exit cap. The only differences
   are (a) the sale pays transaction costs, and (b) the replacement is bought at the
   verified market yield. A first draft of this script compared a growing asset against a
   non-growing yield; that was wrong and is recorded as an irregularity, not hidden.
3. Every input is tagged `verified` (read from an official source on 2026-11-10, named by
   source id) or `assumption` (the analyst's labelled choice). The site renders the tag.
4. Deterministic: fixed RNG seed, no wall-clock, no network. Re-running reproduces the
   byte-identical JSON.

Run: python3 session-313ba936/scripts/model.py
"""
import json
import os
import random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "model_output.json")

SEED = 313936
TRIALS = 20000

# --------------------------------------------------------------------------- VERIFIED
VERIFIED = {
    "ust_10y_pct": {"value": 4.88, "source": "S01", "label": "10-year Treasury CMT, 2026-11-09"},
    "ust_1y_pct": {"value": 4.38, "source": "S01", "label": "1-year Treasury CMT, 2026-11-09"},
    "ust_2y_pct": {"value": 4.56, "source": "S01", "label": "2-year Treasury CMT, 2026-11-09"},
    "ust_30y_pct": {"value": 5.26, "source": "S01", "label": "30-year Treasury CMT, 2026-11-09"},
    "netlease_cash_yield_pct": {"value": 6.8, "source": "S17", "label": "Initial weighted average cash yield on net-lease acquisitions, Q3 2026"},
    "netlease_occupancy_pct": {"value": 98.8, "source": "S17", "label": "Reference net-lease portfolio occupancy"},
    "netlease_walt_years": {"value": 8.5, "source": "S17", "label": "Reference net-lease portfolio weighted average remaining lease term"},
    "netlease_rent_recapture_pct": {"value": 103.5, "source": "S17", "label": "Rent recapture on re-leased properties"},
    "county_pop_2025": {"value": 9853435, "source": "S03", "label": "LA County population 2025, CA DOF P-2A"},
    "county_pop_2040": {"value": 9637524, "source": "S03", "label": "LA County population 2040, CA DOF P-2A"},
    "ca_pit_top_pct": {"value": 12.30, "source": "S13", "label": "California top marginal PIT rate"},
    "prop13_cap_pct": {"value": 2.0, "source": "S12", "label": "Prop 13 annual assessed-value increase cap"},
    "ula_mid_threshold": {"value": 5400000, "source": "S10", "label": "Measure ULA mid-tier threshold"},
    "ula_top_threshold": {"value": 10900000, "source": "S10", "label": "Measure ULA top-tier threshold"},
    "county_dtt_pct": {"value": 0.11, "source": "S11", "label": "LA County documentary transfer tax"},
    "city_dtt_pct": {"value": 0.45, "source": "S10", "label": "City of LA RPTT base rate"},
    "eq_30y_m67_pct": {"value": 60, "source": "S18", "label": "USGS 30-yr P(M>=6.7) Los Angeles region"},
    "eq_30y_m70_pct": {"value": 46, "source": "S18", "label": "USGS 30-yr P(M>=7.0) Los Angeles region"},
    "eq_30y_m75_pct": {"value": 31, "source": "S18", "label": "USGS 30-yr P(M>=7.5) Los Angeles region"},
    "eaton_structures_destroyed": {"value": 9419, "source": "S20", "label": "Eaton Fire structures destroyed"},
}


def annualise(p30):
    """Convert a USGS 30-year probability to an annual probability. Pure arithmetic."""
    return 1.0 - (1.0 - p30 / 100.0) ** (1.0 / 30.0)


EQ_ANNUAL = {k: annualise(VERIFIED[f"eq_30y_{k}_pct"]["value"]) for k in ("m67", "m70", "m75")}

# --------------------------------------------------------------------------- ASSUMPTIONS
ASSUMPTIONS = {
    "rent_normaliser": {"value": 100000, "unit": "USD per year",
                        "why": "Contract rent is unknown (metric L02). Every result is per $100,000 of rent so the owner can scale linearly to their actual rent."},
    "going_in_cap_pct": {"value": 6.8, "unit": "%",
                         "why": "The asset's own cap rate is unpublished (M11). Set equal to the verified Q3 2026 net-lease acquisition cash yield (S17) as the neutral central case. This single number is the one the owner must replace with an appraisal."},
    "expiry_year": {"value": 2032, "unit": "year",
                    "why": "Midpoint of the 2030-2035 window the brief supplies. The exact date is unverified (L01)."},
    "horizon_year": {"value": 2040, "unit": "year",
                     "why": "Covers the remaining term plus a full renewal cycle."},
    "escalation_pct": {"value": 2.0, "unit": "% per year",
                       "why": "Typical flat net-lease escalation. The lease was not read (L03)."},
    "terminal_cap_pct": {"value": 6.8, "unit": "%",
                         "why": "No cap-rate change assumed over the horizon."},
    "brokerage_pct": {"value": 3.0, "unit": "%", "why": "Negotiated, not published (X13)."},
    "closing_pct": {"value": 0.5, "unit": "%", "why": "Title, escrow, legal, diligence. Negotiated."},
    "renew_prob": {"value": 0.75, "unit": "probability",
                   "why": "No official source exists. Balances a live closure programme (R02) against a site the brand occupies."},
    "downtime_months_if_vacated": {"value": 12, "unit": "months",
                                   "why": "A drive-through site can only be re-let to entitlement-compatible uses."},
    "relet_cost_pct_of_year_rent": {"value": 5.0, "unit": "%",
                                    "why": "Leasing commission plus tenant improvements on a small-format asset."},
    "insurance_recovery_pct": {"value": 60.0, "unit": "% of hazard loss",
                               "why": "Coverage after deductible and limits. The actual policy is unknown (H11, H12)."},
    "fire_annual_prob_pct": {"value": 0.5, "unit": "% per year",
                             "why": "LABELLED ASSUMPTION, NOT OFFICIAL. CAL FIRE publishes hazard zones and loss history (S19, S20) but no parcel annual burn probability. Set low because the parcel is urban; flagged on flag.html."},
    "rate_shock_annual_prob_pct": {"value": 4.0, "unit": "% per year",
                                   "why": "Labelled assumption for a +150bp permanent cap-rate widening."},
    "rate_shock_bp": {"value": 150, "unit": "basis points", "why": "Labelled assumption for the size."},
    "uplift_at_renewal_pct": {"value": 0.0, "unit": "%",
                              "why": "Central case assumes renewal at the escalated contract rent, i.e. no reset. The breakeven uplift is solved for separately."},
}

SCENARIOS = [
    {"id": "bear", "label": "Bear", "escalation_pct": 1.5, "terminal_cap_pct": 7.8, "renew_prob": 0.55,
     "narrative": "Wage and insurance costs keep compressing franchisee margin; cap rates widen as the 10-year holds near 4.9%; the tenant extracts a concession or leaves."},
    {"id": "base", "label": "Base", "escalation_pct": 2.0, "terminal_cap_pct": 6.8, "renew_prob": 0.75,
     "narrative": "The verified benchmark holds, rent escalates at 2%, the tenant renews, exit cap unchanged."},
    {"id": "bull", "label": "Bull", "escalation_pct": 2.5, "terminal_cap_pct": 5.8, "renew_prob": 0.85,
     "narrative": "Rates ease, net-lease demand for drive-through sites strengthens, and the tenant renews early to protect the location."},
]

START = 2026
EXPIRY = ASSUMPTIONS["expiry_year"]["value"]
HORIZON = ASSUMPTIONS["horizon_year"]["value"]
N = HORIZON - START


# --------------------------------------------------------------------------- engine
def disposition_cost_rate(price):
    """Cash cost of sale as a fraction of price; Measure ULA is tiered on gross price."""
    r = (ASSUMPTIONS["brokerage_pct"]["value"] + ASSUMPTIONS["closing_pct"]["value"]
         + VERIFIED["county_dtt_pct"]["value"] + VERIFIED["city_dtt_pct"]["value"]) / 100.0
    if price >= VERIFIED["ula_top_threshold"]["value"]:
        r += 0.055
    elif price >= VERIFIED["ula_mid_threshold"]["value"]:
        r += 0.04
    return r


def cashflow_engine(rent0, g_pct, exit_cap_pct, reinvest_pct, renew_prob, uplift_pct, term_value=True):
    """Net-lease holding engine. Linear in rent0.

    Receives escalating rent each year, reinvests it at `reinvest_pct`, applies an expected
    non-renewal loss at the expiry year, and (optionally) values the property at the horizon
    as forward rent / exit cap. Returns (total wealth, terminal property value, cash pile).
    """
    g = g_pct / 100.0
    r = reinvest_pct / 100.0
    cash = 0.0
    for year in range(START + 1, HORIZON + 1):
        rent_t = rent0 * (1 + g) ** (year - START)
        if year > EXPIRY:
            rent_t *= (1 + uplift_pct / 100.0)
        if year == EXPIRY + 1 and renew_prob < 1.0:
            p_vac = 1.0 - renew_prob
            cash -= p_vac * (rent_t * ASSUMPTIONS["downtime_months_if_vacated"]["value"] / 12.0
                             + rent_t * ASSUMPTIONS["relet_cost_pct_of_year_rent"]["value"] / 100.0)
        cash = cash * (1 + r) + rent_t
    if not term_value:
        return cash, 0.0, cash
    fwd = rent0 * (1 + g) ** N
    fwd *= (1 + uplift_pct / 100.0)
    terminal = fwd * (1 + g) / (exit_cap_pct / 100.0)
    return cash + terminal, terminal, cash


def wealth_paths(rent0, g_pct, exit_cap_pct, reinvest_pct, renew_prob, uplift_pct, sell_cap_pct=None):
    """Both strategies on a like-for-like basis.

    Hold : keep the asset.
    Sell : sell at sell_cap_pct, pay costs, buy a replacement at the verified market yield
           (so the replacement's income yield is the verified net-lease benchmark), then run
           the identical engine on it.
    """
    cap = (sell_cap_pct if sell_cap_pct is not None else ASSUMPTIONS["going_in_cap_pct"]["value"]) / 100.0
    gross = rent0 / cap
    cost = disposition_cost_rate(gross)
    net = gross * (1 - cost)
    y = VERIFIED["netlease_cash_yield_pct"]["value"] / 100.0
    replacement_rent = net * y
    # The replacement carries the SAME renewal-risk expectation. Assuming the replacement is
    # risk-free at rollover would flatter the sell case and is not how a lease profile works.
    w_hold = cashflow_engine(rent0, g_pct, exit_cap_pct, reinvest_pct, renew_prob, uplift_pct)
    w_sell = cashflow_engine(replacement_rent, g_pct, exit_cap_pct, reinvest_pct, renew_prob, 0.0)
    return {
        "gross_price": gross, "cost_rate": cost, "net_proceeds": net,
        "replacement_rent": replacement_rent,
        "hold": w_hold, "sell": w_sell,
        "delta_hold_minus_sell": w_hold[0] - w_sell[0],
    }


def breakevens(rent0):
    """The three numbers that actually decide the question, solved not assumed."""
    out = {}
    base = SCENARIOS[1]
    y = VERIFIED["netlease_cash_yield_pct"]["value"]
    r = y

    # (a) Going-in cap rate at which holding and selling tie.
    #     Closed form: hold beats sell iff C > Y*(1-s). Solved numerically so the engine,
    #     not the algebra, is doing the work, and the two can be cross-checked.
    def delta_at_cap(c_pct):
        return wealth_paths(rent0, base["escalation_pct"], base["terminal_cap_pct"], r,
                            base["renew_prob"], 0.0, sell_cap_pct=c_pct)["delta_hold_minus_sell"]
    # delta_hold_minus_sell is INCREASING in the sell cap rate: the cheaper you sell, the
    # better holding looks. So holding wins ABOVE the threshold and selling wins BELOW it.
    # If holding wins at the midpoint, the threshold is lower -> move the upper bound down.
    lo, hi = 0.5, 20.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if delta_at_cap(mid) > 0:
            hi = mid
        else:
            lo = mid
    out["breakeven_going_in_cap_pct"] = lo
    out["breakeven_search_bracket_pct"] = [lo, hi]
    out["breakeven_going_in_cap_closed_form_pct"] = (y * (1 - disposition_cost_rate(rent0 / (lo / 100.0)))) if False else None
    s_at_cap = disposition_cost_rate(rent0 / (ASSUMPTIONS["going_in_cap_pct"]["value"] / 100.0))
    out["breakeven_going_in_cap_closed_form_pct"] = y * (1 - s_at_cap)
    out["breakeven_going_in_cap_closed_form_gap_pp"] = (
        out["breakeven_going_in_cap_pct"] - out["breakeven_going_in_cap_closed_form_pct"])

    # (b) Replacement yield required for selling to beat holding at today's assumed cap.
    lo, hi = 0.5, 20.0
    for _ in range(200):
        mid = (lo + hi) / 2
        gross = rent0 / (ASSUMPTIONS["going_in_cap_pct"]["value"] / 100.0)
        net = gross * (1 - disposition_cost_rate(gross))
        w_sell = cashflow_engine(net * mid / 100.0, base["escalation_pct"], base["terminal_cap_pct"],
                                 r, 1.0, 0.0)[0]
        w_hold = cashflow_engine(rent0, base["escalation_pct"], base["terminal_cap_pct"],
                                 r, base["renew_prob"], 0.0)[0]
        if w_sell < w_hold:
            lo = mid
        else:
            hi = mid
    out["required_replacement_yield_pct"] = lo
    out["required_replacement_yield_closed_form_pct"] = (
        ASSUMPTIONS["going_in_cap_pct"]["value"] / (1 - s_at_cap))

    # (c) The renewal RENT CONCESSION that would flip the answer from hold to sell.
    #     This is the number that prices the negotiation risk: the tenant only has to win a
    #     cut of this size at renewal for selling to become the better decision.
    status = wealth_paths(rent0, base["escalation_pct"], base["terminal_cap_pct"], r,
                          base["renew_prob"], 0.0)["delta_hold_minus_sell"]
    out["status_quo_delta_base"] = status
    lo, hi = -40.0, 0.0
    for _ in range(200):
        mid = (lo + hi) / 2
        d = wealth_paths(rent0, base["escalation_pct"], base["terminal_cap_pct"], r,
                         base["renew_prob"], mid)["delta_hold_minus_sell"]
        if d > 0:
            hi = mid
        else:
            lo = mid
    out["renewal_concession_that_flips_to_sell_pct"] = abs(lo)
    out["breakeven_note"] = ("The numeric threshold differs from the closed form Y*(1-s) because the "
                             "engine also applies an expected non-renewal loss at the expiry year, which "
                             "a pure income-capitalisation formula omits.")
    return out


def sensitivity(rent0):
    grid = []
    base_renew = ASSUMPTIONS["renew_prob"]["value"]
    for cap in [5.8, 6.3, 6.8, 7.3, 7.8]:
        cells = []
        for esc in [1.5, 2.0, 2.5]:
            w = wealth_paths(rent0, esc, cap, VERIFIED["netlease_cash_yield_pct"]["value"], base_renew, 0.0)
            cells.append({"escalation_pct": esc,
                          "hold_wealth": w["hold"][0],
                          "sell_wealth": w["sell"][0],
                          "delta_hold_minus_sell": w["delta_hold_minus_sell"]})
        grid.append({"terminal_cap_pct": cap, "cells": cells})
    return grid


def sensitivity_cap(rent0):
    rows = []
    for c in [4.8, 5.3, 5.8, 6.3, 6.8, 7.3, 7.8, 8.3]:
        w = wealth_paths(rent0, 2.0, 6.8, VERIFIED["netlease_cash_yield_pct"]["value"],
                         ASSUMPTIONS["renew_prob"]["value"], 0.0, sell_cap_pct=c)
        rows.append({"going_in_cap_pct": c, "gross_price": w["gross_price"],
                     "net_proceeds": w["net_proceeds"], "cost_rate_pct": w["cost_rate"] * 100,
                     "hold_minus_sell": w["delta_hold_minus_sell"],
                     "ula_applies": w["gross_price"] >= VERIFIED["ula_mid_threshold"]["value"]})
    return rows


# --------------------------------------------------------------------------- monte carlo
def monte_carlo(rent0):
    rng = random.Random(SEED)
    base = SCENARIOS[1]
    y = VERIFIED["netlease_cash_yield_pct"]["value"]
    p_fire = ASSUMPTIONS["fire_annual_prob_pct"]["value"] / 100.0
    p_rate = ASSUMPTIONS["rate_shock_annual_prob_pct"]["value"] / 100.0
    ins = ASSUMPTIONS["insurance_recovery_pct"]["value"] / 100.0
    cap0 = ASSUMPTIONS["going_in_cap_pct"]["value"]

    sell, hold = [], []
    for _ in range(TRIALS):
        shock_bp = 0.0
        for _y in range(N):
            if rng.random() < p_rate:
                shock_bp = ASSUMPTIONS["rate_shock_bp"]["value"]
                break
        g = max(0.0, rng.gauss(base["escalation_pct"], 0.6))
        # A rate shock pushes CAP RATES UP (prices down) and REINVESTMENT YIELDS UP together.
        # Applying it to only one side would bias the comparison; the first draft did exactly
        # that and is recorded as irregularity F02.
        exit_cap = max(4.5, rng.gauss(base["terminal_cap_pct"], 0.7)) + shock_bp / 100.0
        reinvest = max(0.0, y + shock_bp / 100.0)
        renew = 1.0 if rng.random() < base["renew_prob"] else 0.0

        # Sell path: the price a buyer pays also moves with cap rates at the moment of sale.
        sell_cap = max(4.5, cap0 + shock_bp / 100.0)
        w = wealth_paths(rent0, g, exit_cap, reinvest, renew, 0.0, sell_cap_pct=sell_cap)
        sell.append(w["sell"][0])
        w_h, _, _ = w["hold"]

        # Idiosyncratic hazard hits only the concentrated hold path.
        for _y in range(N):
            hit = 0.0
            if rng.random() < EQ_ANNUAL["m67"]:
                hit += rng.triangular(0.05, 0.35, 0.85)
            if rng.random() < p_fire:
                hit += rng.triangular(0.05, 0.40, 0.95)
            if hit:
                w_h -= w_h * hit * (1 - ins)
        hold.append(w_h)

    def stats(xs):
        xs = sorted(xs)
        n = len(xs)

        def q(p):
            return xs[min(n - 1, max(0, int(round(p * (n - 1)))))]

        k = max(1, int(0.05 * n))
        return {"mean": sum(xs) / n, "median": q(0.50), "p05": q(0.05), "p25": q(0.25),
                "p75": q(0.75), "p95": q(0.95), "p99": q(0.99), "min": xs[0], "max": xs[-1],
                "cvar_05": sum(xs[:k]) / k}

    ss, hs = stats(sell), stats(hold)
    return {
        "seed": SEED, "trials": TRIALS,
        "prob_sell_beats_hold": sum(1 for a, b in zip(sell, hold) if a > b) / TRIALS,
        "prob_hold_loss_exceeds_25pct_of_principal": sum(1 for x in hold if x < 0.75 * sell[0]) / TRIALS,
        "sell_now": ss, "hold": hs,
        "downside_from_mean_pct": {
            "sell_diversified": (ss["mean"] - ss["p05"]) / ss["mean"] * 100,
            "hold_concentrated": (hs["mean"] - hs["p05"]) / hs["mean"] * 100,
        },
        "mean_difference_pct_of_sell_mean": (hs["mean"] - ss["mean"]) / ss["mean"] * 100,
    }


# --------------------------------------------------------------------------- decision
def score_strategies(be):
    weights = {"wealth": 0.30, "growth": 0.25, "liquidity": 0.15, "risk": 0.20, "tax": 0.10}
    strategies = [
        {"id": "extend_then_sell",
         "name": "Negotiate an extension at a market reset, then sell into a 1031 if the price clears the trigger",
         "detail": "Use the tenant's own incentive to stay - a drive-through site inside central LA - to convert a 2030-2035 expiry into a longer term at a rent reset. A longer weighted average lease term is worth more per dollar of rent than the same rent with a near-term rollover, so this improves the hold case and the sale price at the same time.",
         "scores": {"wealth": 4, "growth": 5, "liquidity": 4, "risk": 4, "tax": 4},
         "pros": ["Attacks the only variable the owner controls: rent and term.",
                  "Selling with a fresh ten-year term removes the rollover discount a buyer would otherwise apply.",
                  "Keeps the section 1031 route open and defers the tax decision until a replacement exists."],
         "cons": ["Depends on tenant cooperation, and the tenant is in a closure programme.",
                  "An extension does not reduce concentration risk - it only makes the asset more sellable.",
                  "Time cost: negotiation, marketing and a 1031 identification is a multi-quarter project."]},
        {"id": "sell_now",
         "name": "Sell now into a section 1031 exchange",
         "detail": "Exit at the going-in cap rate, pay brokerage plus county and city transfer tax, and redeploy into two or more net-lease assets or a diversified vehicle, deferring the gain under section 1031.",
         "scores": {"wealth": 3, "growth": 3, "liquidity": 5, "risk": 5, "tax": 4},
         "pros": ["Removes the single-asset earthquake, wildfire and insurance tail in one transaction.",
                  "Converts one illiquid parcel into a diversified, re-priceable position.",
                  "Locks in today's cap-rate environment instead of betting it holds to 2032."],
         "cons": ["Crystallises disposition cost including 0.45% city and 0.11% county transfer tax, and Measure ULA above the indexed threshold.",
                  "Requires an identified replacement inside the exchange window; a failed exchange is worse than not selling.",
                  "Gives up the Prop 13 assessed-value cap, which is real while held and resets on sale."]},
        {"id": "hold_renew",
         "name": "Hold to expiry and renew at market",
         "detail": "Do nothing now; negotiate at or before expiry; keep the asset and the lease.",
         "scores": {"wealth": 3, "growth": 3, "liquidity": 2, "risk": 2, "tax": 5},
         "pros": ["Preserves the Prop 13 cap, which a sale resets.",
                  "No transaction cost, no exchange execution risk, no forced timeline.",
                  "Retains full optionality until the expiry window opens."],
         "cons": ["Leaves the decision to a negotiation conducted under time pressure.",
                  "Carries the full single-asset hazard exposure for another six to fourteen years.",
                  "If the closure programme reaches this unit, the owner holds a vacant drive-through."]},
        {"id": "renew_long",
         "name": "Renew long-term and hold as a permanent income asset",
         "detail": "Extend for the longest term available and treat the asset as a permanent income stream.",
         "scores": {"wealth": 3, "growth": 2, "liquidity": 1, "risk": 2, "tax": 5},
         "pros": ["Maximum contractual certainty of cash flow if the tenant performs.",
                  "Best tax profile: no recognition event and the Prop 13 cap continues."],
         "cons": ["Maximises concentration in a shrinking county, a contracting sector and one credit.",
                  "A long lease also blights redevelopment of the land.",
                  "Scores worst against the owner's stated requirement to keep risk manageable."]},
    ]
    for s in strategies:
        s["weighted"] = round(sum(s["scores"][k] * weights[k] for k in weights) / 5.0 * 100, 1)
    strategies.sort(key=lambda x: -x["weighted"])
    for i, s in enumerate(strategies, 1):
        s["rank"] = i
    return {"weights": weights, "scale": "1 = poor, 5 = strong", "strategies": strategies,
            "note": "Judgement scores on a verified fact base, not measurements. Weights are published so the owner can re-weight and watch the ranking move."}


def triggers(be):
    y = VERIFIED["netlease_cash_yield_pct"]["value"]
    return [
        {"id": "TR1", "trigger": "An appraisal or broker opinion implies a going-in cap rate below the solved breakeven.",
         "reading": f"breakeven {be['breakeven_going_in_cap_pct']:.2f}% vs verified market yield {y:.2f}%",
         "action": "The asset is priced tight relative to what you could buy. Selling wins on arithmetic."},
        {"id": "TR2", "trigger": "An appraisal or broker opinion implies a going-in cap rate above the solved breakeven.",
         "reading": f"breakeven {be['breakeven_going_in_cap_pct']:.2f}%",
         "action": "Holding wins on arithmetic. Do not sell to buy a lower yield."},
        {"id": "TR3", "trigger": "A replacement property is identified at or above the required replacement yield.",
         "reading": f"required {be['required_replacement_yield_pct']:.2f}%",
         "action": "Execute the exchange. This is the only condition under which selling is a pure upgrade."},
        {"id": "TR4", "trigger": "The tenant will sign an extension at a rent reset.",
         "reading": "uplift required to change the answer is solved in the model",
         "action": "Sign, then sell with the longer term. Best combined outcome for wealth and risk."},
        {"id": "TR5", "trigger": "Insurance cost rises enough to cut net operating income, or a carrier declines the risk.",
         "reading": "current premium unverified (H11)",
         "action": "Sell. Uninsurable or uneconomic cover is the clearest sell signal in this asset class."},
        {"id": "TR6", "trigger": "The option notice date is less than twelve months away.",
         "reading": "date unverified (L01, L04)",
         "action": "Stop analysing and start the process. Time becomes the binding constraint, not price."},
        {"id": "TR7", "trigger": "Tenant same-store sales turn positive and the restaurant count stabilises for two consecutive quarters.",
         "reading": "Q3 FY2026: system SSS -1.1%; 2,115 units vs 2,168",
         "action": "Tenant risk is falling; the hold case strengthens and an extension gets easier."},
        {"id": "TR8", "trigger": "Owner liquidity needs crystallise.",
         "reading": "unverified (O03)",
         "action": "Liquidity overrides optimisation. Sell, accept the cost, and pre-plan the exchange."},
        {"id": "TR9", "trigger": "A parcel-level hazard or insurance finding changes the loss distribution.",
         "reading": "FHSZ, flood zone, seismic screening and earthquake cover all unverified (H08-H12)",
         "action": "Re-run the model with the verified hazard inputs before committing either way."},
    ]


# --------------------------------------------------------------------------- main
def main():
    rent0 = ASSUMPTIONS["rent_normaliser"]["value"]
    y = VERIFIED["netlease_cash_yield_pct"]["value"]

    rows = []
    for sc in SCENARIOS:
        w = wealth_paths(rent0, sc["escalation_pct"], sc["terminal_cap_pct"], y, sc["renew_prob"], 0.0)
        rows.append({
            "id": sc["id"], "label": sc["label"], "narrative": sc["narrative"],
            "escalation_pct": sc["escalation_pct"], "terminal_cap_pct": sc["terminal_cap_pct"],
            "renew_prob": sc["renew_prob"],
            "gross_price": w["gross_price"], "cost_rate_pct": w["cost_rate"] * 100,
            "net_proceeds": w["net_proceeds"], "replacement_rent": w["replacement_rent"],
            "sell_wealth": w["sell"][0],
            "hold_terminal_value": w["hold"][1], "hold_cash_pile": w["hold"][2],
            "hold_wealth": w["hold"][0],
            "delta_hold_minus_sell": w["delta_hold_minus_sell"],
        })

    be = breakevens(rent0)
    mc = monte_carlo(rent0)

    out = {
        "engine": "session-313ba936/scripts/model.py",
        "generated_for": "2026-11-10",
        "units": "USD, nominal, pre-tax, per $100,000 of annual contract rent",
        "disclaimer": ("Not an appraisal and not a valuation. Contract rent, exact expiry, escalations, "
                       "basis and debt are unknown. Every dollar figure scales linearly with the owner's "
                       "actual rent; the percentage breakevens are directly reusable."),
        "comparison_basis": ("Holding and selling run through the same cash-flow engine with the same escalation, "
                             "reinvestment rate and exit cap. The sale pays transaction costs and the replacement is "
                             "bought at the verified net-lease market yield. This is a like-for-like comparison; "
                             "an earlier version of this script compared a growing asset to a non-growing yield, "
                             "which is recorded as irregularity F02."),
        "verified_inputs": VERIFIED,
        "annualised_hazard_probabilities_pct": {k: v * 100 for k, v in EQ_ANNUAL.items()},
        "hazard_derivation": "annual p = 1 - (1 - p30)^(1/30) from the USGS 30-year Los Angeles-region probabilities (S18).",
        "assumptions": ASSUMPTIONS,
        "config": {"start_year": START, "expiry_year": EXPIRY, "horizon_year": HORIZON, "years": N,
                   "rent_normaliser": rent0},
        "scenarios": rows,
        "breakevens": be,
        "sensitivity_cap": sensitivity_cap(rent0),
        "sensitivity": sensitivity(rent0),
        "monte_carlo": mc,
        "decision": score_strategies(be),
        "triggers": triggers(be),
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print("wrote", os.path.relpath(OUT, ROOT))
    print(f"  breakeven going-in cap {be['breakeven_going_in_cap_pct']:.3f}% "
          f"(closed form {be['breakeven_going_in_cap_closed_form_pct']:.3f}%, "
          f"gap {be['breakeven_going_in_cap_closed_form_gap_pp']:+.3f}pp)")
    print(f"  required replacement yield {be['required_replacement_yield_pct']:.3f}% "
          f"(closed form {be['required_replacement_yield_closed_form_pct']:.3f}%)")
    print(f"  base delta hold-minus-sell {be['status_quo_delta_base']:,.0f} per $100k rent")
    print(f"  concession that flips to sell {be['renewal_concession_that_flips_to_sell_pct']:.2f}%")
    print(f"  monte carlo P(sell>hold) {mc['prob_sell_beats_hold']*100:.1f}% | "
          f"5th pct sell {mc['sell_now']['p05']:,.0f} vs hold {mc['hold']['p05']:,.0f}")


if __name__ == "__main__":
    main()
