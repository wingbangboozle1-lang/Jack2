#!/usr/bin/env python3
"""Normalized, pre-tax/pre-debt scenario engine and official area-projection summaries.

All property cash flows are expressed in units of current annualized NOI = 100.
This is NOT an appraisal, NOT a dollar rent estimate, and NOT a probability model.
Tax/debt/insurance/owner-specific inputs are deliberately excluded because they are unknown.
"""
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
DATA = ROOT / "data"
MODEL_DIR = ROOT / "model"
DATA.mkdir(exist_ok=True)
MODEL_DIR.mkdir(exist_ok=True)

START_YEAR = 2026
HORIZON = 2036
YEARS = list(range(START_YEAR + 1, HORIZON + 1))
CURRENT_NOI = 100.0

DEFAULTS = dict(
    entry_cap=0.065,          # analyst sale-pricing scenario, not subject cap rate
    exit_cap=0.075,           # analyst terminal scenario
    short_term_cap=0.085,     # analyst pre-expiry sale scenario
    escalation=0.02,          # analyst contract-escalation scenario
    reset=1.00,               # analyst market-renewal reset scenario
    extension_cost=50.0,      # analyst one-time cost at expiry, NOI units
    downtime=1,               # analyst vacate-branch downtime, years
    retenant_cost=150.0,      # analyst one-time cost, NOI units
    reuse_factor=0.85,        # analyst re-let rent factor
    sale_cost=0.03,           # analyst transaction-cost scenario
    reinvest=0.0486,          # Treasury CMT context scenario, not executable offer
    expiry=2032,              # midpoint scenario only; actual expiry unknown
)


def ula_rate(price: float, in_city: bool = True, closing_after_june_2026: bool = True) -> float:
    """Current City of LA ULA rate. Strict lower threshold; upper threshold inclusive.

    Historical pre-July-2026 thresholds are intentionally not modeled here.
    County transfer tax and exemptions are separate and require transaction facts.
    """
    if not closing_after_june_2026:
        raise ValueError("This helper models only closings after June 30, 2026.")
    if not in_city or price <= 0:
        return 0.0
    if price >= 10_900_000:
        return 0.055
    if price > 5_400_000:
        return 0.04
    return 0.0


def city_base_transfer_tax(price: float, in_city: bool = True) -> float:
    if not in_city or price <= 100:
        return 0.0
    return math.ceil(price / 500.0) * 2.25


def noi_path(expiry, escalation, reset, extension_cost, downtime, retenant_cost, reuse_factor, branch):
    """Return annual net operating cash flow before debt/tax for 2027-2036.

    Lease is assumed paid through the expiry year; reset/vacancy begins the next year.
    branch: 'renew' or 'vacate'. Costs are subtracted in the year incurred.
    """
    if branch not in ("renew", "vacate"):
        raise ValueError("branch must be renew or vacate")
    if not (START_YEAR < expiry <= HORIZON):
        raise ValueError("expiry outside model horizon")
    if downtime < 0 or int(downtime) != downtime:
        raise ValueError("downtime must be a nonnegative integer")
    flows = {}
    pre_expiry_noi = None
    stabilized_noi = None
    for year in YEARS:
        if year <= expiry:
            noi = CURRENT_NOI * (1 + escalation) ** (year - START_YEAR)
            if year == expiry:
                pre_expiry_noi = noi
            cost = extension_cost if (branch == "renew" and year == expiry) else 0.0
            flows[year] = noi - cost
        else:
            if branch == "renew":
                if stabilized_noi is None:
                    stabilized_noi = pre_expiry_noi * reset
                else:
                    stabilized_noi *= (1 + escalation)
                flows[year] = stabilized_noi
            else:
                vacancy_end = expiry + downtime
                if year <= vacancy_end:
                    cost = retenant_cost if year == vacancy_end else 0.0
                    flows[year] = -cost
                else:
                    if stabilized_noi is None:
                        stabilized_noi = pre_expiry_noi * reuse_factor
                    else:
                        stabilized_noi *= (1 + escalation)
                    flows[year] = stabilized_noi
    return flows


def terminal_noi(flows, escalation):
    """Next-year stabilized NOI for terminal capitalization; zero if still vacant."""
    last = flows[HORIZON]
    if last <= 0:
        return 0.0
    return last * (1 + escalation)


def fv_cashflows(flows, terminal_value, reinvest, sale_year=HORIZON):
    total = 0.0
    for year, cf in flows.items():
        if year <= sale_year:
            total += cf * (1 + reinvest) ** (HORIZON - year)
    if terminal_value:
        total += terminal_value * (1 + reinvest) ** (HORIZON - sale_year)
    return total


def pv_cashflows(flows, terminal_value, discount, sale_year=HORIZON):
    total = 0.0
    for year, cf in flows.items():
        if year <= sale_year:
            total += cf / (1 + discount) ** (year - START_YEAR)
    if terminal_value:
        total += terminal_value / (1 + discount) ** (sale_year - START_YEAR)
    return total


def evaluate(p):
    g = p["escalation"]
    cost = p["sale_cost"]
    r = p["reinvest"]
    expiry = p["expiry"]
    results = {}

    # A: sell now; proceeds reinvested to horizon.
    gross_now = CURRENT_NOI / p["entry_cap"]
    net_now = gross_now * (1 - cost)
    results["sell_now"] = dict(
        fv=net_now * (1 + r) ** (HORIZON - START_YEAR),
        pv=net_now,
        sale_year=START_YEAR,
        gross_sale=gross_now,
        note="Pre-tax/pre-debt; ULA not applied because NOI units are not dollars.",
    )

    # B: hold without extension, sell one year before expiry at a short-term cap.
    flows = noi_path(expiry, g, p["reset"], 0.0, p["downtime"], p["retenant_cost"], p["reuse_factor"], "renew")
    sell_year = max(START_YEAR + 1, expiry - 1)
    next_noi = CURRENT_NOI * (1 + g) ** (sell_year + 1 - START_YEAR)
    terminal = next_noi / p["short_term_cap"] * (1 - cost)
    results["sell_before_expiry"] = dict(
        fv=fv_cashflows(flows, terminal, r, sell_year),
        pv=pv_cashflows(flows, terminal, 0.08, sell_year),
        sale_year=sell_year,
        gross_sale=next_noi / p["short_term_cap"],
        note="Sells at end of expiry-1; buyer receives expiry-year NOI.",
    )

    # C: extend/renew at expiry and hold to horizon.
    flows_renew = noi_path(expiry, g, p["reset"], p["extension_cost"], p["downtime"], p["retenant_cost"], p["reuse_factor"], "renew")
    term_noi = terminal_noi(flows_renew, g)
    terminal = term_noi / p["exit_cap"] * (1 - cost)
    results["extend_hold"] = dict(
        fv=fv_cashflows(flows_renew, terminal, r),
        pv=pv_cashflows(flows_renew, terminal, 0.08),
        sale_year=HORIZON,
        gross_sale=term_noi / p["exit_cap"],
        annual_flows=flows_renew,
        note="Deterministic renewal branch; no renewal probability assigned.",
    )

    # D: extend/renew, sell two years after expiry, reinvest proceeds.
    sell_year = min(HORIZON, expiry + 2)
    if sell_year < HORIZON:
        next_noi = flows_renew[sell_year] * (1 + g)
        terminal = next_noi / p["exit_cap"] * (1 - cost)
    else:
        terminal = term_noi / p["exit_cap"] * (1 - cost)
    results["extend_sell"] = dict(
        fv=fv_cashflows(flows_renew, terminal, r, sell_year),
        pv=pv_cashflows(flows_renew, terminal, 0.08, sell_year),
        sale_year=sell_year,
        gross_sale=(flows_renew[sell_year] * (1 + g) / p["exit_cap"]) if sell_year < HORIZON else term_noi / p["exit_cap"],
        note="Sells two years after expiry when possible; otherwise at horizon.",
    )

    # E: tenant vacates at expiry; deterministic downtime/re-let branch.
    flows_vacate = noi_path(expiry, g, p["reset"], 0.0, p["downtime"], p["retenant_cost"], p["reuse_factor"], "vacate")
    term_noi_v = terminal_noi(flows_vacate, g)
    terminal_v = term_noi_v / p["exit_cap"] * (1 - cost)
    results["vacate_hold"] = dict(
        fv=fv_cashflows(flows_vacate, terminal_v, r),
        pv=pv_cashflows(flows_vacate, terminal_v, 0.08),
        sale_year=HORIZON,
        gross_sale=term_noi_v / p["exit_cap"],
        annual_flows=flows_vacate,
        note="Deterministic vacancy branch; not probability-weighted.",
    )
    return results


def breakevens(p, results):
    r = p["reinvest"]
    cost = p["sale_cost"]
    hold_fv = results["extend_hold"]["fv"]
    required_gross_now = hold_fv / ((1 - cost) * (1 + r) ** (HORIZON - START_YEAR))

    def delta(reset):
        q = dict(p, reset=reset)
        return evaluate(q)["extend_hold"]["fv"] - results["sell_now"]["fv"]

    lo, hi = 0.50, 1.50
    if delta(lo) > 0:
        required_reset = lo
    elif delta(hi) < 0:
        required_reset = hi
    else:
        for _ in range(80):
            mid = (lo + hi) / 2
            if delta(mid) > 0:
                hi = mid
            else:
                lo = mid
        required_reset = (lo + hi) / 2
    return dict(
        required_gross_sale_now_to_match_extend_hold=required_gross_now,
        current_gross_sale_now_scenario=CURRENT_NOI / p["entry_cap"],
        required_renewal_reset_to_match_sell_now=required_reset,
        note="Normalized breakevens, pre-tax/pre-debt; not executable prices.",
    )


def build_model():
    base = evaluate(DEFAULTS)
    sensitivity = []
    grids = {
        "expiry": [2030, 2032, 2035],
        "exit_cap": [0.065, 0.075, 0.085],
        "reset": [0.90, 1.00, 1.10],
        "reinvest": [0.0486, 0.074],
        "extension_cost": [0.0, 50.0, 100.0],
    }
    for key, values in grids.items():
        for value in values:
            p = dict(DEFAULTS, **{key: value})
            res = evaluate(p)
            sensitivity.append(dict(factor=key, value=value, fv={k: round(v["fv"], 2) for k, v in res.items()}))
    payload = dict(
        meta=dict(
            as_of="2026-11-08", start_year=START_YEAR, horizon=HORIZON,
            normalized_current_noi=CURRENT_NOI,
            basis="Analyst scenarios only. No actual rent, expiry, debt, tax basis, insurance or offer is known.",
            excluded=["income taxes", "transfer taxes/ULA", "debt service", "insurance premiums", "owner liquidity", "probabilities"],
            reinvestment_context="4.86% is a Treasury CMT observation; 7.4% is a diversified REIT acquisition yield. Neither is a guaranteed executable return.",
        ),
        assumptions=DEFAULTS,
        base={k: {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items()} for k, v in base.items()},
        breakevens=breakevens(DEFAULTS, base),
        sensitivity=sensitivity,
    )
    (MODEL_DIR / "scenarios.json").write_text(json.dumps(payload, indent=2) + "\n")
    return payload


def build_projections():
    metrics = json.loads((DATA / "metrics.json").read_text())["rows"]
    by_id = {r["id"]: r for r in metrics}
    rows = []
    def add(series, start_id, end_id, label, source):
        a, b = by_id[start_id]["value"], by_id[end_id]["value"]
        years = int(by_id[end_id]["period"].split(",")[-1].strip()) - int(by_id[start_id]["period"].split(",")[-1].strip()) if "," in by_id[end_id]["period"] else int(by_id[end_id]["period"]) - int(by_id[start_id]["period"])
        cagr = (b / a) ** (1 / years) - 1
        rows.append(dict(series=label, start=by_id[start_id]["period"], end=by_id[end_id]["period"],
                         start_value=a, end_value=b, total_change_pct=round((b/a-1)*100, 3),
                         cagr_pct=round(cagr*100, 3), source=source,
                         note="Derived from official projections; not a rent, value or cap-rate forecast."))
    add("DOF population", "DP2025", "DP2030", "DOF county population", "S05")
    add("DOF population", "DP2025", "DP2035", "DOF county population", "S05")
    add("DOF population", "DP2025", "DP2040", "DOF county population", "S05")
    add("DOF households", "DH2025", "DH2030", "DOF county households", "S47")
    add("DOF households", "DH2025", "DH2035", "DOF county households", "S47")
    add("DOF households", "DH2025", "DH2040", "DOF county households", "S47")
    add("SCAG population", "SP2019", "SP2030", "SCAG county population planning forecast", "S08")
    add("SCAG population", "SP2019", "SP2050", "SCAG county population planning forecast", "S08")
    add("SCAG households", "SH2019", "SH2030", "SCAG county household planning forecast", "S08")
    add("SCAG households", "SH2019", "SH2050", "SCAG county household planning forecast", "S08")
    add("SCAG employment", "SE2019", "SE2030", "SCAG county employment planning forecast", "S08")
    add("SCAG employment", "SE2019", "SE2050", "SCAG county employment planning forecast", "S08")
    payload = dict(meta=dict(as_of="2026-11-08", note="Official projections kept separate by agency/method; growth rates are derived."), rows=rows)
    (MODEL_DIR / "projections.json").write_text(json.dumps(payload, indent=2) + "\n")
    return payload


def export_csv():
    for name in ["sources", "metrics", "requirements", "risks", "decisions", "flags"]:
        rows = json.loads((DATA / f"{name}.json").read_text())["rows"]
        if not rows:
            continue
        fields = list(rows[0].keys())
        with (DATA / f"{name}.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for r in rows:
                w.writerow({k: (";".join(v) if isinstance(v, list) else v) for k, v in r.items()})


if __name__ == "__main__":
    model = build_model()
    proj = build_projections()
    export_csv()
    print("model base FV:", {k: v["fv"] for k, v in model["base"].items()})
    print("projection rows:", len(proj["rows"]))
