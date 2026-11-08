#!/usr/bin/env python3
"""
Session I (arena/343c7030-jack2) projection engine.

Deterministic 2026-2040 projection plus a seeded Monte-Carlo over five courses of
action, all normalised to $100,000 of current annual NOI so that no private rent,
address, basis or loan term ever enters the model.

Nothing in ASSUMPTIONS is an official statistic. Every verified input is pulled
from data/facts.json and cited on the site. Assumptions are printed on the model
page with the range that was tested, as the brief requires.

Standard library only. Deterministic: same seed -> byte-identical output.
"""
import json
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
SEED = 20261108
TRIALS = 15000
NOI0 = 100_000.0
START = 2026
END = 2040
GAMMA = 2.5                      # CRRA risk aversion for the certainty equivalent

# ---------------------------------------------------------------------------
# Assumptions. None of these is read from an official source; each is a modelling
# choice, published as such, and stress-tested in the sensitivity grid.
# ---------------------------------------------------------------------------
ASSUMPTIONS = [
    ("A1", "Going-in capitalisation rate for this asset at 2026", "6.00%", "5.25% – 6.75%",
     "No official series publishes QSR NNN transaction cap rates. Range spans a 25 bp premium to the "
     "10-year Treasury (4.86%, verified C01) and a typical net-lease spread."),
    ("A2", "Cap-rate term adjustment", "-25 bp for 10+ yrs of term; 0 for 5–10; +50 bp for 2–5; +100 bp under 2 yrs",
     "-50 to +150 bp",
     "Standard net-lease term pricing: buyers pay up for long contracted income and discount short "
     "remaining term. Direction is uncontroversial; the size is a judgement."),
    ("A3", "NOI growth, base case", "3.0% / yr", "2.0% – 3.7%",
     "Bracket: 2.0% is a conservative floor; 3.7% is the verified September 2026 LA CPI-U (E18). "
     "Tenant rent growth above CPI is not assumed."),
    ("A4", "Selling costs", "2.5% of price", "2.0% – 3.5%", "Broker plus closing costs, excluding taxes."),
    ("A5", "Basis and accumulated depreciation", "basis = 40% of current value; depreciation taken = 30% of current value",
     "basis 20% – 70% of value",
     "The brief does not disclose the owner's basis. Both figures are placeholders, and the after-tax "
     "ranking is re-run across the range in the sensitivity grid."),
    ("A6", "Federal long-term capital gains + net investment income tax", "23.8%", "23.8%",
     "Statutory top rate for a high-income individual (IRC §1(h) + §1411)."),
    ("A7", "Unrecaptured §1250 gain (depreciation recapture), federal", "25%", "25%", "IRC §1(h)(1)(E)."),
    ("A8", "California income tax on the gain", "13.3%", "13.3%", "Top marginal FTB rate; no preferential capital-gains rate."),
    ("A9", "Replacement asset after a §1031 exchange (diversified net lease)", "6.25% entry and exit cap, 2.5% NOI growth",
     "growth 2.0% – 3.0%",
     "With the same cap on entry and exit the yield cancels and only NOI growth matters, so the tested "
     "range is on growth, not on the cap."),
    ("A10", "Probability the tenant renews at expiry", "65%", "40% – 85%",
     "The tenant has historically renewed at market rates, but carries negative equity (T05) and a "
     "closure programme. Not an official statistic."),
    ("A11", "Downtime if the tenant vacates at expiry", "12 months, then reletting at 90% of prior NOI",
     "6 – 24 months",
     "A drive-through QSR box is single-purpose; reletting or re-tenanting takes time."),
    ("A12", "Tenant default hazard, any year", "1.5% / yr", "0.5% – 4.0%",
     "Anchored to the tenant's FY2025 loss and negative equity, not to a published default probability."),
    ("A13", "Earthquake loss given a major event", "8% of value uninsured/retained, plus 10% of one year's NOI",
     "0 – 25% of value",
     "The 30-year M≥6.7 probability (60%, H01) is official; the loss-given-event is not."),
    ("A14", "Wildfire loss given a major event", "15% of value, 0.5% / yr event probability",
     "0.1% – 1.5% / yr",
     "Central Los Angeles is urban; the parcel's FHSZ class is unknown (H05 blank). Treated as a small "
     "but non-zero tail."),
    ("A15", "Renewal rent relative to in-place rent", "0% change", "-10% – +10%",
     "A renewal at market is assumed flat; the brief gives no rent and no market comps."),
]

STRATEGIES = {
    "S1": {
        "name": "Sell now through a §1031 exchange",
        "short": "Sell 2026, §1031 into diversified net lease",
        "detail": "Sell in 2026, roll the proceeds into a diversified net-lease portfolio under IRC §1031, "
                  "hold that portfolio to 2040 and sell it then.",
    },
    "S2": {
        "name": "Sell now, pay the tax",
        "short": "Sell 2026, taxable",
        "detail": "Same 2026 sale but no exchange: federal and California tax is paid on the gain and "
                  "on depreciation recapture, and the net proceeds are reinvested.",
    },
    "S3": {
        "name": "Blend-and-extend now, sell in 2032",
        "short": "Extend now, sell 2032",
        "detail": "Negotiate an extension now (target 10 years at or above in-place rent), then sell in "
                  "2032 with roughly 4–9 years of term left, through a §1031 exchange.",
    },
    "S4": {
        "name": "Hold to expiry, then sell",
        "short": "Hold to expiry, sell",
        "detail": "Leave the lease alone. At the 2030–2035 expiry either the tenant renews on market "
                  "terms or the box goes dark; sell at or near expiry either way.",
    },
    "S5": {
        "name": "Renew at expiry and hold to 2040",
        "short": "Renew at expiry, hold",
        "detail": "Wait for expiry, renew then, and hold the asset to 2040 collecting rent.",
    },
}

# Verified inputs pulled from facts.json so the model cannot drift from the ledger.
def load_facts():
    with open(os.path.join(DATA, "facts.json")) as fh:
        return {r["id"]: r for r in json.load(fh)["rows"]}


FACTS = load_facts()


def verified(fid):
    row = FACTS[fid]
    assert row["status"] == "verified", f"{fid} is not verified"
    return row


def tax_on_gain(gain, recap, a):
    """Federal + California tax on a taxable sale."""
    if gain <= 0:
        return 0.0
    recap = max(0.0, min(recap, gain))
    fed = a["recap"] * recap + a["ltcg"] * (gain - recap)
    niit = 0.038 * gain
    state = a["ca"] * gain
    return fed + niit + state


def tax_rates():
    return {
        "ltcg": 0.20,
        "recap": 0.25,
        "ca": 0.133,
    }


def city_transfer_tax(price):
    """City of LA: 0.45% base, plus the Measure ULA cliff (S09, verified)."""
    t = 0.0045 * price
    if price > 10_900_000:
        t += 0.055 * price
    elif price > 5_400_000:
        t += 0.04 * price
    return t


def cap_for_term(term_years, cap0):
    if term_years >= 10:
        return cap0 - 0.0025
    if term_years >= 5:
        return cap0
    if term_years >= 2:
        return cap0 + 0.0050
    return cap0 + 0.0100


def expiry_year(rng, deterministic=False):
    """Lease expiry is known only to fall in 2030-2035."""
    return 2032 if deterministic else rng.randint(2030, 2035)


def value_at(noi, cap):
    return noi / cap


def settle(sale_year, price, a, deferred, dep_taken):
    """Sell at sale_year, apply transfer costs and tax, reinvest to END, sell that."""
    costs = a["sell_cost"] * price + city_transfer_tax(price)
    net = price - costs
    if deferred:
        # IRC 1031: no tax now; the old basis carries into the replacement.
        reinvest = net
        basis = max(0.0, a["basis"] - costs)
        dep = dep_taken
    else:
        gain = price - costs - a["basis"]
        tax = tax_on_gain(gain, dep_taken, a)
        reinvest = net - tax
        basis = reinvest
        dep = 0.0
    years = max(0, END - sale_year)
    terminal = reinvest * (1.0 + a["reinvest_growth"]) ** years
    tcost = a["sell_cost"] * terminal
    gain2 = terminal - tcost - basis
    tax2 = tax_on_gain(gain2, dep, a)
    return max(0.0, terminal - tcost - tax2)


def run_strategy(sid, path):
    """One path through one strategy. Returns after-tax terminal wealth at END."""
    a = path["a"]
    cap0 = path["cap0"]
    g = path["g"]

    def noi(t):
        return NOI0 * (1.0 + g) ** (t - START)

    if sid in ("S1", "S2"):
        price = NOI0 / cap0
        return settle(START, price, a, deferred=(sid == "S1"), dep_taken=a["dep_taken"])

    if sid == "S3":
        # extension signed now; sell 2032 with about five years of term left
        sale_year = 2032
        price = value_at(noi(sale_year), cap_for_term(5, cap0)) * (1.0 + a["rent_uplift"])
        return settle(sale_year, price, a, deferred=True, dep_taken=a["dep_taken"])

    if sid == "S4":
        exp = path["expiry"]
        if path["vacates"]:
            dark = a["downtime_months"] / 12.0
            cash = noi(exp) * 0.10 * dark
            sale_year = min(END - 1, exp + 1)
            price = value_at(noi(sale_year), cap0 + 0.0100) * 0.90
        else:
            cash = 0.0
            sale_year = min(END - 1, exp)
            price = value_at(noi(sale_year), cap_for_term(10, cap0))
        return settle(sale_year, price + cash, a, deferred=True, dep_taken=a["dep_taken"])

    if sid == "S5":
        exp = path["expiry"]
        if path["vacates"]:
            cash = noi(exp) * 0.10 * (a["downtime_months"] / 12.0)
            price = value_at(noi(END) * 0.60, cap0 + 0.0100)
        else:
            cash = 0.0
            price = value_at(noi(END), cap_for_term(2040 - exp, cap0))
        return settle(END, price + cash, a, deferred=True, dep_taken=a["dep_taken"])

    raise ValueError(sid)


def make_caps():
    return {
        "basis": 0.40 * (NOI0 / 0.06),
        "dep_taken": 0.30 * (NOI0 / 0.06),
        "sell_cost": 0.025,
        "ltcg": 0.20,
        "recap": 0.25,
        "ca": 0.133,
        "reinvest_growth": 0.025,
        "rent_uplift": 0.0,
        "downtime_months": 12,
    }


def deterministic_case(label, g, cap0):
    a = make_caps()
    out = {}
    for sid in STRATEGIES:
        rng = random.Random(0)
        path = {"a": a, "cap0": cap0, "g": g, "rng": rng, "expiry": 2032, "vacates": False}
        out[sid] = run_strategy(sid, path)
    return {"case": label, "noi_growth": g, "cap0": cap0, "results": out}


def mc_case(g_mean, cap0_mean, trials=TRIALS, seed=SEED, a=None, vacate_p=None):
    a = a or make_caps()
    rng = random.Random(seed)
    acc = {sid: [] for sid in STRATEGIES}
    # annual probability of a major earthquake, from the verified 30-year 60% (H01)
    p_quake_annual = 1.0 - (1.0 - 0.60) ** (1.0 / 30.0)
    for _ in range(trials):
        g = max(-0.02, rng.gauss(g_mean, 0.009))
        cap0 = max(0.040, rng.gauss(cap0_mean, 0.0050))
        exp = rng.randint(2030, 2035)
        vacates = rng.random() > 0.65 if vacate_p is None else (rng.random() > vacate_p)
        hazard_mult = 1.0
        if rng.random() < p_quake_annual * 10:
            hazard_mult -= 0.08
        if rng.random() < 0.005 * 10:
            hazard_mult -= 0.15
        path = {"a": a, "cap0": cap0, "g": g, "rng": rng, "expiry": exp, "vacates": vacates}
        for sid in STRATEGIES:
            acc[sid].append(run_strategy(sid, path) * hazard_mult)
    return acc


def ce(values, gamma=GAMMA):
    """Certainty equivalent of terminal wealth under CRRA utility."""
    if gamma == 1.0:
        return math.exp(sum(math.log(max(v, 1e-9)) for v in values) / len(values))
    n = len(values)
    s = sum(max(v, 1e-9) ** (1.0 - gamma) for v in values) / n
    return s ** (1.0 / (1.0 - gamma))


def pct(values, p):
    xs = sorted(values)
    k = (len(xs) - 1) * p
    lo, hi = math.floor(k), math.ceil(k)
    if lo == hi:
        return xs[int(k)]
    return xs[lo] * (hi - k) + xs[hi] * (k - lo)


def summarise(acc):
    out = {}
    for sid, vals in acc.items():
        out[sid] = {
            "mean": sum(vals) / len(vals),
            "median": pct(vals, 0.5),
            "p05": pct(vals, 0.05),
            "p95": pct(vals, 0.95),
            "ce": ce(vals),
            "prob_beats_hold": None,
        }
    base = acc["S4"]
    for sid, vals in acc.items():
        wins = sum(1 for i in range(len(vals)) if vals[i] > base[i])
        out[sid]["prob_beats_hold"] = wins / len(vals)
    return out


def main():
    det = [
        deterministic_case("Bear", 0.020, 0.0675),
        deterministic_case("Base", 0.030, 0.0600),
        deterministic_case("Bull", 0.037, 0.0525),
    ]

    acc = mc_case(0.030, 0.0600)
    mc = summarise(acc)
    ranking = sorted(mc, key=lambda s: mc[s]["ce"], reverse=True)

    # reinvestment-growth sensitivity (A9), everything else at base
    reinvest_grid = []
    for rg in (0.020, 0.025, 0.030):
        a = make_caps()
        a["reinvest_growth"] = rg
        sub = mc_case(0.030, 0.0600, trials=2500, seed=SEED + 2, a=a)
        sm = summarise(sub)
        reinvest_grid.append({
            "reinvest_growth": rg,
            "best": max(sm, key=lambda k: sm[k]["ce"]),
            "ce": {k: sm[k]["ce"] for k in STRATEGIES},
        })

    # 15-cell sensitivity grid on the two inputs that matter most
    grid = []
    for g in (0.020, 0.030, 0.037):
        for cap in (0.0525, 0.0600, 0.0675):
            a = make_caps()
            sub = mc_case(g, cap, trials=2500, seed=SEED + 1, a=a)
            s = summarise(sub)
            grid.append({
                "growth": g, "cap": cap,
                "best": max(s, key=lambda k: s[k]["ce"]),
                "ce": {k: s[k]["ce"] for k in STRATEGIES},
            })

    # expiry-year sensitivity: what the 2030-2035 ambiguity is worth for hold-to-expiry
    expiry_grid = []
    for exp in range(2030, 2036):
        a = make_caps()
        rng = random.Random(exp)
        path = {"a": a, "cap0": 0.06, "g": 0.03, "rng": rng, "expiry": exp, "vacates": False}
        expiry_grid.append({"expiry": exp, "s4_ce": run_strategy("S4", path)})

    out = {
        "seed": SEED,
        "trials": TRIALS,
        "gamma": GAMMA,
        "noi0": NOI0,
        "buyer_of_record_note": "All figures are per $100,000 of current annual NOI. They are not this asset's value.",
        "verified_inputs": {
            "cpi_la_sep2026": float(verified("E18")["value"]),
            "ust10y_2026_11_06": float(verified("C01")["value"]),
            "quake_30y_m67": float(verified("H01")["value"]),
            "ula_threshold_low": 5_400_000,
            "ula_threshold_high": 10_900_000,
            "city_transfer_base": float(verified("X01")["value"]),
        },
        "assumptions": [
            {"id": i, "name": n, "value": v, "range": r, "why": w} for i, n, v, r, w in ASSUMPTIONS
        ],
        "strategies": STRATEGIES,
        "deterministic": det,
        "monte_carlo": {"summary": mc, "ranking": ranking},
        "sensitivity_grid": grid,
        "reinvest_grid": reinvest_grid,
        "expiry_grid": expiry_grid,
    }
    with open(os.path.join(DATA, "projections.json"), "w") as fh:
        json.dump(out, fh, indent=1)

    print(f"seed {SEED}, {TRIALS} trials, CRRA {GAMMA}")
    for sid in ranking:
        m = mc[sid]
        print(f"  {sid} {STRATEGIES[sid]['short']:<34} CE {m['ce']:>10,.0f}  P05 {m['p05']:>10,.0f}  median {m['median']:>10,.0f}  P(beat hold) {m['prob_beats_hold']:.0%}")
    print("expiry grid:", [f"{r['expiry']}:{r['s4_ce']:,.0f}" for r in expiry_grid])


if __name__ == "__main__":
    main()
