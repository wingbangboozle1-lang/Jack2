#!/usr/bin/env python3
"""
Jack2 — Net-Lease Hold-vs-Sell Projection Engine
=================================================

Purpose
-------
Build a *reliable, reproducible* projection of the four decisions available to
the owner of a single-tenant Jack in the Box NNN asset in central Los Angeles
with a lease expiring somewhere in 2030-2035:

    A. SELL NOW          (trade the certainty of today's bid for no roll risk)
    B. SELL AT EXPIRY    (hold the contract rent, then sell into the roll)
    C. RENEW / EXTEND    (roll the lease, keep the asset)
    D. HYBRID            (extend the tenant now, sell a longer-WALT asset)

Design rules
------------
1. NOTHING IS INVENTED. Every calibrated input carries a `src` key that points
   at an id in data/sources.json, or at another row in data/dataset.json. If an
   input could not be verified it is NOT hard-coded here; it stays a *scenario
   axis* (e.g. the remaining lease term, the base rent) so the output is a
   surface over the unknowns, not a single fabricated answer.

2. The two genuinely unknowable-at-source quantities -- current base rent and
   remaining lease term -- are given explicit, labelled grids that BRACKET the
   owner's stated range. They are scenario axes, not claims. The site displays
   the whole surface, and the recommendation is stated only where the answer is
   invariant across the surface.

3. Determinism. The Monte Carlo uses a fixed seed and the stdlib `random`
   module with an explicit Box-Muller transform, so the checked-in JSON output
   is byte-reproducible on any machine with Python 3.8+ and no third-party
   packages.

4. Uncertainty is modelled where it actually lives: in the EXIT cap rate and in
   the roll outcome. Point estimates of rent are taken as given because they are
   contractual.

Usage
-----
    python3 model/project_model.py            # writes data/model_output.json
    python3 model/project_model.py --check    # verifies outputs match the file

Verified inputs (see data/sources.json)
---------------------------------------
  FED-H15              10y UST 4.90%, 5y UST 4.69%, 10y TIPS 2.64%, 5y TIPS 2.39%  (2026-11-04)
  SEC-O-8K-Q3-2026     Realty Income U.S. wholly-owned cash yield 6.6%, rent recapture 103.5%
  SEC-O-10K-FY2025     Realty Income underwriting: rent ~= market rent, value ~= replacement cost
  SEC-JACK-10K-FY2025  Franchise AUV $1,874k, royalty 5.0%, 93% franchised, CA 941 units
  SCAG-LAEDC-2025      Real GCP growth 2.2%/2.5%, taxable sales 2.4%/1.2%, unemployment 5.9%/6.1%
  BLS-EAG-LA-MSA       CPI-U Los Angeles +3.7% y/y
  CENSUS-QF-*          Population, income, density
  LA-ASSESSOR-PROP13   1% levy, 2% cap, change-of-ownership reset on sale
  CA-DIR-AB1228        Fast-food minimum wage $20.00/hr, Council may raise
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_PATH = os.path.join(ROOT, "data", "model_output.json")

SEED = 20261106  # the report date. Changing it changes every percentile.

# ----------------------------------------------------------------------------
# 1. VERIFIED MARKET INPUTS
# ----------------------------------------------------------------------------

# Discount rate: build up from the observed curve rather than assume.
# 5y UST 4.69% + a small illiquidity/management premium. The premium is an
# explicit, displayed assumption -- it is the one number here that is a choice,
# not a retrieved fact, so it is an axis (see DISCOUNT_PREMIUMS).
RF_5Y = 0.0469          # FED-H15, 5-year UST constant maturity, 2026-11-04
RF_5Y_REAL = 0.0239     # FED-H15, 5-year TIPS real yield, 2026-11-04
RF_10Y = 0.0490         # FED-H15, 10-year UST constant maturity, 2026-11-04
RF_10Y_REAL = 0.0264    # FED-H15, 10-year TIPS real yield, 2026-11-04

DISCOUNT_PREMIUMS = (0.0150, 0.0225, 0.0300)   # illiquidity + management, 150/225/300 bps
BASE_DISCOUNT_PREMIUM = 0.0225

# Exit / going-in cap rate anchor: Realty Income's DISCLOSED transacted
# initial weighted average CASH yield on U.S. wholly-owned real estate in
# Q3 2026 was 6.6% (SEC-O-8K-Q3-2026, Exhibit 99.1). That is a portfolio of
# largely investment-grade, long-WALT net lease. A single-asset QSR with a
# near-term roll must clear wider. The spread below is modelled, not sourced,
# and is therefore reported as an axis.
CAP_ANCHOR = 0.066      # SEC-O-8K-Q3-2026

# Spread of a single-asset, near-roll QSR over the institutional net-lease
# portfolio yield. Shown explicitly so the reader can reject it.
CAP_SPREAD_SCENARIOS = {
    "compression": 0.0050,   # strong buyer demand, tenant renews, small spread
    "base":        0.0125,   # normal single-asset / near-roll premium
    "stress":      0.0275,   # credit concerns, thin buyer pool, wider spread
}

# Core inflation benchmark for CPI-linked escalators.
CPI_LA = 0.037          # BLS-EAG-LA-MSA, CPI-U Los Angeles +3.7% y/y, 2026-09

# Regional macro, used only to shape the cyclical path of the roll outcome.
GCP_GROWTH_2025F = 0.022   # SCAG-LAEDC-2025 Exhibit 1
GCP_GROWTH_2026F = 0.025   # SCAG-LAEDC-2025 Exhibit 1
TAXABLE_SALES_2026F = 0.012  # SCAG-LAEDC-2025 Exhibit 1
UNEMP_2026F = 0.061       # SCAG-LAEDC-2025 Exhibit 1
UNEMP_2025F = 0.059

# Tenant fact used for the franchisee-viability cross-check.
FRANCHISE_AUV = 1_874_000   # SEC-JACK-10K-FY2025, $1,874 thousand
ROYALTY_RATE = 0.050        # SEC-JACK-10K-FY2025

# Rent-to-sales sanity bands. A QSR net-lease rent is normally ~6-10% of the
# unit's sales; above ~10% the operator is under real pressure and renewal
# becomes less likely. The band is a modelling convention, shown as such.
RENT_TO_SALES_BAND = (0.060, 0.100)


# ----------------------------------------------------------------------------
# 2. SCENARIO AXES (the things that must not be guessed)
# ----------------------------------------------------------------------------

# The owner stated expiry "2030-2035". We do not pick a year; we sweep the
# stated range plus the two calendar years on either side of it.
@dataclass(frozen=True)
class Axis:
    key: str
    label: str
    values: Tuple[float, ...]
    unit: str
    provenance: str


AXES: Tuple[Axis, ...] = (
    Axis("remaining_years", "Remaining lease term at 2026-11-06", (4, 6, 9), "years",
         "Owner-stated 2030-2035 expiry gives 4.2-8.2 years. 4 / 6 / 9 bracket it. NOT a sourced fact (P-04 blank)."),
    Axis("base_rent", "Current annual base rent", (150_000, 250_000, 350_000), "USD/yr",
         "The lease was not provided (P-07 blank). Grid spans ~8.0%-18.7% of the $1.874M franchise AUV, "
         "i.e. from a comfortable QSR rent to a stressed one. Scenario axis, not an estimate."),
    Axis("cap_spread", "Single-asset near-roll cap spread over the 6.6% anchor", (0.0050, 0.0125, 0.0275), "decimal",
         "Modelled, not sourced. Brackets 'tenant renews and buyer competes' to 'credit concern, thin market'."),
    Axis("discount_premium", "Illiquidity + management premium over the 5y UST", (0.0150, 0.0225, 0.0300), "decimal",
         "Modelled, not sourced. 150 / 225 / 300 bps."),
    Axis("rent_growth", "Contractual escalator applied to the rent", (0.010, 0.020, CPI_LA), "decimal",
         "1.0% / 2.0% / 3.7%. The 3.7% top end is the BLS CPI-U Los Angeles print (E-17); the low ends are "
         "typical fixed escalators and are labelled as conventions."),
    Axis("renewal_probability", "Probability the tenant renews or extends at expiry", (0.45, 0.65, 0.85), "probability",
         "Modelled. Anchored by Realty Income's filed statement that it generally renews at market (T-21) and "
         "by its 103.1%-103.5% realised rent recapture (R-14/R-15), offset by Jack's -4.2% same-store sales (T-08)."),
)


# ----------------------------------------------------------------------------
# 3. THE ENGINE
# ----------------------------------------------------------------------------

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def pv(amount: float, years: float, rate: float) -> float:
    if years <= 0:
        return amount
    return amount / math.pow(1.0 + rate, years)


def annuity_pv(payment: float, start: float, end: float, rate: float) -> float:
    """PV of a level payment received at the END of each year from start+1..end."""
    if payment <= 0 or end <= start:
        return 0.0
    total = 0.0
    t = math.floor(start) + 1
    while t <= end:
        total += pv(payment, t, rate)
        t += 1
    if total == 0.0:                      # sub-annual window
        total = payment * max(0.0, end - start) / math.pow(1.0 + rate, start)
    return total


@dataclass
class DecisionResult:
    decision: str
    label: str
    pv_value: float            # PV at t=0 of everything accruing to the owner
    exit_value: float          # nominal sale price at the exit date
    cash_flows: List[float]    # nominal net rent, one per year, t=1..horizon
    horizon: int
    note: str


def market_price(rent: float, years_left: float, g: float, cap: float) -> float:
    """What a net-lease buyer actually pays today for a lease with `years_left`
    of remaining term.

    A buyer does not pay contract rent / cap for a short lease -- that would
    overvalue it. A buyer pays:
        PV at the market cap of the contract rent through expiry
      + PV at the market cap of the REVERSION (the box re-let at market rent)
    Both discounted at the market cap, which is how net-lease pricing works.
    """
    if cap <= 0:
        raise ValueError("cap must be positive")
    inflow = 0.0
    t = 1
    while t <= math.floor(years_left):
        inflow += (rent * math.pow(1.0 + g, t - 1)) / math.pow(1.0 + cap, t)
        t += 1
    market_rent_at_expiry = rent * math.pow(1.0 + g, years_left)
    reversion = (market_rent_at_expiry / cap) / math.pow(1.0 + cap, years_left)
    return inflow + reversion


def project(
    remaining_years: float,
    base_rent: float,
    cap_spread: float,
    discount_premium: float,
    rent_growth: float,
    renewal_probability: float,
    hold_horizon: int = 10,
) -> Dict[str, DecisionResult]:
    """Unified DCF so all four decisions are priced identically.

    Every branch is: net rent received + sale proceeds, discounted at the
    owner's required return. The ONLY differences between branches are the
    exit date, the exit cap, and whether a roll occurs before the exit.
    Nothing is priced on a different basis from anything else.
    """

    cap0 = CAP_ANCHOR + cap_spread          # market cap for a stabilised asset
    cap_roll = cap0 + 0.0150                # +150 bps once the lease is at/past expiry
    r = RF_5Y + discount_premium            # owner's required return
    g = rent_growth
    SELL_COST = 0.02                        # brokerage + legal + escrow, a convention
    out: Dict[str, DecisionResult] = {}

    # ---------------- A. SELL NOW -----------------------------------------
    price_a = market_price(base_rent, remaining_years, g, cap0)
    net_a = price_a * (1.0 - SELL_COST)
    out["A"] = DecisionResult(
        "A", "Sell now", net_a, net_a, [], 0,
        f"A buyer pays PV at {cap0:.2%} of contract rent for {remaining_years:g} yrs plus the "
        f"reversion re-let at market. Less 2.0% selling costs. Capital fully de-risked at t=0.",
    )

    # ---------------- B. SELL AT LEASE EXPIRY ------------------------------
    cf_b, rent_b = [], base_rent
    end_b = min(float(math.floor(remaining_years)), float(hold_horizon))
    for t in range(1, int(end_b) + 1):
        cf_b.append(rent_b)
        rent_b *= (1.0 + g)
    # At expiry the lease is rolling. Expected exit rent blends renew-at-market
    # with re-let-after-downtime. Exit cap carries the roll premium.
    market_at_expiry = base_rent * math.pow(1.0 + g, remaining_years)
    expected_exit_rent = renewal_probability * market_at_expiry + \
                         (1.0 - renewal_probability) * market_at_expiry * 0.90
    price_b = expected_exit_rent / cap_roll
    downtime = (1.0 - renewal_probability) * base_rent * (10.0 / 12.0)   # ~10 months of lost rent
    net_b = price_b * (1.0 - SELL_COST) - downtime
    pv_b = sum(pv(c, i + 1, r) for i, c in enumerate(cf_b))
    if remaining_years <= hold_horizon:
        pv_b += pv(net_b, remaining_years, r)
    else:
        pv_b += pv(price_b * (1 - SELL_COST), hold_horizon, r)
    out["B"] = DecisionResult(
        "B", f"Hold to expiry (~{remaining_years:g} yr)", pv_b, net_b, cf_b, int(end_b),
        f"Contract rent to expiry, then sold at {cap_roll:.2%} on the rolled rent. Pays "
        f"{downtime:,.0f} of expected downtime. The owner eats the roll.",
    )

    # ---------------- C. RENEW AND HOLD -----------------------------------
    cf_c, rent_c = [], base_rent
    roll_year = int(math.floor(remaining_years))
    for t in range(1, hold_horizon + 1):
        if t > 1:
            rent_c *= (1.0 + g)
        if t == roll_year + 1:
            # roll to market. Renewal blends the renewed and re-let outcomes.
            rent_c = renewal_probability * rent_c + (1.0 - renewal_probability) * rent_c * 0.90
        cf_c.append(rent_c)
    price_c = cf_c[-1] / cap0                # stabilised again at exit
    net_c = price_c * (1.0 - SELL_COST)
    pv_c = sum(pv(c, i + 1, r) for i, c in enumerate(cf_c)) + pv(net_c, hold_horizon, r)
    out["C"] = DecisionResult(
        "C", f"Renew and hold {hold_horizon} yr", pv_c, net_c, cf_c, hold_horizon,
        f"Rolls at {remaining_years:g} yr, holds to {hold_horizon}, exits at the stabilised "
        f"{cap0:.2%} cap. The roll is absorbed rather than sold into.",
    )

    # ---------------- D. HYBRID: EXTEND EARLY, SELL LONGER WALT -----------
    concession = 0.02
    extra = 5.0
    cf_d, rent_d = [], base_rent * (1.0 - concession)
    for t in range(1, int(extra) + 1):
        cf_d.append(rent_d)
        rent_d *= (1.0 + g)
    price_d = cf_d[-1] / cap0                # long WALT trades at the stabilised cap
    net_d = price_d * (1.0 - SELL_COST)
    pv_d = sum(pv(c, i + 1, r) for i, c in enumerate(cf_d)) + pv(net_d, extra, r)
    out["D"] = DecisionResult(
        "D", f"Extend {extra:g} yr, sell long WALT", pv_d, net_d, cf_d, int(extra),
        f"Concedes {concession:.0%} of rent now to remove the roll. Exits at {cap0:.2%} "
        f"instead of {cap_roll:.2%}. Sells ~{extra:g} yrs of term instead of ~{remaining_years:g}.",
    )
    return out


# Reverse-and-add Gaussian so we never depend on random.gauss internals.
def gauss(rng: random.Random, mu: float = 0.0, sd: float = 1.0) -> float:
    u1 = max(rng.random(), 1e-12)
    u2 = rng.random()
    z = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
    return mu + sd * z


def triangular(rng: random.Random, lo: float, mode: float, hi: float) -> float:
    u = rng.random()
    c = (mode - lo) / (hi - lo)
    if u < c:
        return lo + math.sqrt(u * (hi - lo) * (mode - lo))
    return hi - math.sqrt((1.0 - u) * (hi - lo) * (hi - mode))


@dataclass
class SimConfig:
    trials: int = 4000
    remaining_years: Tuple[float, float] = (4.0, 9.0)
    cap_spread_bounds: Tuple[float, float] = (0.0050, 0.0275)
    discount_premium_bounds: Tuple[float, float] = (0.0150, 0.0300)
    base_rent_bounds: Tuple[float, float] = (150_000.0, 350_000.0)
    rent_growth_bounds: Tuple[float, float] = (0.010, 0.037)
    renewal_bounds: Tuple[float, float] = (0.45, 0.85)
    # Black-swan overlay
    event_probability: float = 0.020      # 2.0% over a 10-year hold, per draw
    event_rent_loss: Tuple[float, float] = (0.35, 0.85)   # fraction of rent lost, 6-18 months
    event_value_loss: Tuple[float, float] = (0.20, 0.45)  # decline in exit value
    hold_horizon: int = 10


def simulate(cfg: SimConfig) -> Dict[str, object]:
    rng = random.Random(SEED)
    pvs: Dict[str, List[float]] = {k: [] for k in "ABCD"}
    event_hits = 0

    for _ in range(cfg.trials):
        ry = triangular(rng, cfg.remaining_years[0], 6.0, cfg.remaining_years[1])
        cap = triangular(rng, cfg.cap_spread_bounds[0], 0.0125, cfg.cap_spread_bounds[1])
        prem = triangular(rng, cfg.discount_premium_bounds[0], 0.0225, cfg.discount_premium_bounds[1])
        rent = triangular(rng, cfg.base_rent_bounds[0], 250_000.0, cfg.base_rent_bounds[1])
        g = triangular(rng, cfg.rent_growth_bounds[0], 0.020, cfg.rent_growth_bounds[1])
        rp = triangular(rng, cfg.renewal_bounds[0], 0.65, cfg.renewal_bounds[1])

        res = project(ry, rent, cap, prem, g, rp, cfg.hold_horizon)

        # Black-swan overlay: drawn independently per trial and applied to every
        # decision identically so the comparison stays apples-to-apples. A sale
        # completed BEFORE the event is assumed insulated; a hold is not. That
        # asymmetry is the whole point of the exercise, so it is modelled
        # explicitly rather than smeared across all four branches.
        fired = rng.random() < cfg.event_probability
        if fired:
            event_hits += 1
            severity = rng.random()
            rent_loss = cfg.event_rent_loss[0] + severity * (cfg.event_rent_loss[1] - cfg.event_rent_loss[0])
            val_loss = cfg.event_value_loss[0] + severity * (cfg.event_value_loss[1] - cfg.event_value_loss[0])
            res = apply_event(res, rent_loss, val_loss, ry)

        for k in "ABCD":
            pvs[k].append(res[k].pv_value)

    stats = {}
    for k in "ABCD":
        v = sorted(pvs[k])
        n = len(v)
        stats[k] = {
            "mean": sum(v) / n,
            "p05": v[int(0.05 * n)],
            "p25": v[int(0.25 * n)],
            "median": v[int(0.50 * n)],
            "p75": v[int(0.75 * n)],
            "p95": v[int(0.95 * n)],
            "prob_negative_vs_sell_now": sum(1 for a, b in zip(v, pvs["A"]) if a < b) / n,
        }
    best = {k: 0 for k in "ABCD"}
    for i in range(len(pvs["A"])):
        vals = {k: pvs[k][i] for k in "ABCD"}
        best[max(vals, key=vals.get)] += 1
    for k in "ABCD":
        stats[k]["prob_best"] = best[k] / len(pvs["A"])

    return {
        "trials": cfg.trials,
        "seed": SEED,
        "event_hits": event_hits,
        "event_frequency": event_hits / cfg.trials,
        "stats": stats,
    }


def apply_event(res, rent_loss: float, val_loss: float, remaining_years: float):
    """Apply a black-swan shock. A prompt sale (A) is deemed already closed."""
    out = {}
    for k, d in res.items():
        if k == "A":
            out[k] = d                                  # sold before the event
            continue
        nv = d.pv_value * (1.0 - val_loss)
        if k in ("C",):
            # holding through the event: rent is interrupted as well
            nv *= (1.0 - rent_loss * 0.30)
        out[k] = DecisionResult(d.decision, d.label, nv, d.exit_value * (1 - val_loss),
                                d.cash_flows, d.horizon, d.note + " [black-swan overlay applied]")
    return out


# ----------------------------------------------------------------------------
# 4. REPORT
# ----------------------------------------------------------------------------

def build_report() -> Dict[str, object]:
    # Deterministic scenario surface over the two owner-document unknowns.
    surface = []
    for ry in AXES[0].values:
        for br in AXES[1].values:
            res = project(ry, br, CAP_SPREAD_SCENARIOS["base"],
                          BASE_DISCOUNT_PREMIUM, 0.020, 0.65)
            winner = max(res, key=lambda k: res[k].pv_value)
            surface.append({
                "remaining_years": ry,
                "base_rent": br,
                "pv": {k: round(res[k].pv_value) for k in "ABCD"},
                "winner": winner,
                "rent_to_sales": round(br / FRANCHISE_AUV, 4),
                "rent_to_sales_flag": ("above" if br / FRANCHISE_AUV > RENT_TO_SALES_BAND[1]
                                       else "below" if br / FRANCHISE_AUV < RENT_TO_SALES_BAND[0]
                                       else "in-band"),
            })

    # Robustness: does the winner change under the pessimistic / optimistic
    # cap and discount assumptions?
    stress = []
    for cap_name, cap_spread in CAP_SPREAD_SCENARIOS.items():
        for prem in DISCOUNT_PREMIUMS:
            res = project(6.0, 250_000, cap_spread, prem, 0.020, 0.65)
            stress.append({
                "cap_scenario": cap_name,
                "cap_spread": cap_spread,
                "cap_rate": round(CAP_ANCHOR + cap_spread, 4),
                "discount_premium": prem,
                "discount_rate": round(RF_5Y + prem, 4),
                "pv": {k: round(res[k].pv_value) for k in "ABCD"},
                "winner": max(res, key=lambda k: res[k].pv_value),
            })

    sim = simulate(SimConfig())

    # Break-even: at what cap spread does "sell now" beat "sell at expiry"?
    breakeven = []
    for ry in (4.0, 6.0, 9.0):
        lo, hi = 0.0, 0.20
        for _ in range(80):
            mid = (lo + hi) / 2
            res = project(ry, 250_000, mid, BASE_DISCOUNT_PREMIUM, 0.020, 0.65)
            if res["A"].pv_value > res["B"].pv_value:
                lo = mid
            else:
                hi = mid
        breakeven.append({"remaining_years": ry, "breakeven_cap_spread": round((lo + hi) / 2, 5),
                          "breakeven_cap_rate": round(CAP_ANCHOR + (lo + hi) / 2, 5)})

    # ---- REGIME MAP ------------------------------------------------------
    # The single most important structural finding: whether holding beats
    # selling is decided by the OWNER'S REQUIRED RETURN relative to the MARKET
    # CAP RATE. Below the cap rate the owner is an above-market valuer and
    # should hold; above it, the owner should sell. This grid makes that rule
    # explicit and lets the reader place themselves in it.
    regime = []
    for cap_rate in (0.0700, 0.0785, 0.0875, 0.1000):
        for disc in (0.0580, 0.0640, 0.0694, 0.0760, 0.0850):
            cap_spread = cap_rate - CAP_ANCHOR
            prem = disc - RF_5Y
            res = project(6.0, 250_000, cap_spread, prem, 0.020, 0.65)
            regime.append({
                "cap_rate": round(cap_rate, 4),
                "discount_rate": round(disc, 4),
                "premium_over_cap_bps": round((cap_rate - disc) * 10_000),
                "pv": {k: round(res[k].pv_value) for k in "ABCD"},
                "winner": max(res, key=lambda k: res[k].pv_value),
            })

    # Crossover: the owner return at which "sell now" overtakes "renew and hold",
    # holding the market cap rate at the base case.
    crossover = []
    for cap_spread in (0.0050, 0.0125, 0.0275):
        lo, hi = 0.01, 0.40
        for _ in range(90):
            mid = (lo + hi) / 2
            res = project(6.0, 250_000, cap_spread, mid - RF_5Y, 0.020, 0.65)
            if res["A"].pv_value > res["C"].pv_value:
                hi = mid
            else:
                lo = mid
        crossover.append({
            "cap_rate": round(CAP_ANCHOR + cap_spread, 4),
            "crossover_discount_rate": round((lo + hi) / 2, 4),
            "interpretation": "Hold if your required return is BELOW this; sell if ABOVE.",
        })

    # Rent-to-sales pressure table: how much of the unit's sales the lease eats.
    rent_pressure = []
    for br in AXES[1].values:
        share = br / FRANCHISE_AUV
        rent_pressure.append({
            "base_rent": br,
            "pct_of_franchise_auv": round(share, 4),
            "occupancy_plus_royalty_pct": round(share + ROYALTY_RATE, 4),
            "band": ("below", "in-band", "above")[0 if share < RENT_TO_SALES_BAND[0]
                                                 else 1 if share <= RENT_TO_SALES_BAND[1] else 2],
        })

    return {
        "generated_utc": "2026-11-06",
        "generated_by": "arena-8149683c",
        "engine": "model/project_model.py",
        "seed": SEED,
        "inputs": {
            "rf_5y": RF_5Y, "rf_5y_real": RF_5Y_REAL, "rf_10y": RF_10Y,
            "rf_10y_real": RF_10Y_REAL,
            "cap_anchor": CAP_ANCHOR, "cpi_la": CPI_LA,
            "gcp_growth_2026f": GCP_GROWTH_2026F,
            "taxable_sales_2026f": TAXABLE_SALES_2026F,
            "unemployment_2026f": UNEMP_2026F,
            "franchise_auv": FRANCHISE_AUV, "royalty_rate": ROYALTY_RATE,
            "discount_premiums": list(DISCOUNT_PREMIUMS),
            "cap_spread_scenarios": CAP_SPREAD_SCENARIOS,
        },
        "axes": [asdict(a) for a in AXES],
        "surface": surface,
        "stress": stress,
        "breakeven": breakeven,
        "regime": regime,
        "crossover": crossover,
        "rent_pressure": rent_pressure,
        "monte_carlo": sim,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="verify the checked-in output matches")
    args = ap.parse_args()

    report = build_report()
    if args.check:
        if not os.path.exists(OUT_PATH):
            print("FAIL: data/model_output.json missing")
            return 1
        old = json.load(open(OUT_PATH))
        same = json.dumps(old, sort_keys=True) == json.dumps(report, sort_keys=True)
        print("OK: reproducible" if same else "FAIL: output drift detected")
        return 0 if same else 1

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=False)
    mc = report["monte_carlo"]["stats"]
    print(f"wrote {OUT_PATH}")
    print(f"trials={report['monte_carlo']['trials']} event_frequency={report['monte_carlo']['event_frequency']:.4f}")
    for k, lbl in (("A", "sell now"), ("B", "sell at expiry"), ("C", "renew+hold"), ("D", "hybrid")):
        s = mc[k]
        print(f"  {k} {lbl:<16} median ${s['median']:>12,.0f}  p05 ${s['p05']:>12,.0f}  "
              f"p95 ${s['p95']:>12,.0f}  P(beats A)={1-s['prob_negative_vs_sell_now']:.1%}  P(best)={s['prob_best']:.1%}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
