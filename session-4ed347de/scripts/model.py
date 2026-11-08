#!/usr/bin/env python3
"""
Session I (session-4ed347de) projection and verification engine.

Four jobs, all deterministic except the explicitly-seeded Monte Carlo:

1. REPRODUCE  - re-implement the published root model (tools/model.py) from its own published
                inputs and check, line by line, that this session reproduces data/model_output.json.
                If the reproduction fails, that is a finding, not a nuisance.
2. SENSITIVITY- re-run the sell-vs-hold comparison across the *range* of SEC-filed net-lease
                acquisition yields, because the published answer sits inside that range.
3. PANEL      - assemble the verified area-economy panel actually used in the narrative.
4. MONTE CARLO- 20,000 paths with business-as-usual risk plus explicit black-swan hazards
                (earthquake, wildfire, tenant credit event), on both the sell and the hold path.
                Seed is fixed so the run is reproducible.

Rules:
  * No input here is invented. Every "verified" input carries a source id that exists in
    data/sources.json and a value that was read on that page on 2026-11-08.
  * Analyst assumptions are labelled ANALYST and are separated from verified inputs.
  * Nothing here is an appraisal, tax advice or investment advice.

Run: python3 session-4ed347de/scripts/model.py
Out: data/model_output.json
"""
import json
import os
import random

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "data", "model_output.json")

with open(os.path.join(HERE, "data", "sources.json"), encoding="utf-8") as f:
    SRC = {s["id"]: s for s in json.load(f)["sources"]}
with open(os.path.join(HERE, "data", "verification.json"), encoding="utf-8") as f:
    VER = json.load(f)
VROW = {r["id"]: r for r in VER["rows"]}


def ver(row_id):
    """Fetch a verified value by ledger row id. Refuses to return an unverified row."""
    r = VROW[row_id]
    if r["status"] != "verified":
        raise SystemExit(f"{row_id} is not verified; refusing to use it as a model input")
    return r


# --------------------------------------------------------------------------- verified inputs
TREASURY = float(ver("C01")["value"]) / 100.0          # S10  verified print 4.84%
TREASURY_PUBLISHED_ASSUMPTION = 0.049                  # root model's A10 (an ASSUMPTION, not the DGS10 print)
NETLEASE_FY2025 = float(ver("C03")["value"]) / 100.0   # S12
NETLEASE_Q3_2026 = float(ver("C04")["value"]) / 100.0  # S13
COUNTY_DTT = float(ver("X06")["value"]) / 100.0        # S16  (0.11%)
CITY_DTT = float(ver("X03")["value"]) / 100.0          # S15  (0.45%)
ULA_T1 = float(ver("X04")["value"]) / 100.0            # S15  (4.0%)
ULA_T2 = float(ver("X05")["value"]) / 100.0            # S15  (5.5%)
ULA_THRESH = (5_400_000.0, 10_900_000.0)               # S15  thresholds

# --------------------------------------------------------------------------- analyst assumptions
# These are ASSUMPTIONS, not verified facts. They are the same assumptions the published root
# model makes (data/valuation.json), kept identical on purpose so the reproduction test is fair.
A = {
    "A1": 150_000.0,   # subject base rent, USD/yr  (OWNER-SUPPLIED FACT NOT AVAILABLE -> assumption)
    "A2": 0.020,       # contract escalation per year
    "A3": 2032,        # lease expiry used (midpoint of the 2030-2035 window)
    "A4": 0.080,       # owner discount rate
    "A5": 0.065,       # base exit cap
    "A8": 18,          # months of downtime if the tenant does not renew
    "A9": 300_000.0,   # landlord leasing / tenant-improvement cost on re-tenanting
    "A10": 0.049,      # reinvestment yield if sold (published assumption; below the DGS10 print)
    "A11": 2040,       # comparison horizon
    "A7": 0.75,        # base renewal probability
}
START, EXPIRY, HORIZON = 2026, int(A["A3"]), int(A["A11"])
BASE_RENT, ESC, DISC = A["A1"], A["A2"], A["A4"]
BROKER, CLOSING = 0.03, 0.005
DOWNTIME_YRS, TIFFIN = A["A8"] / 12.0, A["A9"]


def transfer_cost_rate(price):
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


def future_value(cf, t, r, horizon=HORIZON):
    return cf * (1.0 + r) ** (horizon - t)


def sell_now(cap, r):
    price = value_from_rent(BASE_RENT, cap)
    net = net_proceeds(price)
    return {"price": price, "cost_rate": transfer_cost_rate(price), "net_proceeds": net,
            "wealth_horizon": net * (1.0 + r) ** (HORIZON - START), "reinvest_rate": r}


def renew_and_hold(exit_cap, reprice=1.0, g=ESC, r=None):
    r = TREASURY_PUBLISHED_ASSUMPTION if r is None else r
    wealth = 0.0
    for t in range(1, EXPIRY - START + 1):
        wealth += future_value(BASE_RENT * (1.0 + g) ** (t - 1), START + t, r)
    rent = BASE_RENT * (1.0 + g) ** (EXPIRY - START) * reprice
    years_after = HORIZON - EXPIRY
    for i in range(1, years_after + 1):
        wealth += future_value(rent * (1.0 + g) ** (i - 1), EXPIRY + i, r)
    terminal_rent = rent * (1.0 + g) ** years_after
    terminal_price = value_from_rent(terminal_rent, exit_cap)
    terminal_net = net_proceeds(terminal_price)
    wealth += terminal_net
    return {"renewed_rent": rent, "terminal_price": terminal_price,
            "terminal_net": terminal_net, "wealth_horizon": wealth}


def do_not_renew(exit_cap, g=ESC, r=None):
    r = TREASURY_PUBLISHED_ASSUMPTION if r is None else r
    rents = 0.0
    for t in range(1, EXPIRY - START + 1):
        rents += future_value(BASE_RENT * (1.0 + g) ** (t - 1), START + t, r)
    market_rent = BASE_RENT * (1.0 + g) ** (EXPIRY - START)
    cost = TIFFIN + market_rent * DOWNTIME_YRS
    wealth = rents - future_value(cost, EXPIRY, r)
    price = value_from_rent(market_rent, exit_cap)
    wealth += future_value(net_proceeds(price), EXPIRY + DOWNTIME_YRS, r)
    return {"market_rent": market_rent, "downtime_cost": cost,
            "relet_price": price, "wealth_horizon": wealth}


SCENARIOS = [
    {"id": "bear", "label": "Bear", "exit_cap": 0.075, "esc": 0.015, "reprice": 0.90, "renew_prob": 0.55},
    {"id": "base", "label": "Base", "exit_cap": 0.065, "esc": 0.020, "reprice": 1.00, "renew_prob": 0.75},
    {"id": "bull", "label": "Bull", "exit_cap": 0.055, "esc": 0.025, "reprice": 1.15, "renew_prob": 0.85},
]


def evaluate(exit_cap, g, reprice, p, treasury=TREASURY_PUBLISHED_ASSUMPTION, netlease=None):
    netlease = NETLEASE_FY2025 if netlease is None else netlease
    a_t, a_n = sell_now(exit_cap, treasury), sell_now(exit_cap, netlease)
    ren = renew_and_hold(exit_cap, reprice=reprice, g=g, r=treasury)
    dr = do_not_renew(exit_cap, g=g, r=treasury)
    hold = p * ren["wealth_horizon"] + (1 - p) * dr["wealth_horizon"]
    return {
        "sell_now_price": a_t["price"],
        "sell_now_cost_rate": a_t["cost_rate"],
        "sell_now_net": a_t["net_proceeds"],
        "sell_now_wealth_treasury": a_t["wealth_horizon"],
        "sell_now_wealth_netlease": a_n["wealth_horizon"],
        "renew_wealth": ren["wealth_horizon"],
        "vacate_wealth": dr["wealth_horizon"],
        "hold_expected_wealth": hold,
        "delta_hold_vs_sell_treasury": hold - a_t["wealth_horizon"],
        "delta_hold_vs_sell_netlease": hold - a_n["wealth_horizon"],
        "renewed_rent": ren["renewed_rent"],
        "market_rent_at_expiry": dr["market_rent"],
    }


# ============================================================ 1. REPRODUCE the published model
PUB_PATH = os.path.join(ROOT, "data", "model_output.json")
reproduction = {"status": "not_run", "checked": [], "mismatches": []}
try:
    with open(PUB_PATH, encoding="utf-8") as f:
        PUB = json.load(f)
    for sc in SCENARIOS:
        mine = evaluate(sc["exit_cap"], sc["esc"], sc["reprice"], sc["renew_prob"])
        theirs = next(s for s in PUB["scenarios"] if s["id"] == sc["id"])
        for k in ("sell_now_net", "sell_now_wealth_treasury", "sell_now_wealth_netlease",
                  "hold_expected_wealth", "delta_hold_vs_sell_treasury", "delta_hold_vs_sell_netlease"):
            a, b = mine[k], theirs.get(k)
            ok = b is not None and abs(a - b) <= max(1.0, abs(b) * 1e-6)
            reproduction["checked"].append({"scenario": sc["id"], "key": k,
                                            "session_i": round(a, 2), "published": round(b, 2) if b is not None else None,
                                            "match": ok})
            if not ok:
                reproduction["mismatches"].append(f"{sc['id']}.{k}")
    # also reproduce the published breakeven on the required reinvestment yield
    def required_yield(target, net, years):
        return (target / net) ** (1.0 / years) - 1.0
    repro_be = {}
    for sc in SCENARIOS:
        m = evaluate(sc["exit_cap"], sc["esc"], sc["reprice"], sc["renew_prob"])
        repro_be[sc["id"]] = round(100 * required_yield(m["hold_expected_wealth"], m["sell_now_net"],
                                                        HORIZON - START), 3)
    pub_be = PUB["breakevens"]["required_reinvest_yield_pct"]
    for k, val in repro_be.items():
        ok = abs(val - pub_be[k]) <= 0.01
        reproduction["checked"].append({"scenario": k, "key": "breakevens.required_reinvest_yield_pct",
                                        "session_i": val, "published": pub_be[k], "match": ok})
        if not ok:
            reproduction["mismatches"].append(f"breakeven.{k}")
    reproduction["status"] = "pass" if not reproduction["mismatches"] else "mismatch"
except FileNotFoundError:
    reproduction["status"] = "published_model_not_found"

# ============================================================ 2. YIELD SENSITIVITY
base_sc = SCENARIOS[1]
base_mine = evaluate(base_sc["exit_cap"], base_sc["esc"], base_sc["reprice"], base_sc["renew_prob"])
base_hold = base_mine["hold_expected_wealth"]

yield_grid = []
y_exact = None
y = 0.0550
while y <= 0.0755:
    s = sell_now(base_sc["exit_cap"], y)
    delta = base_hold - s["wealth_horizon"]
    yield_grid.append({
        "netlease_yield": round(100 * y, 2),
        "sell_wealth": s["wealth_horizon"],
        "delta_hold_minus_sell": delta,
        "hold_wins": delta > 0,
        "is_fy2025_published_input": abs(y - NETLEASE_FY2025) < 1e-9,
        "is_current_sec_q3_2026": abs(y - NETLEASE_Q3_2026) < 1e-9,
    })
    y = round(y + 0.0010, 6)

lo, hi = 0.02, 0.20
# sell wealth is monotonically INCREASING in the reinvestment yield, so bisect upward:
# lo stays at a yield where holding still wins, hi moves down to the first yield where selling wins.
for _ in range(200):
    mid = (lo + hi) / 2
    if sell_now(base_sc["exit_cap"], mid)["wealth_horizon"] < base_hold:
        lo = mid
    else:
        hi = mid
y_exact = (lo + hi) / 2

# ============================================================ 3. AREA PANEL
panel_ids = ["L02", "L07", "L08", "L09", "L10", "L12", "L13", "L14", "L15", "L18", "L19",
             "D01", "D02", "D03", "D04", "D05", "D06", "D09", "D10", "D11", "D15", "D18",
             "T07", "T09", "T11", "T12", "C01", "C02", "C05", "C06", "H01", "H04", "H05"]
panel = []
for pid in panel_ids:
    r = VROW[pid]
    panel.append({"id": pid, "label": r["label"], "value": r["value"], "unit": r["unit"],
                  "as_of": r["as_of"], "source": r["source"],
                  "source_url": SRC[r["source"]]["url"], "source_publisher": SRC[r["source"]]["publisher"]})

# ============================================================ 4. MONTE CARLO WITH BLACK SWANS
# Explicit, published distributions. Nothing is hidden.
MC = {
    "trials": 20_000,
    "seed": 424242,
    "distributions": {
        "exit_cap": "triangular(5.5%, 6.5%, 7.5%)",
        "escalation": "uniform(1.5%, 2.5%)",
        "rent_reset_at_renewal": "triangular(0.90, 1.00, 1.15)",
        "renewal_probability": "uniform(55%, 85%)",
        "netlease_yield_for_reinvestment": "triangular(5.8%, 6.8%, 7.4%)  [range of SEC-filed net-lease yields read this session]",
        "earthquake_M6.7plus_near_site_per_year": "3.0%  [derived: USGS gives 60% over 30 years -> 1-(1-p)^30 = 0.60]",
        "earthquake_loss_if_it_hits": "triangular(5%, 20%, 50%) of asset value",
        "earthquake_insurance_recovery": "uniform(0%, 80%) of the loss",
        "wildfire_affecting_parcel_per_year": "0.2%",
        "wildfire_loss_if_it_hits": "triangular(5%, 30%, 100%) of asset value",
        "wildfire_insurance_recovery": "uniform(0%, 90%) of the loss",
        "tenant_credit_event_per_year": "2.0%  -> vacancy of 18 months plus a full re-tenanting cost",
        "diversification_factor_on_reinvested_portfolio": "0.40  ANALYST: a multi-property net-lease book absorbs the same shock at about 40% of single-asset severity",
    },
    "notes": [
        "The sell path is modelled as: sell, reinvest in diversified net lease at the drawn yield, then absorb the same hazards at the diversification factor. It is NOT modelled as risk-free.",
        "The hold path keeps one tenant and one parcel, so it absorbs the full single-asset severity.",
        "Rates and caps are held at the drawn values for the whole horizon; no path re-levers.",
    ],
}

def clamp(x, a, b):
    return max(a, min(b, x))

def tri(rng, a, m, b):
    return rng.triangular(a, b, m)

rng = random.Random(MC["seed"])
EQ_P = 1.0 - (1.0 - 0.60) ** (1.0 / 30.0)      # from USGS 60% in 30 years (S23)
WF_P = 0.002
CR_P = 0.02
DIV = 0.40

def one_asset_shock_path(rng, years, value_at_start):
    """Return the total after-insurance loss fraction experienced over `years` on one asset."""
    lost = 0.0
    for _ in range(years):
        if rng.random() < EQ_P:
            loss = tri(rng, 0.05, 0.20, 0.50) * value_at_start
            rec = rng.uniform(0.0, 0.80)
            lost += loss * (1.0 - rec)
        if rng.random() < WF_P:
            loss = tri(rng, 0.05, 0.30, 1.00) * value_at_start
            rec = rng.uniform(0.0, 0.90)
            lost += loss * (1.0 - rec)
    return lost


sell_w, hold_w = [], []
sell_shock_w, hold_shock_w = [], []
for _ in range(MC["trials"]):
    cap = tri(rng, 0.055, 0.065, 0.075)
    g = rng.uniform(0.015, 0.025)
    rp = tri(rng, 0.90, 1.00, 1.15)
    p = rng.uniform(0.55, 0.85)
    ny = tri(rng, 0.058, 0.068, 0.074)

    s = sell_now(cap, ny)
    # sell path: reinvested book, hazards at diversification factor, over the full horizon
    sell_shock = DIV * one_asset_shock_path(rng, HORIZON - START, s["net_proceeds"])
    sell_shock_w.append(sell_shock)
    sell_w.append(s["wealth_horizon"] - sell_shock * (1.0 + ny) ** ((HORIZON - START) / 2.0))

    # hold path: full single-asset exposure, plus tenant credit events
    ren = renew_and_hold(cap, reprice=rp, g=g, r=TREASURY)
    dr = do_not_renew(cap, g=g, r=TREASURY)
    h = p * ren["wealth_horizon"] + (1 - p) * dr["wealth_horizon"]
    equity_value = value_from_rent(BASE_RENT * (1 + g) ** (EXPIRY - START), cap)
    own_shock = one_asset_shock_path(rng, HORIZON - START, equity_value)
    hold_shock_w.append(own_shock)
    h -= own_shock
    for _y in range(EXPIRY - START, HORIZON - START):
        if rng.random() < CR_P:
            h -= TIFFIN
    hold_w.append(h)


def pct(xs, q):
    s = sorted(xs)
    k = (len(s) - 1) * q
    f = int(k)
    c = min(f + 1, len(s) - 1)
    return s[f] + (s[c] - s[f]) * (k - f)


def ce(xs, gamma=2.5):
    """Certainty equivalent of the terminal wealth distribution under CRRA utility."""
    if gamma == 1.0:
        return 0.0
    m = sum((x ** (1 - gamma)) for x in xs) / len(xs)
    return m ** (1 / (1 - gamma))


P_WEALTH = 100_000.0 / BASE_RENT   # normalise to $100k of NOI
mc_sell = {"mean": sum(sell_w) / len(sell_w), "p05": pct(sell_w, .05), "p50": pct(sell_w, .50),
           "p95": pct(sell_w, .95), "ce_crra2_5": ce(sell_w)}
mc_hold = {"mean": sum(hold_w) / len(hold_w), "p05": pct(hold_w, .05), "p50": pct(hold_w, .50),
           "p95": pct(hold_w, .95), "ce_crra2_5": ce(hold_w)}
wins = sum(1 for a, b in zip(sell_w, hold_w) if a > b)
for d in (mc_sell, mc_hold):
    for k in list(d.keys()):
        d[k] = round(d[k], 0)
    d["per_100k_noi"] = {k: round(v * P_WEALTH, 0) for k, v in d.items() if isinstance(v, (int, float))}
def shock_stats(xs, base):
    return {"mean_loss_usd": round(sum(xs) / len(xs), 0),
            "loss_pct_of_value_p25": round(100 * pct(xs, .25) / base, 2),
            "loss_pct_of_value_p50": round(100 * pct(xs, .50) / base, 2),
            "loss_pct_of_value_p75": round(100 * pct(xs, .75) / base, 2),
            "loss_pct_of_value_p90": round(100 * pct(xs, .90) / base, 2),
            "loss_pct_of_value_p99": round(100 * pct(xs, .99) / base, 2),
            "prob_any_loss_pct": round(100 * sum(1 for x in xs if x > 0.0) / len(xs), 1)}

base_value = value_from_rent(BASE_RENT, 0.065)
mc_shocks = {"single_asset_hold_path": shock_stats(hold_shock_w, base_value),
             "diversified_sell_path": shock_stats(sell_shock_w, net_proceeds(base_value)),
             "value_used_usd": round(base_value, 0)}
mc = {"config": MC, "sell_path": mc_sell, "hold_path": mc_hold, "hazard_loss_distribution": mc_shocks,
      "prob_sell_beats_hold": round(wins / len(sell_w), 4),
      "prob_hold_beats_sell": round(1 - wins / len(sell_w), 4),
      "mean_difference_sell_minus_hold": round(sum(sell_w) / len(sell_w) - sum(hold_w) / len(hold_w), 0),
      "eq_annual_probability_used": round(EQ_P, 5)}

# ============================================================ output
out = {
    "generated_by": "session-4ed347de/scripts/model.py",
    "generated_for": "2026-11-08",
    "verified_inputs": {
        "treasury_10y_pct": round(TREASURY * 100, 2), "treasury_source": "C01/S10",
        "netlease_fy2025_pct": round(NETLEASE_FY2025 * 100, 2), "netlease_fy2025_source": "C03/S12",
        "netlease_q3_2026_pct": round(NETLEASE_Q3_2026 * 100, 2), "netlease_q3_2026_source": "C04/S13",
        "county_dtt_pct": round(COUNTY_DTT * 100, 3), "city_dtt_pct": round(CITY_DTT * 100, 3),
        "ula_tier1_pct": round(ULA_T1 * 100, 2), "ula_tier2_pct": round(ULA_T2 * 100, 2),
        "ula_thresholds": ULA_THRESH,
    },
    "analyst_assumptions": A,
    "observation_reinvestment_rate": {
        "published_model_uses_pct": 4.90,
        "verified_10y_treasury_pct": round(TREASURY * 100, 2),
        "effect_on_base_case_sell_wealth_usd": round(
            sell_now(0.065, TREASURY)["wealth_horizon"] - sell_now(0.065, TREASURY_PUBLISHED_ASSUMPTION)["wealth_horizon"], 0),
        "note": "The root model's A10 'Reinvestment yield if sold' is 4.90%, labelled an analyst assumption. "
                "The verified 10-year Treasury print on 2026-11-05 was 4.84%. Using the verified print lowers the "
                "sell-path wealth figure slightly. Not an error; recorded so the assumption is not read as a verified value.",
    },
    "reproduction_of_published_model": reproduction,
    "scenarios": [],
    "yield_sensitivity": {"grid": yield_grid, "breakeven_yield_pct": round(100 * y_exact, 3),
                          "base_hold_wealth": base_hold},
    "area_panel": panel,
    "monte_carlo": mc,
}

for sc in SCENARIOS:
    m = evaluate(sc["exit_cap"], sc["esc"], sc["reprice"], sc["renew_prob"])
    monthly = {
        "id": sc["id"], "label": sc["label"], "exit_cap": sc["exit_cap"], "escalation": sc["esc"],
        "renewal_probability": sc["renew_prob"], "rent_reset": sc["reprice"],
    }
    monthly.update({k: round(v, 2) if isinstance(v, float) else v for k, v in m.items()})
    out["scenarios"].append(monthly)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1)

# ============================================================ console summary
print(f"reproduction of published root model: {reproduction['status'].upper()} "
      f"({len(reproduction['checked'])} values checked, {len(reproduction['mismatches'])} mismatches)")
print(f"base hold wealth                 ${base_hold:,.0f}")
print(f"breakeven net-lease yield        {100*y_exact:.2f}%")
print(f"  FY2025 yield used by published model {100*NETLEASE_FY2025:.2f}% -> sell wealth "
      f"${sell_now(0.065, NETLEASE_FY2025)['wealth_horizon']:,.0f}")
print(f"  Q3 2026 SEC-filed yield              {100*NETLEASE_Q3_2026:.2f}% -> sell wealth "
      f"${sell_now(0.065, NETLEASE_Q3_2026)['wealth_horizon']:,.0f}")
print(f"monte carlo ({MC['trials']} trials): P(sell beats hold) = {mc['prob_sell_beats_hold']:.1%}")
print(f"  sell mean ${mc_sell['mean']:,.0f}  p05 ${mc_sell['p05']:,.0f}  CE ${mc_sell['ce_crra2_5']:,.0f}")
print(f"  hold mean ${mc_hold['mean']:,.0f}  p05 ${mc_hold['p05']:,.0f}  CE ${mc_hold['ce_crra2_5']:,.0f}")
print("wrote", os.path.relpath(OUT, ROOT))
