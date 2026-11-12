#!/usr/bin/env python3
"""Projection model for the sell-or-renew decision (session-1c30f8e8, final integration).

WHAT IT IS
    A transparent scenario engine, not a forecast and not an appraisal. The property's rent,
    exact expiry, lease terms, value and tax basis are unknown to this workbook, so every money
    amount is expressed per $100 of CURRENT yearly net rent and every strategy is run for each
    possible expiry year, 2030 to 2035.

WHERE THE NUMBERS COME FROM
    canonical/data/assumptions.json. Each setting is an ANCHOR (copied from a verified ledger
    row and checked against it here) or an ASSUMPTION (set by the analyst, labelled as such on
    the site). Nothing here is presented as a verified fact about the property.

TWO ENGINES, SAME RULES
    expected()  - closed-form expected value with no market noise and no disasters. Used for
                  breakevens and sensitivities, and to test the simulation.
    simulate()  - seeded Monte Carlo that adds yield movements, tenant failure and regional
                  disasters, and reports the spread of outcomes (the tail, not only the mean).

Standard library only. Deterministic: the same inputs always give the same output file.
"""
import json
import os
import random
import re
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(DATA, "model_output.json")

STRATEGIES = [
    ("sell_cash", "Sell now and hold the proceeds in Treasuries", "sell"),
    ("sell_exchange", "Sell now and exchange into a longer lease elsewhere", "sell"),
    ("extend_then_sell", "Ask for an early extension, then sell and exchange either way", "sell"),
    ("test_then_decide", "Ask for an early extension: keep the property if the tenant agrees, sell and exchange if it refuses", "sequence"),
    ("extend_and_hold", "Ask for an early extension and keep the property either way", "renew"),
    ("do_nothing", "Do nothing: hold to expiry and see whether the tenant renews", "renew"),
]


# --------------------------------------------------------------------------- inputs
def _num(text):
    m = re.search(r"-?\d[\d,]*(?:\.\d+)?", text)
    return float(m.group(0).replace(",", ""))


def load_rows():
    rows = {}
    facts = os.path.join(DATA, "facts")
    for name in sorted(os.listdir(facts)):
        if name.endswith(".json"):
            with open(os.path.join(facts, name), encoding="utf-8") as fh:
                for r in json.load(fh)["rows"]:
                    rows[r["id"]] = r
    return rows


def load_assumptions():
    with open(os.path.join(DATA, "assumptions.json"), encoding="utf-8") as fh:
        return json.load(fh)


def check_anchors(doc, rows):
    """Every anchor must equal the number published in its ledger row."""
    problems = []
    for key, s in doc["settings"].items():
        if s["kind"] != "anchor":
            continue
        row = rows.get(s["row"])
        if row is None or row["status"] not in ("verified", "computed"):
            problems.append(f"{key}: ledger row {s['row']} is missing or not verified")
        elif abs(_num(row["value"]) - float(s["value"])) > 1e-9:
            problems.append(f"{key}: assumptions.json says {s['value']} but {s['row']} says {row['value']}")
    return problems


def base_settings(doc, **overrides):
    s = {k: float(v["value"]) for k, v in doc["settings"].items()}
    s.update(overrides)
    return s


# --------------------------------------------------------------------------- building blocks
def premium(remaining_years, s):
    """Extra yield (points) for a lease with fewer than 10 years left; zero at 10 or more."""
    missing = max(0.0, 10.0 - max(0.0, remaining_years))
    return s["short_premium"] * missing / 10.0


def leased_value(rent, cap_points, remaining_years, s):
    return rent / ((cap_points + premium(remaining_years, s)) / 100.0)


def vacant_value(last_rent, cap_points, s):
    return s["vacant_value"] / 100.0 * last_rent / (cap_points / 100.0)


def grow(amount, years, s):
    """Carry a cash amount forward at the reinvestment rate."""
    return amount * (1.0 + s["reinvest_rate"] / 100.0) ** years


def net_sale(gross, s):
    return gross * (1.0 - s["sell_cost"] / 100.0)


class Path:
    """Everything random in one trial. The closed-form engine uses a 'calm' path."""

    def __init__(self, horizon, cap_nat, bump, credit, repl_credit, regional, damage,
                 lease_ends_on_damage, u_keen, u_expiry, u_relet, u_repl_renew, u_repl_relet):
        self.H = horizon
        self.cap_nat = cap_nat            # national buyer yield, points, by year
        self.bump = bump                  # extra local yield after a regional disaster
        self.credit = credit              # set of years the current tenant would fail
        self.repl_credit = repl_credit    # set of years the replacement tenant would fail
        self.regional = regional          # set of years with a regional disaster
        self.damage = damage              # subset of those years that damage this building
        self.lease_ends_on_damage = lease_ends_on_damage
        self.u_keen = u_keen              # tenant's keenness today (answers an extension request)
        self.u_expiry = u_expiry          # tenant's keenness at expiry (same, unless intentions changed)
        self.u_relet, self.u_repl_renew, self.u_repl_relet = u_relet, u_repl_renew, u_repl_relet

    def cap_local(self, t):
        return self.cap_nat[t] + self.bump[t]


def calm_path(s, horizon, u_keen, u_expiry, relet):
    n = horizon + 1
    return Path(horizon, [s["cap_long"]] * n, [0.0] * n, set(), set(), set(), set(), False,
                u_keen, u_expiry, 0.0 if relet else 1.0, 0.0, 0.0)


def random_path(s, horizon, rng):
    n = horizon + 1
    cap = [s["cap_long"]]
    bump = [0.0]
    regional, damage = set(), set()
    for t in range(1, n):
        prev = cap[-1]
        step = s["cap_revert"] * (s["cap_long"] - prev) + rng.gauss(0.0, s["cap_sigma"])
        cap.append(min(14.0, max(3.5, prev + step)))
        b = bump[-1] * (1.0 - s["cap_revert"])
        if rng.random() < s["p_regional_event"] / 100.0:
            regional.add(t)
            b += s["regional_cap_bump"]
            if rng.random() < s["p_site_damage"] / 100.0:
                damage.add(t)
        bump.append(b)
    credit = {t for t in range(1, n) if rng.random() < s["p_credit"] / 100.0}
    repl_credit = {t for t in range(1, n) if rng.random() < s["repl_p_credit"] / 100.0}
    u_keen = rng.random()
    changed = rng.random() < s["intent_change"] / 100.0
    u_new = rng.random()
    return Path(horizon, cap, bump, credit, repl_credit, regional, damage,
                rng.random() < s["p_lease_ends_on_damage"] / 100.0,
                u_keen, u_new if changed else u_keen, rng.random(), rng.random(), rng.random())


def run_property(s, path, rent, lease_end, p_renew, local=True, start=0, rent_growth=0.0,
                 cap_spread=0.0, credit_years=None, u_relet=None, u_renew=None):
    """Wealth at the horizon from owning one net-leased property from year `start`.

    Cash arrives at the end of each year and is carried forward at the reinvestment rate.
    At the horizon whatever is still owned is converted to cash at its sale value, net of
    selling cost, so that every strategy is compared in the same currency.
    """
    H = path.H
    credit_years = path.credit if credit_years is None else credit_years
    u_relet = path.u_relet if u_relet is None else u_relet
    u_renew = path.u_expiry if u_renew is None else u_renew
    cap = (lambda t: path.cap_local(t) + cap_spread) if local else (lambda t: path.cap_nat[t] + cap_spread)
    wealth = 0.0
    leased, owned = True, True
    last_rent = rent
    vacant_since = None
    skip_rent_year = None
    for t in range(start + 1, H + 1):
        if not owned:
            break
        if leased:
            if t != skip_rent_year:
                wealth += grow(rent, H - t, s)
            last_rent = rent
            if local and t in path.damage:
                wealth -= grow(s["damage_loss"] / 100.0 * leased_value(rent, cap(t), lease_end - t, s), H - t, s)
                skip_rent_year = t + 1
                if path.lease_ends_on_damage:
                    leased, vacant_since = False, t
                    continue
            if t in credit_years:
                leased, vacant_since = False, t
                continue
            if t >= lease_end and t < H:
                chance = p_renew
                if local and ((t in path.regional) or (t - 1 in path.regional)):
                    chance *= s["regional_renew_hit"] / 100.0
                if u_renew < chance / 100.0:
                    rent = rent * s["renew_rent"] / 100.0
                    lease_end = t + s["renew_term"]
                else:
                    leased, vacant_since = False, t
                continue
            rent *= 1.0 + rent_growth / 100.0
        else:
            wealth -= grow(s["vacant_carry"] / 100.0 * last_rent, H - t, s)
            if local and t in path.damage:
                wealth -= grow(s["damage_loss"] / 100.0 * vacant_value(last_rent, cap(t), s), H - t, s)
            if t - vacant_since >= s["vacant_years"] and t < H:
                if u_relet < s["p_relet"] / 100.0:
                    rent = last_rent * s["relet_rent"] / 100.0
                    wealth -= grow(s["relet_cost"] / 100.0 * rent, H - t, s)
                    lease_end = t + s["relet_term"]
                    leased = True
                else:
                    wealth += grow(net_sale(vacant_value(last_rent, cap(t), s), s), H - t, s)
                    owned = False
    if owned:
        if leased:
            wealth += net_sale(leased_value(rent, cap(H), s["terminal_years_left"], s), s)
        else:
            wealth += net_sale(vacant_value(last_rent, cap(H), s), s)
    return wealth


def run_exchange(s, path, net_proceeds):
    """Proceeds of a sale today, exchanged into a longer lease outside the hazard region."""
    invested = net_proceeds * (1.0 - s["buy_cost"] / 100.0)
    rent = invested * s["repl_cap"] / 100.0
    return run_property(s, path, rent, s["repl_term"], s["p_renew"], local=False,
                        rent_growth=s["repl_growth"], cap_spread=s["repl_cap"] - s["cap_long"],
                        credit_years=path.repl_credit, u_relet=path.u_repl_relet, u_renew=path.u_repl_renew)


def strategies_on_path(s, path, expiry_index):
    """Wealth at the horizon for each of the six strategies on one path."""
    H = path.H
    as_is = net_sale(leased_value(100.0, s["cap_long"], expiry_index, s), s)
    ext_rent = 100.0 * s["extend_rent"] / 100.0
    extended = net_sale(leased_value(ext_rent, s["cap_long"], s["extend_term"], s), s)
    # One "keenness" draw answers an extension request today. The same draw decides renewal at
    # expiry unless the tenant's intentions change in between (setting 'intent_change'), so a
    # refusal today is information, and a signed extension is protection against a change.
    agreed = path.u_keen < s["p_extend_now"] / 100.0
    out = {}
    out["sell_cash"] = grow(as_is * (1.0 - s["tax_drag"] / 100.0), H, s)
    out["sell_exchange"] = run_exchange(s, path, as_is)
    out["extend_then_sell"] = run_exchange(s, path, extended if agreed else as_is)
    keep_extended = run_property(s, path, ext_rent, s["extend_term"], s["p_renew"], rent_growth=s["rent_growth"])
    keep_refused = run_property(s, path, 100.0, expiry_index, s["p_renew"], rent_growth=s["rent_growth"])
    out["test_then_decide"] = keep_extended if agreed else out["sell_exchange"]
    out["extend_and_hold"] = keep_extended if agreed else keep_refused
    out["do_nothing"] = run_property(s, path, 100.0, expiry_index, s["p_renew"], rent_growth=s["rent_growth"])
    out["_agreed"] = agreed
    return out


# --------------------------------------------------------------------------- engine 1: expected value
def expected(s, expiry_year, start_year=2026, horizon_year=2040):
    """Probability-weighted outcome with no market noise, no tenant failure and no disaster.

    The uncertainties left are the tenant's keenness today, whether its intentions change
    before expiry, and whether an empty building is re-let or sold. All are integrated exactly.
    """
    H = horizon_year - start_year
    e = expiry_year - start_year
    p_ren = min(1.0, max(0.0, s["p_renew"] / 100.0))
    p_ext = min(1.0, max(0.0, s["p_extend_now"] / 100.0))
    change = min(1.0, max(0.0, s["intent_change"] / 100.0))
    cuts = sorted({0.0, 1.0, p_ext, p_ren})
    total = {k: 0.0 for k, _, _ in STRATEGIES}
    for lo, hi in zip(cuts, cuts[1:]):
        if hi <= lo:
            continue
        keen = (lo + hi) / 2.0
        # (weight, keenness at expiry): unchanged, or changed and then renewing / not renewing
        branches = [(1.0 - change, keen), (change * p_ren, 0.0), (change * (1.0 - p_ren), 1.0)]
        for weight, at_expiry in branches:
            if weight <= 0.0:
                continue
            for relet, p_relet in ((True, s["p_relet"] / 100.0), (False, 1.0 - s["p_relet"] / 100.0)):
                path = calm_path(s, H, keen, at_expiry, relet)
                for key, value in strategies_on_path(s, path, e).items():
                    if key in total:
                        total[key] += (hi - lo) * weight * p_relet * value
    return total


def breakeven(s, expiry_year, setting, lo, hi, a="do_nothing", b="sell_exchange", steps=60):
    """Value of `setting` at which strategies a and b have the same expected outcome."""
    def gap(x):
        t = dict(s)
        t[setting] = x
        ev = expected(t, expiry_year)
        return ev[a] - ev[b]
    g_lo, g_hi = gap(lo), gap(hi)
    if g_lo == 0:
        return lo
    if g_lo * g_hi > 0:
        return None
    for _ in range(steps):
        mid = (lo + hi) / 2.0
        g_mid = gap(mid)
        if g_lo * g_mid <= 0:
            hi = mid
        else:
            lo, g_lo = mid, g_mid
    return (lo + hi) / 2.0


def sell_later_curve(s, expiry_year, start_year=2026, horizon_year=2040):
    """Outcome of holding s more years and then selling for cash, with nothing going wrong."""
    H = horizon_year - start_year
    e = expiry_year - start_year
    out = []
    for wait in range(0, e + 1):
        rent, wealth = 100.0, 0.0
        for t in range(1, wait + 1):
            wealth += grow(rent, H - t, s)
            rent *= 1.0 + s["rent_growth"] / 100.0
        price = leased_value(rent, s["cap_long"], e - wait, s)
        wealth += grow(net_sale(price, s), H - wait, s)
        out.append({"sell_year": start_year + wait, "years_left_on_lease": e - wait,
                    "sale_price": round(price, 1), "wealth_2040": round(wealth, 1)})
    return out


# --------------------------------------------------------------------------- engine 2: simulation
def pct(sorted_values, q):
    if not sorted_values:
        return None
    k = (len(sorted_values) - 1) * q
    f = int(k)
    c = min(f + 1, len(sorted_values) - 1)
    return sorted_values[f] + (sorted_values[c] - sorted_values[f]) * (k - f)


def simulate(s, expiry_year, trials, seed, start_year=2026, horizon_year=2040):
    H = horizon_year - start_year
    e = expiry_year - start_year
    rng = random.Random(seed * 1000 + expiry_year)
    results = {k: [] for k, _, _ in STRATEGIES}
    results["_agreed"] = []
    for _ in range(int(trials)):
        path = random_path(s, H, rng)
        for k, v in strategies_on_path(s, path, e).items():
            results[k].append(v)
    return results


def summarise(results, weight):
    cash = results["sell_cash"]
    out = {}
    for key, values in results.items():
        if key.startswith("_"):
            continue
        v = sorted(values)
        p5, med = pct(v, 0.05), pct(v, 0.50)
        tail = v[: max(1, len(v) // 20)]
        out[key] = {
            "mean": round(statistics.fmean(v), 1), "median": round(med, 1),
            "p05": round(p5, 1), "p25": round(pct(v, 0.25), 1), "p75": round(pct(v, 0.75), 1),
            "p95": round(pct(v, 0.95), 1), "worst_5pct_mean": round(statistics.fmean(tail), 1),
            "chance_below_cash_sale": round(100.0 * sum(1 for x, c in zip(values, cash) if x < c - 1e-9) / len(values), 1),
            "score": round(med - weight * (med - p5), 1),
        }
    return out


def after_the_answer(results, weight):
    """Once the tenant has answered an extension request: keep the property or sell and exchange?"""
    def stats(values):
        v = sorted(values)
        med, p5 = pct(v, 0.50), pct(v, 0.05)
        return {"median": round(med, 1), "p05": round(p5, 1), "score": round(med - weight * (med - p5), 1)}
    yes = [i for i, a in enumerate(results["_agreed"]) if a]
    no = [i for i, a in enumerate(results["_agreed"]) if not a]
    pick = lambda key, idx: [results[key][i] for i in idx]
    return {
        "share_agreeing_pct": round(100.0 * len(yes) / max(1, len(results["_agreed"])), 1),
        "if_tenant_agrees": {"keep": stats(pick("test_then_decide", yes)), "sell_and_exchange": stats(pick("extend_then_sell", yes))},
        "if_tenant_refuses": {"keep": stats(pick("extend_and_hold", no)), "sell_and_exchange": stats(pick("sell_exchange", no))},
    }


def area_outlook(rows):
    """Official projections for the county, re-indexed, plus one plainly-labelled extra scenario."""
    def n(rid):
        return _num(rows[rid]["value"])
    pop = {2025: n("PJ-001")}
    for rid, year in (("PJ-002", 2026), ("PJ-003", 2027), ("PJ-004", 2028), ("PJ-005", 2029), ("PJ-006", 2030),
                      ("PJ-007", 2031), ("PJ-008", 2032), ("PJ-009", 2033), ("PJ-010", 2034), ("PJ-011", 2035)):
        pop[year] = n(rid)
    start = n("PJ-020")                       # July 1, 2020
    trend = (pop[2025] / start) ** (1.0 / 5.0) - 1.0
    school = {"2025-26": n("PP-060")}
    for rid, year in (("PJ-030", "2026-27"), ("PJ-031", "2027-28"), ("PJ-032", "2028-29"), ("PJ-033", "2029-30"),
                      ("PJ-034", "2030-31"), ("PJ-035", "2031-32"), ("PJ-036", "2032-33"), ("PJ-037", "2033-34"),
                      ("PJ-038", "2034-35"), ("PJ-039", "2035-36")):
        school[year] = n(rid)
    base_school = school["2025-26"]
    return {
        "residents": [{"year": y, "official_projection": int(v), "index_2025_100": round(100.0 * v / pop[2025], 1),
                       "if_2020_2025_trend_continued": int(round(pop[2025] * (1.0 + trend) ** (y - 2025))),
                       "trend_index_2025_100": round(100.0 * (1.0 + trend) ** (y - 2025), 1)} for y, v in sorted(pop.items())],
        "residents_trend_pct_a_year": round(100.0 * trend, 2),
        "school_enrollment": [{"school_year": y, "official_projection": int(v), "index_2025_26_100": round(100.0 * v / base_school, 1)}
                              for y, v in school.items()],
        "source_rows": {"residents": "PJ-001 to PJ-011, PJ-020", "school_enrollment": "PP-060, PJ-030 to PJ-039"},
        "note": "The official columns are the State's own projections. The 'trend continued' column is this workbook's "
                "arithmetic (the 2020 to 2025 yearly change carried forward) and is a scenario, not an official figure.",
    }


def rank(summary, field="score"):
    return [k for k, _ in sorted(summary.items(), key=lambda kv: -kv[1][field])]


# --------------------------------------------------------------------------- run everything
def build():
    doc = load_assumptions()
    rows = load_rows()
    problems = check_anchors(doc, rows)
    if problems:
        raise SystemExit("anchor check failed:\n  " + "\n  ".join(problems))
    meta = doc["meta"]
    s = base_settings(doc)
    years = doc["expiry_years"]
    start, horizon = meta["start_year"], meta["horizon_year"]

    out = {"meta": {"unit": meta["unit"], "start_year": start, "horizon_year": horizon,
                    "trials": meta["trials"], "seed": meta["seed"],
                    "note": "Scenario output. Not a forecast, not an appraisal, not advice. "
                            "Base case is before income tax."},
           "strategies": [{"key": k, "label": lab, "family": fam} for k, lab, fam in STRATEGIES],
           "today": {}, "by_expiry": {}, "pooled": {}, "sensitivity": [], "breakevens": {},
           "sell_later": {}, "tax_sensitivity": [], "stress": [], "after_the_answer": {},
           "area_outlook": area_outlook(rows)}

    out["today"] = {
        "sale_price_as_is": {str(y): round(leased_value(100.0, s["cap_long"], y - start, s), 1) for y in years},
        "sale_price_if_extended": round(leased_value(s["extend_rent"], s["cap_long"], s["extend_term"], s), 1),
        "price_gain_from_extension_pct": {str(y): round(100.0 * (leased_value(s["extend_rent"], s["cap_long"], s["extend_term"], s)
                                                                 / leased_value(100.0, s["cap_long"], y - start, s) - 1.0), 1) for y in years},
    }

    pooled = {k: [] for k, _, _ in STRATEGIES}
    pooled["_agreed"] = []
    for y in years:
        res = simulate(s, y, meta["trials"], meta["seed"], start, horizon)
        for k in pooled:
            pooled[k].extend(res[k])
        summ = summarise(res, s["downside_weight"])
        ev = expected(s, y, start, horizon)
        out["by_expiry"][str(y)] = {"simulation": summ, "ranking": rank(summ),
                                    "expected_calm": {k: round(v, 1) for k, v in ev.items()}}
        out["sell_later"][str(y)] = sell_later_curve(s, y, start, horizon)
        out["breakevens"][str(y)] = {
            "renewal_chance_where_doing_nothing_equals_selling": _r(breakeven(s, y, "p_renew", 0.0, 100.0)),
            "short_lease_premium_where_doing_nothing_equals_selling": _r(breakeven(s, y, "short_premium", 0.0, 6.0), 2),
            "extension_rent_where_keeping_equals_selling": _r(breakeven(
                dict(s, p_extend_now=100.0), y, "extend_rent", 50.0, 130.0, a="extend_and_hold", b="sell_exchange")),
            "tax_drag_where_cash_sale_equals_doing_nothing": _r(breakeven(s, y, "tax_drag", -60.0, 60.0, a="sell_cash", b="do_nothing")),
        }
    out["after_the_answer"] = after_the_answer(pooled, s["downside_weight"])
    summ = summarise(pooled, s["downside_weight"])
    out["pooled"] = {"simulation": summ,
                     "ranking_by_score": rank(summ), "ranking_by_median": rank(summ, "median"),
                     "ranking_by_bad_case": rank(summ, "p05"),
                     "score_rule": "typical outcome minus %.1f x (typical outcome minus 1-in-20 bad outcome)" % s["downside_weight"]}
    for w in (0.0, 0.25, 0.5, 0.75, 1.0):
        out["pooled"].setdefault("ranking_by_weight", {})[str(w)] = rank(summarise(pooled, w))

    # one-at-a-time sensitivity of the calm expected gap, averaged over the six expiry years
    def avg_gap(t, a, b):
        return statistics.fmean(expected(t, y, start, horizon)[a] - expected(t, y, start, horizon)[b] for y in years)
    base_gap = avg_gap(s, "do_nothing", "sell_exchange")
    for key, spec in doc["settings"].items():
        if key in ("downside_weight", "terminal_years_left", "cap_sigma", "cap_revert", "p_credit", "p_regional_event", "p_site_damage",
                   "damage_loss", "p_lease_ends_on_damage", "regional_cap_bump", "regional_renew_hit", "repl_p_credit"):
            continue
        lo = avg_gap(dict(s, **{key: float(spec["low"])}), "do_nothing", "sell_exchange")
        hi = avg_gap(dict(s, **{key: float(spec["high"])}), "do_nothing", "sell_exchange")
        out["sensitivity"].append({"setting": key, "label": spec["label"], "kind": spec["kind"],
                                   "low": spec["low"], "high": spec["high"], "unit": spec["unit"],
                                   "gap_at_low": round(lo, 1), "gap_at_high": round(hi, 1),
                                   "swing": round(abs(hi - lo), 1)})
    out["sensitivity"].sort(key=lambda r: -r["swing"])
    out["sensitivity_base_gap"] = round(base_gap, 1)

    for drag in (0.0, 10.0, 20.0, 30.0):
        t = dict(s, tax_drag=drag)
        out["tax_sensitivity"].append({"tax_drag_pct": drag,
                                       "sell_cash": round(statistics.fmean(expected(t, y, start, horizon)["sell_cash"] for y in years), 1),
                                       "do_nothing": round(statistics.fmean(expected(t, y, start, horizon)["do_nothing"] for y in years), 1),
                                       "sell_exchange": round(statistics.fmean(expected(t, y, start, horizon)["sell_exchange"] for y in years), 1)})

    # named stress cases, simulated at a mid-window expiry with a smaller trial count
    stress = [
        ("Business as usual", {}),
        ("Tenant in trouble: renewal chance 40%, yearly failure chance 4%", {"p_renew": 40.0, "p_credit": 4.0}),
        ("Tenant healthy: renewal chance 90%, yearly failure chance 0.5%", {"p_renew": 90.0, "p_credit": 0.5}),
        ("Disaster-prone site: damage in 40% of regional events, 70% uninsured loss, lease ends 90% of the time",
         {"p_site_damage": 40.0, "damage_loss": 70.0, "p_lease_ends_on_damage": 90.0}),
        ("Well-protected site: damage in 5% of regional events, 10% uninsured loss, lease ends 10% of the time",
         {"p_site_damage": 5.0, "damage_loss": 10.0, "p_lease_ends_on_damage": 10.0}),
        ("Higher interest rates: buyer yield 7.5%, short-lease premium 3 points", {"cap_long": 7.5, "short_premium": 3.0}),
        ("Scarce Los Angeles land: buyer yield 5.5%, empty building worth 90% of leased value", {"cap_long": 5.5, "vacant_value": 90.0}),
        ("Sale price above $5,400,000: selling cost 7.1%", {"sell_cost": 7.1}),
    ]
    mid = years[len(years) // 2]
    for label, over in stress:
        t = dict(s, **over)
        summ = summarise(simulate(t, mid, max(2000, meta["trials"] // 4), meta["seed"] + 7, start, horizon), s["downside_weight"])
        out["stress"].append({"case": label, "expiry_year": mid, "changes": over, "ranking": rank(summ),
                              "summary": {k: {f: summ[k][f] for f in ("median", "p05", "score", "chance_below_cash_sale")} for k in summ}})
    return out


def _r(x, nd=1):
    return None if x is None else round(x, nd)


def main():
    out = build()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("wrote", os.path.relpath(OUT, os.path.dirname(HERE)))
    print("ranking by score:", " > ".join(out["pooled"]["ranking_by_score"]))


if __name__ == "__main__":
    main()
