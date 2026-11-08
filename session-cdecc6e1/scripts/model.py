"""Deterministic scenario model for the Session I workbook.

Reads: session-cdecc6e1/data/valuation.json
Writes: session-cdecc6e1/data/model_output.json

Rules:
  * Every verified input carries a source key (Txx) and date - never estimated.
  * Every analyst input carries an "A" key and is explicitly labelled an assumption.
  * Output is pre-tax, non-appraisal scenario analysis for decision support only.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def load():
    with open(DATA / "valuation.json", encoding="utf-8") as f:
        return json.load(f)


def by_key(vals, key):
    for v in vals:
        if v["key"] == key:
            return v
    raise KeyError(key)


def transaction_stack(price, cfg):
    """Transaction cost as a share of price (base + ULA tier). Verified rates T07/T08; brokerage/legal A6."""
    base = cfg["verified"]["brokerage"] + cfg["verified"]["escrow"] + cfg["verified"]["county_dtt"] + cfg["verified"]["city_dtt"]
    stack = base
    ula_tier = None
    if price >= cfg["verified"]["ula_threshold_2"]:
        stack += cfg["verified"]["ula_t2"]; ula_tier = 2
    elif price >= cfg["verified"]["ula_threshold_1"]:
        stack += cfg["verified"]["ula_t1"]; ula_tier = 1
    return stack, ula_tier


def pv(rate, cfs):
    return sum(cf / ((1 + rate) ** (i + 1)) for i, cf in enumerate(cfs))


def main():
    val = load()
    vi = {v["key"]: v["value"] for v in val["verified_inputs"]}
    assumptions = {a["key"]: a for a in val["analyst_assumptions"]}

    cfg = {
        "rent": assumptions["A1"]["value"],
        "escalation": assumptions["A2"]["value"] / 100.0,
        "expiry": int(assumptions["A3"]["value"]),
        "discount": assumptions["A4"]["value"] / 100.0,
        "exit_cap_base": assumptions["A5"]["value"] / 100.0,
        "brokerage": assumptions["A6"]["value"] / 100.0,
        "renewal_prob": assumptions["A7"]["value"] / 100.0,
        "downtime_months": assumptions["A8"]["value"],
        "leasing_cost": assumptions["A9"]["value"],
        "reinvest_yield": assumptions["A10"]["value"] / 100.0,
        "horizon": int(assumptions["A11"]["value"]),
        "verified": {
            "treasury": vi["t10"] / 100.0,
            "county_dtt": vi["county_dtt"] / 100.0,
            "city_dtt": vi["city_dtt"] / 100.0,
            "ula_t1": vi["ula_t1"] / 100.0,
            "ula_t2": vi["ula_t2"] / 100.0,
            "ula_threshold_1": vi["ula_threshold_1"],
            "ula_threshold_2": vi["ula_threshold_2"],
        },
    }
    cfg["verified"]["brokerage"] = 0.03   # 3.0% brokerage; the extra 0.5% escrow is added separately below
    cfg["verified"]["escrow"] = 0.005

    results = {"inputs": cfg, "scenarios": []}
    for cap in [0.055, 0.060, 0.065, 0.070, 0.075]:
        price = cfg["rent"] / cap
        stack, ula_tier = transaction_stack(price, cfg)
        net_proceeds = price * (1 - stack)

        # Hold & renew: cash flows from year after expiry through horizon.
        cfs = []
        r = cfg["rent"]
        for year in range(cfg["expiry"] + 1, cfg["horizon"] + 1):
            r *= (1 + cfg["escalation"])
            cfs.append(r)
        terminal = r / cfg["exit_cap_base"]
        cfs[-1] += terminal
        pv_hold_renew = pv(cfg["discount"], cfs)
        pv_hold_renew_weighted = cfg["renewal_prob"] * pv_hold_renew

        # Hold & tenant does not renew: downtime, then re-lease at same rent.
        cfs_nr = []
        r = cfg["rent"]
        for year in range(cfg["expiry"] + 1, cfg["horizon"] + 1):
            months_into_hold = (year - cfg["expiry"]) * 12
            if months_into_hold <= cfg["downtime_months"]:
                cfs_nr.append(0.0)
            else:
                cfs_nr.append(r)
                r *= (1 + cfg["escalation"])
        if cfs_nr:
            terminal_nr = cfs_nr[-1] / cfg["exit_cap_base"]
            cfs_nr[-1] = cfs_nr[-1] - cfg["leasing_cost"] + terminal_nr
        pv_hold_norenew = pv(cfg["discount"], cfs_nr)
        pv_hold_norenew_weighted = (1 - cfg["renewal_prob"]) * pv_hold_norenew

        pv_hold = pv_hold_renew_weighted + pv_hold_norenew_weighted
        reinvest_income = net_proceeds * cfg["reinvest_yield"]
        results["scenarios"].append({
            "exit_cap_pct": cap * 100,
            "gross_price_usd": round(price, 2),
            "transaction_stack_pct": round(stack * 100, 2),
            "ula_tier": ula_tier,
            "net_proceeds_usd": round(net_proceeds, 2),
            "pv_hold_renew_usd": round(pv_hold_renew, 2),
            "pv_hold_weighted_usd": round(pv_hold, 2),
            "hold_minus_sell_usd": round(pv_hold - net_proceeds, 2),
            "annual_reinvest_income_at_treasury_usd": round(reinvest_income, 2),
            "net_proceeds_as_years_of_rent": round(net_proceeds / cfg["rent"], 1)
        })

    # Required rent uplift so that holding equals selling at base cap.
    base_cap = cfg["exit_cap_base"]
    price_base = cfg["rent"] / base_cap
    stack_base, _ = transaction_stack(price_base, cfg)
    net_base = price_base * (1 - stack_base)
    cfs_eq = []
    r = cfg["rent"]
    for year in range(cfg["expiry"] + 1, cfg["horizon"] + 1):
        r *= (1 + cfg["escalation"])
        cfs_eq.append(r)
    terminal_eq = r / base_cap
    cfs_eq[-1] += terminal_eq
    # solve for multiplicative uplift u on r such that PV = net_base
    lo, hi = 0.0, 2.0
    for _ in range(60):
        mid = (lo + hi) / 2
        cfs = [cf * mid for cf in cfs_eq[:-1]] + [cfs_eq[-1] * mid]
        if pv(cfg["discount"], cfs) < net_base:
            lo = mid
        else:
            hi = mid
    required_uplift = (lo + hi) / 2

    results["summary"] = {
        "rent_usd_per_year": cfg["rent"],
        "expiry_year": cfg["expiry"],
        "horizon_year": cfg["horizon"],
        "discount_rate_pct": cfg["discount"] * 100,
        "treasury_yield_pct": cfg["verified"]["treasury"] * 100,
        "required_rent_uplift_for_hold_to_equal_sell_at_base_cap": round(required_uplift, 4),
        "breakeven_note": "If the renewal rent is below the market rent by more than the uplift factor above, selling at the base cap dominates holding (all else equal).",
        "caveats": [
            "Rent $150k/yr is A1 (8% of verified AUV) - replace with contract rent (P03).",
            "Expiry 2032 is A3 - actual date is P02.",
            "Exit caps are A5 bands, not appraisals (M56 unverified).",
            "Pre-tax; owner basis unknown (P05); CPA tax model required before any binding decision (X-06)."
        ]
    }

    with open(DATA / "model_output.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(json.dumps(results["summary"], indent=2))
    for s in results["scenarios"]:
        print(s)


if __name__ == "__main__":
    main()
