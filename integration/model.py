#!/usr/bin/env python3
"""Projection and decision model for the integrated workbook (Session N, session-fe9d2a91).

Standard library only. No network. Deterministic: the same inputs give the same file.

Inputs
    integration/data/facts.json        verified figures; the model uses only rows that carry an "n" field
    integration/data/assumptions.json  scenario settings (sweeps and the seed)
Output
    integration/data/model_output.json

Every number the model takes from facts.json is checked against the words quoted from the official page:
if the number is not literally in the quote, the model stops.

The property's rent, expiry date and lease terms are not known, so every result is expressed
per $100 of current yearly rent, for each expiry year in the 2030 to 2035 window.
"""
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(DATA, "model_output.json")


# ----------------------------------------------------------------------------- inputs
def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


def number_tokens(x):
    """Ways a number may be printed on a page: 9853435 -> '9,853,435'; 4.98 -> '4.98'; 12.3 -> '12.3', '12.30'."""
    if float(x).is_integer():
        i = int(x)
        return {format(i, ","), str(i)}
    s = repr(float(x))
    return {s, s + "0", format(float(x), ",.1f"), format(float(x), ",.2f")}


def collect_inputs(facts):
    """Return ({name: number}, {name: fact id}); stop if a number is not in its quote."""
    values, origin = {}, {}
    for f in facts:
        for name, x in (f.get("n") or {}).items():
            if f.get("status") != "verified":
                raise SystemExit(f"model input {name} comes from {f['id']}, which is not a verified row")
            quote = f.get("quote", "")
            if not any(tok in quote for tok in number_tokens(x)):
                raise SystemExit(f"model input {name}={x} is not in the quoted text of {f['id']}")
            if name in values:
                raise SystemExit(f"model input {name} is defined twice")
            values[name], origin[name] = x, f["id"]
    return values, origin


# ----------------------------------------------------------------------------- formulas
def annuity(rent, growth, rate, years):
    """Present value of `years` yearly payments, the first one a year from now, growing at `growth`."""
    return sum(rent * (1 + growth) ** (t - 1) / (1 + rate) ** t for t in range(1, years + 1))


def last_rent(rent, growth, years):
    return rent * (1 + growth) ** (years - 1)


def hold_parts(years, rate, cap, growth=0.0, rent=100.0):
    """(A, B): hold value = A + B * mix, where mix is the expected reversion as a share of leased value at the old rent."""
    a = annuity(rent, growth, rate, years)
    b = last_rent(rent, growth, years) / cap / (1 + rate) ** years
    return a, b


def mix(p, recapture, vacant_ratio):
    return p * recapture + (1 - p) * vacant_ratio


def hold_value(years, rate, cap, p, recapture, vacant_ratio, growth=0.0, rent=100.0):
    a, b = hold_parts(years, rate, cap, growth, rent)
    return a + b * mix(p, recapture, vacant_ratio)


def breakeven_p(sale_yield, years, rate, cap, recapture, vacant_ratio, growth=0.0, rent=100.0):
    """Renewal probability at which holding to expiry is worth exactly a sale today at `sale_yield`."""
    a, b = hold_parts(years, rate, cap, growth, rent)
    return ((rent / sale_yield - a) / b - vacant_ratio) / (recapture - vacant_ratio)


def prob_within(p30, years, horizon=30.0):
    """Chance of at least one event in `years`, given the chance in `horizon` years, at a constant yearly rate."""
    return 1 - (1 - p30) ** (years / horizon)


def cumulative(rate, years):
    return 1 - (1 - rate) ** years


def transfer_tax_rate(price, v):
    county = v["county_cents"] / v["county_per"]
    city = v["city_base"] / 100
    if price >= v["ula_t2"]:
        city += v["ula_r2"] / 100
    elif price > v["ula_t1"]:
        city += v["ula_r1"] / 100
    return county + city


def r(x, nd=2):
    return round(float(x) + 0.0, nd)


def pct(x, nd=1):
    return r(100 * x, nd)


def percentile(sorted_values, q):
    """Nearest-rank percentile on an already sorted list."""
    k = max(0, min(len(sorted_values) - 1, int(math.ceil(q * len(sorted_values))) - 1))
    return sorted_values[k]


# ----------------------------------------------------------------------------- model
def build(facts_doc, settings_doc):
    facts = facts_doc["facts"]
    v, origin = collect_inputs(facts)
    by_id = {f["id"]: f for f in facts}
    cfg = settings_doc["model"]
    computed = []

    def comp(cid, page, group, label, value, formula, names, note=None):
        ids = []
        for n in names:
            fid = origin[n]
            if fid not in ids:
                ids.append(fid)
        row = {"id": cid, "page": page, "group": group, "label": label, "value": value, "formula": formula,
               "inputs": ids, "sources": sorted({by_id[i]["source"] for i in ids}), "status": "computed"}
        if note:
            row["note"] = note
        computed.append(row)

    # ---- area
    comp("K-001", "market-economics", "Population", "Gap between the state and federal counts of county residents",
         f"{v['dof_2025'] - v['census_county']:,} ({pct((v['dof_2025'] - v['census_county']) / v['census_county'])}%)",
         f"{v['dof_2025']:,} - {v['census_county']:,}", ["dof_2025", "census_county"],
         "Two official series, two methods. Neither is corrected here.")
    for cid, key, year in (("K-002", "dof_2030", 2030), ("K-003", "dof_2035", 2035), ("K-004", "dof_2040", 2040), ("K-005", "dof_2050", 2050)):
        comp(cid, "projection-model", "Residents", f"Projected change in county residents, 2025 to {year}",
             f"{pct(v[key] / v['dof_2025'] - 1, 2):+.2f}%", f"{v[key]:,} / {v['dof_2025']:,} - 1", [key, "dof_2025"])
    comp("K-006", "projection-model", "School enrollment", "Projected change in county school enrollment, 2025-26 to 2035-36",
         f"{pct(v['k12_2035'] / v['k12_2025'] - 1):+.1f}% ({v['k12_2035'] - v['k12_2025']:+,} students)",
         f"{v['k12_2035']:,} / {v['k12_2025']:,} - 1", ["k12_2035", "k12_2025"])
    comp("K-007", "market-economics", "Schools", "Change in county school enrollment over the last ten years",
         f"{pct(v['k12_2025'] / v['k12_2015'] - 1):+.1f}%", f"{v['k12_2025']:,} / {v['k12_2015']:,} - 1", ["k12_2025", "k12_2015"])
    food_cagr = (v["food_2050"] / v["food_2022"]) ** (1 / 28) - 1
    comp("K-008", "projection-model", "Jobs", "Projected growth in regional food-service jobs, per year",
         f"{pct(food_cagr, 2):.2f}% a year", f"({v['food_2050']} / {v['food_2022']}) ^ (1/28) - 1", ["food_2050", "food_2022"])

    # ---- tenant
    comp("K-010", "tenant", "Restaurants", "Change in the number of restaurants over the year",
         f"{pct(v['units_now'] / v['units_year_ago'] - 1):+.1f}% ({v['units_now'] - v['units_year_ago']:+,})",
         f"{v['units_now']:,} / {v['units_year_ago']:,} - 1", ["units_now", "units_year_ago"])
    q_rate = v["closed_q"] / v["units_q_start"] * 52 / 12
    comp("K-011", "tenant", "Restaurants", "Closures in the latest quarter, as a yearly rate",
         f"{pct(q_rate)}% a year", f"{v['closed_q']} / {v['units_q_start']:,} x 52/12 (a 12-week quarter)", ["closed_q", "units_q_start"])
    g_lo, g_hi = v["closures_lo"] / v["units_fy25"], v["closures_hi"] / v["units_fy25"]
    comp("K-012", "tenant", "Restaurants", "Closures the company expects in fiscal 2026, as a share of all restaurants",
         f"{pct(g_lo)}% to {pct(g_hi)}%", f"{v['closures_lo']} to {v['closures_hi']} / {v['units_fy25']:,}", ["closures_lo", "units_fy25"])
    comp("K-013", "tenant", "Restaurants", "Closure programme as a share of all restaurants",
         f"{pct(v['program_lo'] / v['units_year_ago'])}% to {pct(v['program_hi'] / v['units_year_ago'])}%",
         f"{v['program_lo']} to {v['program_hi']} / {v['units_year_ago']:,} (the earliest count read by this session)", ["program_lo", "units_year_ago"])
    comp("K-014", "tenant", "Restaurants", "Share of restaurants in California",
         f"{pct(v['units_ca'] / v['units_fy25'])}%", f"{v['units_ca']} / {v['units_fy25']:,}", ["units_ca", "units_fy25"],
         "California is the company's largest market.")
    net_debt = v["ltd"] + v["cur_debt"] - v["cash"]
    ebitda_mid = (v["ebitda_lo"] + v["ebitda_hi"]) / 2
    comp("K-015", "tenant", "Balance sheet", "Debt less cash, against forecast yearly earnings before interest, tax and depreciation",
         f"{r(net_debt / 1000 / ebitda_mid, 1)} times", f"({v['ltd']:,} + {v['cur_debt']:,} - {v['cash']:,}) / 1,000 / {ebitda_mid}",
         ["ltd", "cur_debt", "cash", "ebitda_lo"], "Uses the midpoint of the company's forecast. Lease obligations are not included.")
    comp("K-016", "tenant", "Sales and earnings", "Change in rent collected from franchisees",
         f"{pct(v['rent_q'] / v['rent_q_prior'] - 1):+.1f}% in the quarter; {pct(v['rent_ytd'] / v['rent_ytd_prior'] - 1):+.1f}% year to date",
         f"{v['rent_q']:,} / {v['rent_q_prior']:,} - 1; {v['rent_ytd']:,} / {v['rent_ytd_prior']:,} - 1", ["rent_q", "rent_q_prior"])
    comp("K-017", "tenant", "Sales and earnings", "Margin the company keeps on rent passed through from franchisees",
         f"{pct((v['rent_q'] - v['occ_q']) / v['rent_q'])}%", f"({v['rent_q']:,} - {v['occ_q']:,}) / {v['rent_q']:,}", ["rent_q", "occ_q"],
         "On many sites the company is the tenant and sublets to a franchisee.")
    third = v["own_bldg_leased_land"] + v["leased"] + v["franchisee_direct"]
    comp("K-018", "tenant", "How it holds its restaurant sites", "Sites on land the company does not own: who the landlord's tenant is",
         f"Company {pct((v['own_bldg_leased_land'] + v['leased']) / third)}%; franchisee {pct(v['franchisee_direct'] / third)}%",
         f"({v['own_bldg_leased_land']} + {v['leased']:,}) / {third:,}; {v['franchisee_direct']} / {third:,}",
         ["own_bldg_leased_land", "leased", "franchisee_direct"],
         "A share of all such sites, not a statement about the subject property.")
    comp("K-019", "tenant", "How it holds its restaurant sites", "Of those sites, ground leases where the company owns the building",
         f"{pct(v['own_bldg_leased_land'] / third)}%", f"{v['own_bldg_leased_land']} / {third:,}", ["own_bldg_leased_land", "leased", "franchisee_direct"])

    # ---- pricing
    comp("K-020", "valuation", "What buyers pay for leased properties", "Purchase yield above the 10-year Treasury yield",
         f"{r(v['nnn_buy'] - v['t10'])} points (NNN REIT); {r(v['o_buy_q'] - v['t10'])} points (Realty Income)",
         f"{v['nnn_buy']} - {v['t10']}; {v['o_buy_q']} - {v['t10']}", ["nnn_buy", "t10", "o_buy_q"])
    same_q, same_9 = v["same_q"] / v["exp_q"], v["same_9m"] / v["exp_9m"]
    new_q, new_9 = v["new_q"] / v["exp_q"], v["new_9m"] / v["exp_9m"]
    comp("K-021", "valuation", "What happens when leases expire", "Share of expiring leases renewed by the same tenant",
         f"{pct(same_q)}% in the quarter; {pct(same_9)}% in nine months", f"{v['same_q']} / {v['exp_q']}; {v['same_9m']} / {v['exp_9m']:,}",
         ["same_q", "exp_q", "same_9m", "exp_9m"], "A portfolio of 15,536 properties across many industries. Not specific to restaurants or to Los Angeles.")
    comp("K-022", "valuation", "What happens when leases expire", "Share of expiring leases taken by a new tenant",
         f"{pct(new_q)}% in the quarter; {pct(new_9)}% in nine months", f"{v['new_q']} / {v['exp_q']}; {v['new_9m']} / {v['exp_9m']:,}",
         ["new_q", "exp_q", "new_9m", "exp_9m"])
    comp("K-023", "valuation", "What happens when leases expire", "Vacant sales for every 100 expiring leases",
         f"{r(100 * v['vac_q'] / v['exp_q'], 1)} in the quarter; {r(100 * v['vac_9m'] / v['exp_9m'], 1)} in nine months",
         f"{v['vac_q']} / {v['exp_q']}; {v['vac_9m']} / {v['exp_9m']:,}", ["vac_q", "exp_q", "vac_9m", "exp_9m"],
         "Vacant sales include properties that became vacant in earlier periods, so the three shares do not add to 100.")
    vq, iq = v["vac_usd_q"] * 1000 / v["vac_sf_q"], v["inc_usd_q"] * 1000 / v["inc_sf_q"]
    v9, i9 = v["vac_usd_9m"] * 1000 / v["vac_sf_9m"], v["inc_usd_9m"] * 1000 / v["inc_sf_9m"]
    ratio_q, ratio_9 = vq / iq, v9 / i9
    comp("K-024", "valuation", "What vacant buildings sell for", "Price per square foot: vacant against leased",
         f"${r(vq, 0):,.0f} against ${r(iq, 0):,.0f} in the quarter; ${r(v9, 0):,.0f} against ${r(i9, 0):,.0f} in nine months",
         f"{v['vac_usd_q']:,}k / {v['vac_sf_q']:,}; {v['inc_usd_q']:,}k / {v['inc_sf_q']:,}; {v['vac_usd_9m']:,}k / {v['vac_sf_9m']:,}; {v['inc_usd_9m']:,}k / {v['inc_sf_9m']:,}",
         ["vac_usd_q", "inc_usd_q", "vac_usd_9m", "inc_usd_9m"])
    comp("K-025", "valuation", "What vacant buildings sell for", "A vacant property's price as a share of a leased one's, per square foot",
         f"{pct(ratio_q)}% in the quarter; {pct(ratio_9)}% in nine months", "vacant price per square foot / leased price per square foot",
         ["vac_usd_q", "inc_usd_q", "vac_usd_9m", "inc_usd_9m"],
         "National averages over different buildings. In central Los Angeles the land may set the price; only an appraisal can say.")
    comp("K-026", "valuation", "Interest rates", "10-year Treasury yield today against the February 2026 federal projection",
         f"{r(v['t10'] - v['cbo_10y_2027'])} to {r(v['t10'] - v['cbo_10y_2025'])} points higher",
         f"{v['t10']} - {v['cbo_10y_2027']}; {v['t10']} - {v['cbo_10y_2025']}", ["t10", "cbo_10y_2027", "cbo_10y_2025"],
         "Higher long-term rates lower what buyers pay for fixed rent.")

    # ---- taxes
    county = v["county_cents"] / v["county_per"]
    low, mid, top = (transfer_tax_rate(p, v) for p in (1_000_000, 6_000_000, 11_000_000))
    comp("K-030", "taxes", "Tax on the sale price", "County transfer tax as a percentage",
         f"{pct(county, 2)}%", f"{v['county_cents']} / {v['county_per']}", ["county_cents"])
    comp("K-031", "taxes", "Tax on the sale price", "County and city transfer tax together, by sale price",
         f"{pct(low, 2)}% up to $5,400,000; {pct(mid, 2)}% above that; {pct(top, 2)}% at $10,900,000 or more",
         f"{pct(county, 2)}% + {v['city_base']}%; + {v['ula_r1']}%; + {v['ula_r2']}%", ["county_cents", "city_base", "ula_r1", "ula_r2", "ula_t1"])
    cliff = v["ula_t1"] * (1 - low) / (1 - mid)
    comp("K-032", "taxes", "Tax on the sale price", "Price needed above the first threshold to net more than a sale at exactly $5,400,000",
         f"${cliff:,.0f}", f"{v['ula_t1']:,} x (1 - {pct(low, 2)}%) / (1 - {pct(mid, 2)}%)", ["ula_t1", "city_base", "ula_r1", "county_cents"],
         f"A sale between $5,400,000 and ${cliff:,.0f} leaves the seller with less than a sale at $5,400,000.")
    extra_tax = v["ula_t1"] * (mid - low)
    comp("K-033", "taxes", "Tax on the sale price", "Extra tax triggered by the first dollar above $5,400,000",
         f"${extra_tax:,.0f}", f"{v['ula_t1']:,} x {v['ula_r1']}%", ["ula_t1", "ula_r1"])
    combined = v["fed_ltcg"] + v["niit"] + v["ca_top"] + v["ca_extra"]
    comp("K-034", "taxes", "Tax on the gain", "Top federal and California rates on a long-term gain, added together",
         f"{r(combined, 1)}%", f"{v['fed_ltcg']} + {v['niit']} + {v['ca_top']} + {v['ca_extra']}", ["fed_ltcg", "niit", "ca_top", "ca_extra"],
         "An upper bound for a high-income California resident. The part of the gain that reflects past depreciation is taxed federally at up to 25% instead of 20%.")

    # ---- hazards and tenant events before expiry
    years_list = [y - cfg["valuation_year"] for y in cfg["expiry_years"]]
    events = []
    for year, t in zip(cfg["expiry_years"], years_list):
        events.append({
            "expiry_year": year, "years": t,
            "quake_6_7": pct(prob_within(v["eq67"] / 100, t)),
            "quake_7_0": pct(prob_within(v["eq70"] / 100, t)),
            "quake_7_5": pct(prob_within(v["eq75"] / 100, t)),
            "closure_low": pct(cumulative(g_lo, t)),
            "closure_high": pct(cumulative(q_rate, t)),
        })
    comp("K-040", "hazards", "Earthquake", "Chance of a magnitude 6.7 or larger earthquake in the region before the lease expires",
         f"{events[0]['quake_6_7']}% by {cfg['expiry_years'][0]}; {events[-1]['quake_6_7']}% by {cfg['expiry_years'][-1]}",
         "1 - (1 - 60%) ^ (years / 30), a constant yearly rate", ["eq67"],
         "Somewhere in the Los Angeles region. Not the chance of damage to this building.")
    comp("K-041", "hazards", "Earthquake", "Chance of a magnitude 7 or larger earthquake in the region before the lease expires",
         f"{events[0]['quake_7_0']}% by {cfg['expiry_years'][0]}; {events[-1]['quake_7_0']}% by {cfg['expiry_years'][-1]}",
         "1 - (1 - 46%) ^ (years / 30), a constant yearly rate", ["eq70"])
    comp("K-042", "tenant", "Restaurants", "Chance an average restaurant in the system closes before the lease expires",
         f"{events[0]['closure_low']}% to {events[0]['closure_high']}% by {cfg['expiry_years'][0]}; {events[-1]['closure_low']}% to {events[-1]['closure_high']}% by {cfg['expiry_years'][-1]}",
         f"1 - (1 - rate) ^ years, at {pct(g_lo)}% and {pct(q_rate)}% a year", ["closures_lo", "units_fy25", "closed_q", "units_q_start"],
         "Closures target underperforming restaurants. This restaurant's sales are not known, so its own chance may be far lower or higher. A closed restaurant still owes rent until the lease ends.")

    # ---- area index table
    pop = by_id["J-S01"]["series"]
    k12 = by_id["J-S02"]["series"]
    wage, level = [], 100.0
    for year in range(2025, 2037):
        if year == 2026:
            level *= 1 + v["eci_2026"] / 100
        elif year == 2027:
            level *= 1 + v["eci_2027"] / 100
        elif year > 2027:
            level *= 1 + v["eci_later"] / 100
        wage.append(level)
    area = []
    for i, year in enumerate(range(2025, 2037)):
        area.append({
            "year": year,
            "residents": pop[str(year)], "residents_index": r(100 * pop[str(year)] / pop["2025"], 1),
            "students": k12[str(year)], "students_index": r(100 * k12[str(year)] / k12["2025"], 1),
            "us_wage_index": r(wage[i], 1),
            "flat_rent_real_2pct": r(100 / 1.02 ** i, 1),
            "flat_rent_real_3pct": r(100 / 1.03 ** i, 1),
        })

    # ---- hold or sell
    rate = v["t10"] / 100
    cap = v["nnn_buy"] / 100
    rec = v["recap_9m"] / 100
    p0 = same_9
    d0 = round(ratio_9, 4)
    d_alt = round(ratio_q, 4)
    g0, g_alt = cfg["rent_growth"]["base"], cfg["rent_growth"]["alt"]
    base = {"discount_rate_pct": v["t10"], "buyer_yield_at_renewal_pct": v["nnn_buy"], "renewal_probability_pct": pct(p0),
            "renewal_rent_pct_of_old": v["recap_9m"], "vacant_price_pct_of_leased": pct(d0), "rent_growth_pct": 100 * g0}

    grid = []
    for year, t in zip(cfg["expiry_years"], years_list):
        a, b = hold_parts(t, rate, cap, g0)
        h = a + b * mix(p0, rec, d0)
        row = {
            "expiry_year": year, "years_of_rent_left": t,
            "pv_rent": r(a), "pv_expected_resale": r(b * mix(p0, rec, d0)), "hold_value": r(h),
            "equivalent_sale_yield_pct": r(100 * 100 / h),
            "hold_value_if_renewed": r(a + b * rec), "hold_value_if_vacant": r(a + b * d0),
            "yield_if_renewed_pct": r(100 * 100 / (a + b * rec)), "yield_if_vacant_pct": r(100 * 100 / (a + b * d0)),
            "gap_renewed_minus_vacant": r(b * (rec - d0)),
            "value_of_certain_renewal": r(b * (rec - mix(p0, rec, d0))),
            "breakeven_renewal_probability_pct": {
                f"{s:.1f}": r(100 * breakeven_p(s / 100, t, rate, cap, rec, d0, g0), 1) for s in cfg["sale_yields_swept"]},
        }
        grid.append(row)

    mid_year = 2032
    t_mid = mid_year - cfg["valuation_year"]

    def hv(**kw):
        args = dict(years=t_mid, rate=rate, cap=cap, p=p0, recapture=rec, vacant_ratio=d0, growth=g0)
        args.update(kw)
        return hold_value(**args)

    h_base = hv()
    sens_defs = [
        ("Tenant certainly renews", dict(p=1.0), ["C-035"]),
        ("Renewal chance 90%", dict(p=0.9), ["C-035"]),
        ("Renewal chance 50%", dict(p=0.5), ["C-035"]),
        ("Tenant certainly leaves", dict(p=0.0), ["C-035"]),
        ("Vacant building sells for 86% of leased price, not 63%", dict(vacant_ratio=d_alt), ["C-040", "C-041"]),
        ("Buyer wants 6.5% on the renewed lease, not 7.3%", dict(cap=v["o_buy_9m"] / 100), ["C-018"]),
        ("Buyer wants 7.8% on the renewed lease, not 7.3%", dict(cap=v["nnn_sell_q"] / 100), ["C-012"]),
        ("Sale money would earn 6.6%, not 4.98%", dict(rate=v["o_buy_q"] / 100), ["C-017"]),
        ("Sale money would earn 7.3%, not 4.98%", dict(rate=v["nnn_buy"] / 100), ["C-010"]),
        ("Rent rises 2% a year until expiry", dict(growth=g_alt), ["T-054"]),
        ("Renewal rent 103.5% of old rent, not 103.1%", dict(recapture=v["recap_q"] / 100), ["C-038"]),
    ]
    sensitivity = []
    for label, change, anchors in sens_defs:
        h = hv(**change)
        sensitivity.append({"case": label, "hold_value": r(h), "change_pct": r(100 * (h / h_base - 1), 1),
                            "equivalent_sale_yield_pct": r(100 * 100 / h), "anchors": anchors})

    shock = cfg["stress"]["yield_shock_points"] / 100
    early = cfg["stress"]["rent_stops_years_early"]

    def rent_stops(years, stop_years):
        a = annuity(100.0, g0, rate, years - stop_years)
        b = last_rent(100.0, g0, years) / cap / (1 + rate) ** years
        return a + b * d0

    stress_defs = [
        ("Tenant leaves at expiry", hv(p=0.0), ["T-008", "C-042"]),
        ("Buyers' yields and interest rates 2 points higher", hv(rate=rate + shock, cap=cap + shock), ["C-001", "C-005"]),
        ("Tenant leaves and yields are 2 points higher", hv(p=0.0, rate=rate + shock, cap=cap + shock), ["T-008", "C-001"]),
        (f"Rent stops {early} years before expiry, then the building is sold vacant", rent_stops(t_mid, early), ["T-033", "C-042"]),
        (f"Rent stops {early} years early, sold vacant, yields 2 points higher",
         annuity(100.0, g0, rate + shock, t_mid - early) + last_rent(100.0, g0, t_mid) / (cap + shock) / (1 + rate + shock) ** t_mid * d0,
         ["T-033", "C-001", "C-042"]),
    ]
    stress = [{"case": label, "hold_value": r(h), "change_pct": r(100 * (h / h_base - 1), 1),
               "years_of_rent_lost": r((h_base - h) / 100, 1), "anchors": anchors} for label, h, anchors in stress_defs]

    # value of an early extension, and the lowest renewal rent worth accepting for certainty
    extension = []
    for p in cfg["renewal_probabilities_swept"]:
        p = p0 if p == "base" else p
        a, b = hold_parts(t_mid, rate, cap, g0)
        expected = mix(p, rec, d0)
        extension.append({"renewal_probability_pct": pct(p), "is_base": p == p0, "hold_value": r(a + b * expected),
                          "walk_away_rent_pct_of_current": r(100 * expected, 1),
                          "value_of_certainty": r(b * (rec - expected)),
                          "value_of_certainty_years_of_rent": r(b * (rec - expected) / 100, 2)})

    # ---- after a sale: income compared with the rent today
    exchange = []
    tt_low, tt_mid = low, mid
    tax = combined / 100
    for s in cfg["sale_yields_swept"]:
        price = 100 / (s / 100)
        row = {"sale_yield_pct": s, "price_per_100_rent": r(price),
               "exchange_into_7_3_pct": r(price * (1 - tt_low) * v["nnn_buy"] / 100, 1),
               "exchange_into_6_6_pct": r(price * (1 - tt_low) * v["o_buy_q"] / 100, 1),
               "exchange_into_7_3_pct_upper_band": r(price * (1 - tt_mid) * v["nnn_buy"] / 100, 1)}
        for gshare in cfg["gain_shares_swept"]:
            row[f"taxable_then_treasury_gain_{int(gshare * 100)}"] = r(price * (1 - tt_low - gshare * tax) * v["t10"] / 100, 1)
        exchange.append(row)

    # ---- simulation (same seed, same result)
    mc_cfg = cfg["monte_carlo"]
    rng = random.Random(mc_cfg["seed"])
    lo_same, hi_same = sorted((same_9, same_q))
    lo_new, hi_new = sorted((new_q, new_9))
    lo_rec, hi_rec = sorted((v["recap_9m"] / 100, v["recap_q"] / 100))
    lo_d, hi_d = sorted((d0, d_alt))
    lo_cap, hi_cap = v["o_buy_9m"] / 100, v["nnn_sell_q"] / 100
    simulation = []
    for year, t in zip(cfg["expiry_years"], years_list):
        a = annuity(100.0, g0, rate, t)
        disc = (1 + rate) ** t
        values, relet = [], 0
        for _ in range(mc_cfg["trials"]):
            p_relet = (lo_same + (hi_same - lo_same) * rng.random()) + (lo_new + (hi_new - lo_new) * rng.random())
            c = lo_cap + (hi_cap - lo_cap) * rng.random()
            m = lo_rec + (hi_rec - lo_rec) * rng.random()
            d = lo_d + (hi_d - lo_d) * rng.random()
            if rng.random() < p_relet:
                share, relet = m, relet + 1
            else:
                share = d
            values.append(a + 100.0 / c / disc * share)
        values.sort()
        mean = sum(values) / len(values)
        simulation.append({
            "expiry_year": year, "trials": mc_cfg["trials"], "share_relet_pct": r(100 * relet / len(values), 1),
            "mean": r(mean), "p05": r(percentile(values, 0.05)), "p25": r(percentile(values, 0.25)),
            "p50": r(percentile(values, 0.50)), "p75": r(percentile(values, 0.75)), "p95": r(percentile(values, 0.95)),
            "chance_hold_beats_sale_pct": {
                f"{s:.1f}": r(100 * sum(1 for x in values if x > 100 / (s / 100)) / len(values), 1) for s in cfg["sale_yields_swept"]},
        })

    return {
        "meta": {"session": "session-fe9d2a91", "generated_by": "integration/model.py",
                 "unit": "Per $100 of current yearly rent, before tax, unless a row says otherwise",
                 "inputs_checked_against_quotes": len(v)},
        "base_case": base,
        "computed": computed,
        "area_by_year": area,
        "events_before_expiry": events,
        "hold_by_expiry_year": grid,
        "sensitivity_expiry_2032": {"expiry_year": mid_year, "base_hold_value": r(h_base), "rows": sensitivity},
        "stress_expiry_2032": {"expiry_year": mid_year, "base_hold_value": r(h_base), "rows": stress},
        "extension_expiry_2032": {"expiry_year": mid_year, "rows": extension},
        "after_sale_income": {"note": "Yearly income per $100 of current rent after selling at the yield shown. Brokerage and closing costs are not included.",
                              "transfer_tax_pct": {"up_to_5_4m": pct(tt_low, 2), "above_5_4m": pct(tt_mid, 2)},
                              "tax_rate_on_gain_pct": r(combined, 1), "rows": exchange},
        "simulation": {"seed": mc_cfg["seed"],
                       "ranges": {"renewed_by_same_tenant_pct": [pct(lo_same), pct(hi_same)], "new_tenant_pct": [pct(lo_new), pct(hi_new)],
                                  "renewal_rent_pct_of_old": [pct(lo_rec), pct(hi_rec)], "vacant_price_pct_of_leased": [pct(lo_d), pct(hi_d)],
                                  "buyer_yield_pct": [pct(lo_cap), pct(hi_cap)]},
                       "rows": simulation},
    }


def render():
    doc = build(load("facts.json"), load("assumptions.json"))
    return json.dumps(doc, indent=1, ensure_ascii=False, sort_keys=False) + "\n"


def main():
    text = render()
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(text)
    doc = json.loads(text)
    print(f"wrote {os.path.relpath(OUT, os.path.dirname(HERE))}: {len(doc['computed'])} computed rows, "
          f"{doc['meta']['inputs_checked_against_quotes']} inputs checked against quotes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
