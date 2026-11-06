#!/usr/bin/env python3
"""
Deterministic decision model for a single-tenant Jack in the Box NNN asset in Central Los Angeles.

Design rules
------------
1. Verified inputs come ONLY from data/valuation.json "verified_inputs" (each has an official source id).
2. Analyst assumptions are separated in "analyst_assumptions" and are labelled as such on the website.
3. Nothing here produces an appraisal. The output is a decision *framework*: it shows which
   assumptions actually drive the sell-vs-renew answer, and it publishes the breakeven points.
4. Fully deterministic. Same inputs -> same outputs. No randomness, no Monte Carlo.

Run:  python3 tools/model.py
Out:  data/model_output.json  and  research/model-report.md
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAL_PATH = os.path.join(ROOT, "data", "valuation.json")
OUT_JSON = os.path.join(ROOT, "data", "model_output.json")
OUT_MD = os.path.join(ROOT, "research", "model-report.md")

with open(VAL_PATH, encoding="utf-8") as f:
    VAL = json.load(f)

V = {row["key"]: row["value"] for row in VAL["verified_inputs"]}
A = {row["key"]: row["value"] for row in VAL["analyst_assumptions"]}

START = 2026
EXPIRY = int(A["A3"])          # base case 2032 (midpoint of the 2030-2035 window)
HORIZON = int(A["A11"])        # 2040
BASE_RENT = float(A["A1"])
ESC = float(A["A2"]) / 100.0
DISC = float(A["A4"]) / 100.0
BROKER = 0.03
CLOSING = 0.005
COUNTY_DTT = 0.0011
CITY_DTT = 0.0045
ULA_T1 = 0.04
ULA_T2 = 0.055
ULA_THRESH = (5400000.0, 10900000.0)
TIFFIN = float(A["A9"])
DOWNTIME_YRS = float(A["A8"]) / 12.0
TREASURY = float(A["A10"]) / 100.0
NETLEASE = float(V["netlease_yield"]) / 100.0


def transfer_cost_rate(price):
    """Total disposition cost rate including the City of Los Angeles tiered Measure ULA surtax."""
    rate = BROKER + CLOSING + COUNTY_DTT + CITY_DTT
    if price >= ULA_THRESH[1]:
        rate += ULA_T2
    elif price >= ULA_THRESH[0]:
        rate += ULA_T1
    return rate


def net_proceeds(price):
    return price * (1.0 - transfer_cost_rate(price))


def value_from_rent(rent, cap):
    return rent / cap


def future_value(cf, t, horizon=HORIZON, r=None):
    """Compound a cash flow received at year t to the horizon year."""
    r = TREASURY if r is None else r
    return cf * (1.0 + r) ** (horizon - t)


def sell_now(cap, r):
    price = value_from_rent(BASE_RENT, cap)
    net = net_proceeds(price)
    return {
        "price": price,
        "cost_rate": transfer_cost_rate(price),
        "net_proceeds": net,
        "wealth_horizon": net * (1.0 + r) ** (HORIZON - START),
        "reinvest_rate": r,
    }


def hold_then_sell(exit_cap, g=ESC, r=TREASURY):
    """Collect contract rent through the lease term, sell the asset at expiry."""
    rents = []
    for t in range(1, EXPIRY - START + 1):
        rents.append(BASE_RENT * (1.0 + g) ** (t - 1))
    exit_rent = BASE_RENT * (1.0 + g) ** (EXPIRY - START)
    price = value_from_rent(exit_rent, exit_cap)
    net = net_proceeds(price)
    wealth = sum(future_value(cf, START + i + 1, r=r) for i, cf in enumerate(rents))
    wealth += future_value(net, EXPIRY, r=r)
    return {"contract_rent": sum(rents), "exit_price": price, "net_proceeds": net, "wealth_horizon": wealth}


def renew_and_hold(exit_cap, reprice=1.0, g=ESC, r=TREASURY):
    """Renew at expiry at a repriced market rent, hold to the horizon, then value the reversion."""
    # pre-expiry contract rent
    wealth = 0.0
    for t in range(1, EXPIRY - START + 1):
        wealth += future_value(BASE_RENT * (1.0 + g) ** (t - 1), START + t, r=r)
    # post-expiry renewed rent
    rent = BASE_RENT * (1.0 + g) ** (EXPIRY - START) * reprice
    years_after = HORIZON - EXPIRY
    renewed_total = 0.0
    for i in range(1, years_after + 1):
        cf = rent * (1.0 + g) ** (i - 1)
        renewed_total += cf
        wealth += future_value(cf, EXPIRY + i, r=r)
    reversion_rent = rent * (1.0 + g) ** years_after
    terminal_price = value_from_rent(reversion_rent, exit_cap)
    terminal_net = net_proceeds(terminal_price)
    wealth += terminal_net
    return {
        "renewed_rent": rent,
        "renewed_rent_total": renewed_total,
        "terminal_price": terminal_price,
        "terminal_net": terminal_net,
        "wealth_horizon": wealth,
    }


def do_not_renew(exit_cap, g=ESC, r=TREASURY):
    """Tenant vacates: downtime, leasing costs, then a market-rent re-let at expiry."""
    rents = 0.0
    for t in range(1, EXPIRY - START + 1):
        rents += future_value(BASE_RENT * (1.0 + g) ** (t - 1), START + t, r=r)
    market_rent = BASE_RENT * (1.0 + g) ** (EXPIRY - START)
    # capital outlay and lost income during downtime
    cost = TIFFIN + market_rent * DOWNTIME_YRS
    wealth = rents - future_value(cost, EXPIRY, r=r)
    # re-let asset valued at expiry-end
    t_relet = EXPIRY + DOWNTIME_YRS
    price = value_from_rent(market_rent, exit_cap)
    wealth += future_value(net_proceeds(price), t_relet, r=r)
    return {"market_rent": market_rent, "downtime_cost": cost, "relet_price": price, "wealth_horizon": wealth}


SCENARIOS = [
    {"id": "bear", "label": "Bear", "exit_cap": 0.075, "esc": 0.015, "reprice": 0.90,
     "renew_prob": 0.55, "narrative": "Rates stay high, exit cap 7.50%, 1.5% escalators, tenant negotiates rent down 10% at renewal."},
    {"id": "base", "label": "Base", "exit_cap": 0.065, "esc": 0.020, "reprice": 1.00,
     "renew_prob": 0.75, "narrative": "Exit cap 6.50%, 2.0% escalators, renewal at then-current market rent, 75% renewal probability."},
    {"id": "bull", "label": "Bull", "exit_cap": 0.055, "esc": 0.025, "reprice": 1.15,
     "renew_prob": 0.85, "narrative": "Rate relief compresses the exit cap to 5.50%, 2.5% escalators, market rent 15% above contract at renewal."},
]

results = {"config": {
    "start_year": START, "expiry_year": EXPIRY, "horizon_year": HORIZON,
    "base_rent": BASE_RENT, "discount_rate": DISC,
    "reinvest_treasury": TREASURY, "reinvest_netlease": NETLEASE,
    "transfer_cost_formula": "3.00% brokerage + 0.50% closing + 0.11% county DTT + 0.45% city DTT + Measure ULA tier (4.0% above $5.4M / 5.5% at $10.9M)",
}, "scenarios": [], "breakevens": {}, "sensitivity": [], "renewal_value": {}, "assumption_sensitivity": []}

for sc in SCENARIOS:
    cap, g, rp, p = sc["exit_cap"], sc["esc"], sc["reprice"], sc["renew_prob"]
    a_t = sell_now(cap, TREASURY)
    a_n = sell_now(cap, NETLEASE)
    post = hold_then_sell(cap, g=g)
    ren = renew_and_hold(cap, reprice=rp, g=g)
    dr = do_not_renew(cap, g=g)
    hold_expected = p * ren["wealth_horizon"] + (1 - p) * dr["wealth_horizon"]
    results["scenarios"].append({
        "id": sc["id"], "label": sc["label"], "narrative": sc["narrative"],
        "exit_cap": cap, "escalation": g, "renew_prob": p, "reprice": rp,
        "sell_now_price": a_t["price"],
        "sell_now_cost_rate": a_t["cost_rate"],
        "sell_now_net": a_t["net_proceeds"],
        "sell_now_wealth_treasury": a_t["wealth_horizon"],
        "sell_now_wealth_netlease": a_n["wealth_horizon"],
        "hold_to_expiry_wealth": post["wealth_horizon"],
        "renew_wealth": ren["wealth_horizon"],
        "vacate_wealth": dr["wealth_horizon"],
        "hold_expected_wealth": hold_expected,
        "delta_hold_vs_sell_treasury": hold_expected - a_t["wealth_horizon"],
        "delta_hold_vs_sell_netlease": hold_expected - a_n["wealth_horizon"],
        "npv_treasury": a_t["wealth_horizon"] / (1 + DISC) ** (HORIZON - START),
        "npv_hold": hold_expected / (1 + DISC) ** (HORIZON - START),
        "renewed_rent": ren["renewed_rent"],
        "market_rent_at_expiry": dr["market_rent"],
    })

# ---- Breakeven 1: reinvestment yield that lets "sell now" match "hold" -----------
def required_yield(target, net, years):
    return (target / net) ** (1.0 / years) - 1.0

for sc in results["scenarios"]:
    results["breakevens"].setdefault("required_reinvest_yield_pct", {})[sc["id"]] = round(
        100 * required_yield(sc["hold_expected_wealth"], sc["sell_now_net"], HORIZON - START), 3)

# ---- Breakeven 2: exit cap at which hold == sell (base escalation) ---------------
def breakeven_cap(sell_wealth, g=ESC, p=0.75, rp=1.0):
    lo, hi = 0.02, 0.30
    for _ in range(80):
        mid = (lo + hi) / 2
        ren = renew_and_hold(mid, reprice=rp, g=g)
        dr = do_not_renew(mid, g=g)
        val = p * ren["wealth_horizon"] + (1 - p) * dr["wealth_horizon"]
        if val > sell_wealth:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2

sell_t = sell_now(0.065, TREASURY)["wealth_horizon"]
sell_n = sell_now(0.065, NETLEASE)["wealth_horizon"]
results["breakevens"]["exit_cap_hold_equals_sell_treasury_pct"] = round(100 * breakeven_cap(sell_t), 3)
results["breakevens"]["exit_cap_hold_equals_sell_netlease_pct"] = round(100 * breakeven_cap(sell_n), 3)

# ---- Sensitivity grid: exit cap x escalation, renew-and-hold wealth at horizon ----
caps = [0.055, 0.060, 0.065, 0.070, 0.075]
escs = [0.015, 0.020, 0.025]
for cap in caps:
    row = {"exit_cap": cap, "cells": []}
    for g in escs:
        ren = renew_and_hold(cap, reprice=1.0, g=g)
        dr = do_not_renew(cap, g=g)
        exp = 0.75 * ren["wealth_horizon"] + 0.25 * dr["wealth_horizon"]
        row["cells"].append({"escalation": g, "wealth": exp, "delta_vs_sell_netlease": exp - sell_n,
                             "delta_vs_sell_treasury": exp - sell_t})
    results["sensitivity"].append(row)

# ---- What market-rent uplift at renewal is needed to beat "sell now" -------------
base_renew = renew_and_hold(0.065, reprice=1.0, g=ESC)["wealth_horizon"]
base_vacate = do_not_renew(0.065, g=ESC)["wealth_horizon"]
lo, hi = 0.10, 3.00
for _ in range(80):
    mid = (lo + hi) / 2
    val = 0.75 * renew_and_hold(0.065, reprice=mid, g=ESC)["wealth_horizon"] + 0.25 * base_vacate
    if val > sell_n:
        hi = mid
    else:
        lo = mid
results["renewal_value"] = {
    "renew_wealth_at_market_rent": base_renew,
    "vacate_wealth": base_vacate,
    "required_rent_uplift_to_beat_sell_netlease_pct": round(100 * ((lo + hi) / 2 - 1.0), 2),
    "required_rent_uplift_to_beat_sell_treasury_pct": None,
}
lo2, hi2 = 0.10, 3.00
for _ in range(80):
    mid = (lo2 + hi2) / 2
    val = 0.75 * renew_and_hold(0.065, reprice=mid, g=ESC)["wealth_horizon"] + 0.25 * base_vacate
    if val > sell_t:
        hi2 = mid
    else:
        lo2 = mid
results["renewal_value"]["required_rent_uplift_to_beat_sell_treasury_pct"] = round(100 * ((lo2 + hi2) / 2 - 1.0), 2)

# ---- One-at-a-time sensitivity of the base case ---------------------------------
base = next(s for s in results["scenarios"] if s["id"] == "base")
drivers = []
for label, cap, g, p, rp in [
    ("Exit cap 5.50% instead of 6.50%", 0.055, ESC, 0.75, 1.0),
    ("Exit cap 7.50% instead of 6.50%", 0.075, ESC, 0.75, 1.0),
    ("Escalation 1.5% instead of 2.0%", 0.065, 0.015, 0.75, 1.0),
    ("Escalation 2.5% instead of 2.0%", 0.065, 0.025, 0.75, 1.0),
    ("Renewal probability 55% instead of 75%", 0.065, ESC, 0.55, 1.0),
    ("Renewal probability 85% instead of 75%", 0.065, ESC, 0.85, 1.0),
    ("Rent reset 10% lower at renewal", 0.065, ESC, 0.75, 0.90),
    ("Rent reset 15% higher at renewal", 0.065, ESC, 0.75, 1.15),
]:
    ren = renew_and_hold(cap, reprice=rp, g=g)
    vac = do_not_renew(cap, g=g)
    exp = p * ren["wealth_horizon"] + (1 - p) * vac["wealth_horizon"]
    drivers.append({"change": label, "hold_expected_wealth": exp,
                    "delta_vs_base_hold": exp - base["hold_expected_wealth"],
                    "delta_vs_sell_netlease": exp - sell_n,
                    "delta_vs_sell_treasury": exp - sell_t})
drivers.sort(key=lambda d: abs(d["delta_vs_base_hold"]), reverse=True)
results["assumption_sensitivity"] = drivers

with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

# ---- Markdown report -------------------------------------------------------------
def m(x):
    return f"${x:,.0f}"

lines = []
lines.append("# Model report - sell vs renew, Central Los Angeles Jack in the Box NNN\n")
lines.append("Generated by `tools/model.py` on the verified inputs in `data/valuation.json`. "
             "All figures are pre-tax, nominal US dollars, and are a decision framework - not an appraisal.\n")
lines.append("## Inputs\n")
lines.append(f"- Base rent used: {m(BASE_RENT)}/yr (assumption A1 - benchmark of 8% of the verified FY2025 franchise AUV)")
lines.append(f"- Lease expiry used: {EXPIRY} (assumption A3 - midpoint of the 2030-2035 window)")
lines.append(f"- Horizon: {HORIZON}; discount rate: {DISC*100:.2f}%")
lines.append(f"- Reinvestment alternatives: Treasury {TREASURY*100:.2f}% (verified S11); net-lease {NETLEASE*100:.2f}% (verified S10)")
lines.append(f"- Disposition cost: brokerage 3.00% + closing 0.50% + county DTT 0.11% + city DTT 0.45% + Measure ULA 4.0%/5.5% above the official thresholds\n")
lines.append("## Scenario results (wealth at 2040)\n")
lines.append("| Scenario | Sell-now price | Net proceeds | Sell now, reinvest at Treasury | Sell now, reinvest at net-lease yield | Hold + renew (prob-weighted) | Hold minus sell (Treasury) | Hold minus sell (net-lease) |")
lines.append("|---|---|---|---|---|---|---|---|")
for s in results["scenarios"]:
    lines.append(f"| {s['label']} | {m(s['sell_now_price'])} | {m(s['sell_now_net'])} | {m(s['sell_now_wealth_treasury'])} | "
                 f"{m(s['sell_now_wealth_netlease'])} | {m(s['hold_expected_wealth'])} | "
                 f"{m(s['delta_hold_vs_sell_treasury'])} | {m(s['delta_hold_vs_sell_netlease'])} |")
lines.append("\n## Breakevens\n")
lines.append(f"- Reinvestment yield needed for 'sell now' to match 'hold', base case: "
             f"{results['breakevens']['required_reinvest_yield_pct']['base']:.2f}%")
lines.append(f"- Reinvestment yield needed, bear case: {results['breakevens']['required_reinvest_yield_pct']['bear']:.2f}%")
lines.append(f"- Reinvestment yield needed, bull case: {results['breakevens']['required_reinvest_yield_pct']['bull']:.2f}%")
lines.append(f"- Exit cap at which hold equals sell (vs Treasury reinvestment): {results['breakevens']['exit_cap_hold_equals_sell_treasury_pct']:.2f}%")
lines.append(f"- Exit cap at which hold equals sell (vs net-lease reinvestment): {results['breakevens']['exit_cap_hold_equals_sell_netlease_pct']:.2f}%")
lines.append(f"- Rent uplift at renewal needed to beat selling and reinvesting at the net-lease yield: "
             f"{results['renewal_value']['required_rent_uplift_to_beat_sell_netlease_pct']:.2f}%")
lines.append(f"- Rent uplift at renewal needed to beat selling and reinvesting at the Treasury yield: "
             f"{results['renewal_value']['required_rent_uplift_to_beat_sell_treasury_pct']:.2f}%")
lines.append("\n## Sensitivity: exit cap x rent escalation (hold + renew, prob-weighted)\n")
lines.append("| Exit cap | 1.5% escalation | 2.0% escalation | 2.5% escalation |")
lines.append("|---|---|---|---|")
for row in results["sensitivity"]:
    cells = " | ".join(m(c["wealth"]) for c in row["cells"])
    lines.append(f"| {row['exit_cap']*100:.2f}% | {cells} |")
lines.append("\n## Which assumptions actually move the answer\n")
lines.append("| Change from base case | Hold wealth at 2040 | Delta vs base | Delta vs sell + net-lease reinvestment |")
lines.append("|---|---|---|---|")
for d in results["assumption_sensitivity"]:
    lines.append(f"| {d['change']} | {m(d['hold_expected_wealth'])} | {m(d['delta_vs_base_hold'])} | {m(d['delta_vs_sell_netlease'])} |")
lines.append("\n## What this model does NOT do\n")
lines.append("- It does not value the actual parcel. Rent, expiration date, basis and debt are placeholders (P01-P12).")
lines.append("- It does not compute income tax, depreciation recapture, NIIT or California tax. That requires the owner's basis (P05).")
lines.append("- It does not price tenant default beyond the renewal probability, and it does not model a wildfire or earthquake loss; those are handled in the risk register.")
lines.append("- It does not use any non-official data source. Cap-rate inputs are a labelled assumption, because no government agency publishes asset-level cap rates (M51).")

with open(OUT_MD, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print("wrote", OUT_JSON)
print("wrote", OUT_MD)
for s in results["scenarios"]:
    print(f"{s['label']:5s} sell@T={s['sell_now_wealth_treasury']/1e6:6.2f}M sell@NL={s['sell_now_wealth_netlease']/1e6:6.2f}M "
          f"hold={s['hold_expected_wealth']/1e6:6.2f}M")
print("required reinvest yield (base):", results["breakevens"]["required_reinvest_yield_pct"]["base"])
print("required rent uplift vs net-lease:", results["renewal_value"]["required_rent_uplift_to_beat_sell_netlease_pct"])
