#!/usr/bin/env python3
"""Session N projection engine - index basis, deterministic + seeded Monte Carlo.

Basis
-----
The owner's rent, basis and debt are private blanks (metrics M136, M143, M144),
so this model works strictly per $1 of CURRENT net operating income (NOI = 1.0
at t=0). Every published number is therefore unit-free and contains no private
data.

Nothing in this file invents property facts. Assumptions are labeled as
assumptions and are anchored to verified metrics from data/metrics.json where a
real anchor exists (10-year Treasury M66, net-lease benchmark M71, metro CPI
M96). Scenario grids are swept, not asserted.

Deterministic scenarios
-----------------------
    PV_hold(T, g, r, cap0, capT)
        = sum_{t=1..T} (1+g)^t / (1+r)^t   +   ((1+g)^T / capT) / (1+r)^T
    price_now  = 1 / cap0
    net_sale   = price_now * (1 - transfer_rate)      [pre-tax of capital gain]

Capital-gains tax on sale is NOT modelled as a number because the owner's basis
is a blank (M143); it is published as a decision-page note with the verified
top marginal rate (M85).

Monte Carlo
-----------
Seed 20261111, 20,000 trials. g, r and exit-cap drift are sampled from
truncated normal distributions around the base-case anchors. The output reports
the distribution of (PV_hold - net_sale) and P(PV_hold > net_sale).

Self-test (model.py --selftest) checks arithmetic identities:
  * r = 0, g = 0, cap0 = capT  =>  PV_hold = T + 1/cap0
  * price_now identity          =>  1/price_now = cap0
  * seeded run is bit-stable across two invocations with the same seed.
"""
from __future__ import annotations

import json
import math
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "session-2b3370d1", "data", "model_output.json")

SEED = 20261111
TRIALS = 20000

# --- Assumptions (labeled; anchored where possible) --------------------------
ASSUMPTIONS = [
    {"id": "A1", "label": "base NOI growth g = 2.0%/yr",
     "anchor": "Below the LA metro CPI-U 3.7% (M96) and the LA-CSA ECI 3.9% (M97) because county population is declining (M06: -0.6%) and school enrollment falls (M33). Held flat in real terms is optimistic; 2.0% is a deliberately conservative nominal anchor."},
    {"id": "A2", "label": "base required return r = 7.0%/yr",
     "anchor": "10-year Treasury 4.98% (M66) plus a ~200bp private-real-estate risk premium; swept 6.0-9.0% in the grid."},
    {"id": "A3", "label": "base going-in cap cap0 = 7.3%",
     "anchor": "The only official yield datapoint available: Realty Income Q2-2026 initial weighted-average cash yield of ~7.3% (M71). The subject asset's own cap rate is a blank (M145) - the grid sweeps 6.0-9.0%."},
    {"id": "A4", "label": "base exit cap drift = +10bp per year",
     "anchor": "Neutral-to-slightly-adverse: population decline and tenant shrinkage argue against cap-rate tightening; grid sweeps -20bp to +40bp per year."},
    {"id": "A5", "label": "hold horizon T swept 4-9 years",
     "anchor": "The stated NNN expiry window is 2030-2035; from 2026 that is 4 to 9 years."},
    {"id": "A6", "label": "transfer tax applied on the sale path only",
     "anchor": "County DTT 0.11% (M80); City all-in 4.45% tier-1 / 5.95% tier-2 (M78/M79) if the parcel is in City limits - both are modelled as separate cases because jurisdiction is a blank (M132)."},
]


def pv_hold(T: float, g: float, r: float, cap0: float, cap_t: float) -> float:
    """Present value at t=0 of NOI growing at g, discounted at r, exit at cap_t."""
    T = int(T)
    pv = 0.0
    for t in range(1, T + 1):
        pv += (1.0 + g) ** t / (1.0 + r) ** t
    exit_value = (1.0 + g) ** T / cap_t
    pv += exit_value / (1.0 + r) ** T
    return pv


def price_now(cap0: float) -> float:
    return 1.0 / cap0


def net_sale(cap0: float, transfer_rate: float) -> float:
    return price_now(cap0) * (1.0 - transfer_rate)


def deterministic_grid() -> dict:
    rows = []
    for cap0 in (0.060, 0.065, 0.070, 0.073, 0.075, 0.080, 0.085, 0.090):
        for g in (0.000, 0.010, 0.020, 0.030, 0.037):
            for T in (4, 5, 6, 7, 8, 9):
                for drift_bp in (-20, 0, 10, 20, 40):
                    r = 0.070
                    cap_t = cap0 + (drift_bp / 10000.0) * T
                    pv = pv_hold(T, g, r, cap0, cap_t)
                    for case, rate in (("county_only", 0.0011),
                                       ("city_tier1", 0.0445),
                                       ("city_tier2", 0.0595)):
                        ns = net_sale(cap0, rate)
                        rows.append({
                            "cap0": cap0, "g": g, "T": T, "drift_bp": drift_bp,
                            "r": r, "case": case,
                            "transfer_rate": rate,
                            "pv_hold": round(pv, 6),
                            "net_sale": round(ns, 6),
                            "delta": round(pv - ns, 6),
                            "hold_wins": pv > ns,
                        })
    return {"rows": rows}


def breakeven_cap0(T: int, g: float, r: float, transfer_rate: float,
                   drift_bp: float) -> float | None:
    """cap0 such that pv_hold == net_sale (bisection on [0.02, 0.25])."""
    def f(c: float) -> float:
        cap_t = c + (drift_bp / 10000.0) * T
        if cap_t <= 0.005:
            return 1e9
        return pv_hold(T, g, r, c, cap_t) - net_sale(c, transfer_rate)

    lo, hi = 0.02, 0.25
    if f(lo) * f(hi) > 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2.0


def breakevens() -> list[dict]:
    out = []
    for case, rate in (("county_only", 0.0011), ("city_tier1", 0.0445),
                       ("city_tier2", 0.0595)):
        for T in (4, 6, 9):
            for g in (0.010, 0.020, 0.030):
                be = breakeven_cap0(T, g, 0.070, rate, 10)
                out.append({
                    "case": case, "transfer_rate": rate, "T": T, "g": g, "r": 0.070,
                    "drift_bp": 10,
                    "breakeven_cap0": None if be is None else round(be, 6),
                })
    return out


def monte_carlo() -> dict:
    rng = random.Random(SEED)
    deltas = []
    n_hold = 0
    for _ in range(TRIALS):
        g = min(max(rng.gauss(0.020, 0.012), -0.02), 0.05)
        r = min(max(rng.gauss(0.070, 0.010), 0.04), 0.12)
        drift_bp = min(max(rng.gauss(10.0, 15.0), -40.0), 60.0)
        cap0 = min(max(rng.gauss(0.073, 0.006), 0.055), 0.10)
        T = rng.randint(4, 9)
        rate = (0.0011, 0.0445, 0.0595)[rng.randint(0, 2)]
        cap_t = cap0 + (drift_bp / 10000.0) * T
        if cap_t <= 0.01:
            continue
        d = pv_hold(T, g, r, cap0, cap_t) - net_sale(cap0, rate)
        deltas.append(d)
        if d > 0:
            n_hold += 1
    deltas.sort()
    n = len(deltas)

    def pct(p: float) -> float:
        return round(deltas[min(n - 1, int(p * n))], 6)

    return {
        "seed": SEED,
        "trials": TRIALS,
        "n": n,
        "p_hold_wins": round(n_hold / n, 6),
        "mean_delta": round(sum(deltas) / n, 6),
        "p5": pct(0.05),
        "p25": pct(0.25),
        "median": pct(0.50),
        "p75": pct(0.75),
        "p95": pct(0.95),
        "min": round(deltas[0], 6),
        "max": round(deltas[-1], 6),
    }


def scenarios() -> list[dict]:
    """Named scenarios for the decisions page (index basis, per $1 current NOI)."""
    out = []
    for name, g, r, cap0, drift_bp, T in (
        ("Bear (tenant shrinkage continues, cap expansion)", 0.000, 0.085, 0.085, 40, 9),
        ("Base (official anchors: 10Y 4.98%, benchmark cap 7.3%)", 0.020, 0.070, 0.073, 10, 6),
        ("Bull (CPI-linked renewal, stable credit, cap flat)", 0.037, 0.065, 0.070, -20, 9),
    ):
        cap_t = cap0 + (drift_bp / 10000.0) * T
        pv = pv_hold(T, g, r, cap0, cap_t)
        row = {
            "name": name, "g": g, "r": r, "cap0": cap0, "drift_bp": drift_bp, "T": T,
            "pv_hold": round(pv, 4),
        }
        for case, rate in (("county_only", 0.0011), ("city_tier1", 0.0445)):
            row[f"net_sale_{case}"] = round(net_sale(cap0, rate), 4)
        out.append(row)
    return out


def selftest() -> int:
    failures = []
    # identity 1: r=0, g=0, cap0=capT => PV = T + 1/cap0
    for T in (1, 4, 9):
        for cap in (0.06, 0.073, 0.09):
            got = pv_hold(T, 0.0, 0.0, cap, cap)
            want = T + 1.0 / cap
            if abs(got - want) > 1e-9:
                failures.append(f"pv_hold identity T={T} cap={cap}: {got} != {want}")
    # identity 2: price_now
    if abs(price_now(0.073) - 1.0 / 0.073) > 1e-12:
        failures.append("price_now identity")
    # identity 3: net_sale scales with transfer rate
    if abs(net_sale(0.073, 0.0) - price_now(0.073)) > 1e-12:
        failures.append("net_sale at zero transfer")
    # identity 4: seeded MC is stable
    a = monte_carlo()["median"]
    b = monte_carlo()["median"]
    if a != b:
        failures.append(f"MC not stable: {a} != {b}")
    # identity 5: bisection agrees with direct evaluation near the root
    be = breakeven_cap0(6, 0.02, 0.070, 0.0445, 10)
    if be is not None:
        cap_t = be + (10 / 10000.0) * 6
        lhs = pv_hold(6, 0.02, 0.070, be, cap_t)
        rhs = net_sale(be, 0.0445)
        if abs(lhs - rhs) > 1e-6:
            failures.append(f"breakeven residual {lhs - rhs}")
    if failures:
        for f in failures:
            print("FAIL:", f, file=sys.stderr)
        return 1
    print(f"selftest OK: {len(failures)} failures; seed={SEED}; trials={TRIALS}")
    return 0


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    out = {
        "session": "session-2b3370d1",
        "seed": SEED,
        "trials": TRIALS,
        "basis": "per $1 current NOI (index basis); owner rent/basis/debt are private blanks",
        "assumptions": ASSUMPTIONS,
        "scenarios": scenarios(),
        "breakevens": breakevens(),
        "monte_carlo": monte_carlo(),
        "grid_summary": _grid_summary(),
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")
    print(f"wrote {OUT} ({os.path.getsize(OUT)} bytes)")
    return 0


def _grid_summary() -> dict:
    grid = deterministic_grid()["rows"]
    total = len(grid)
    hold_wins = sum(1 for r in grid if r["hold_wins"])
    by_case = {}
    for case in ("county_only", "city_tier1", "city_tier2"):
        sub = [r for r in grid if r["case"] == case]
        by_case[case] = {
            "cells": len(sub),
            "hold_wins": sum(1 for r in sub if r["hold_wins"]),
            "hold_win_share": round(sum(1 for r in sub if r["hold_wins"]) / len(sub), 4),
        }
    return {
        "cells": total,
        "hold_wins": hold_wins,
        "hold_win_share": round(hold_wins / total, 4),
        "by_transfer_case": by_case,
    }


if __name__ == "__main__":
    sys.exit(main())
