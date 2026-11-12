#!/usr/bin/env python3
"""Normalized projection model - Session O (session-6596c3f2).
Per $100k of NOI (=$1.00 normalized to 1.0). NO dollar valuation is asserted:
rent, price, cap rate and basis are unverified (B02/B07/B09) and stay blank
in the data ledger. All parameters below are LABELED ANALYST ASSUMPTIONS,
anchored only to the verified 10-yr Treasury 4.88% (M28, 2026-11-09).
Deterministic + Monte Carlo (seed 20261112, 10,000 trials). Stdlib only.
Output: data/model_output.json  (wealth = PV multiple of 1.0x annual NOI,
discount 6%/yr to 2026, horizon 2040, interim rent included)."""
import json, math, random, statistics
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
ASSUMPTIONS = {
 "anchor_10y_treasury_pct": 4.88, "anchor_source": "M28 (S05, FRED DGS10, 2026-11-09)",
 "cap_short_term_base_pct": 6.75, "cap_short_term_range_pct": [6.0, 7.5],
 "cap_long_term_base_pct": 6.25, "cap_long_term_range_pct": [5.75, 6.9],
 "discount_rate_pct": 6.0, "sell_cost_pct": 2.5, "transfer_tax_below_ula_pct": 0.56,
 "dark_land_factor_of_leased_value": 0.55, "downtime_months_base": 18,
 "renewal_rent_haircut_pct": 10, "replacement_growth_pct": 3.0,
 "tax_drag_strategy_E_assumption": "20% of an assumed 60% gain fraction = 12% of price (ILLUSTRATION ONLY - real tax is blank, Q-15)",
 "note": "Assumptions are not market data. B07 (actual cap rate) is blank by design. Sensitivity grid below shows the decision across the full range."
}
def pv(rents, exit_value, exit_year, disc=0.06):
    v = sum(r/((1+disc)**(i+1)) for i, r in enumerate(rents)) + exit_value/((1+disc)**exit_year)
    return v
def det():
    # years from 2026: A sell 2027(yr1), B sell 2030(yr4) after extension, C expiry 2032(yr6), D hold to 2040(yr14)
    # Comparable metric: PV(rents)+PV(net exit proceeds). Reinvestment growth excluded for ALL strategies equally.
    A = pv([1.0]*1, (1/0.0675)*0.9694, 1)
    B = pv([1.0]*4, (1/0.0625)*0.9694, 4)
    C = pv([1.0]*6, (1/0.0675)*0.55, 6)  # dark sale at land factor
    D = pv([1.0]*6 + [0.9]*8, (0.9/0.08), 14)
    E = pv([1.0]*1, (1/0.0675)*0.9694*0.88, 1)  # after illustrative tax drag
    return {"A_sell_now_1031": round(A,2), "B_extend_then_sell": round(B,2),
            "C_hold_to_expiry_dark_sale": round(C,2), "D_renew_at_expiry_hold": round(D,2),
            "E_sell_now_taxable_illustration": round(E,2)}
def mc(n=10000, seed=20261112):
    rng = random.Random(seed)
    out = {k: [] for k in ["A","B","C","D","E"]}
    for _ in range(n):
        capS = rng.uniform(6.0,7.5)/100; capL = rng.uniform(5.75,6.9)/100
        dark = rng.uniform(0.35,0.7); down = rng.uniform(0.75,2.5)  # years dark for C/D delay
        hair = rng.uniform(0,0.35)  # hazard/credit haircut hitting hold paths
        g = rng.uniform(0.0,0.02)   # rent growth on extended/renewed rent
        A = pv([1.0], (1/capS)*0.9694, 1)
        B = pv([1.0]*4, (1/capL)*0.9694*(1-hair*0.3), 4)
        C = pv([1.0]*6, (1/capS)*dark, 6+int(down))
        D = pv([1.0]*6 + [(0.9)*(1-hair)]*8, ((0.9)*(1-hair)/0.08), 14)
        E = A*0.88
        for k,v in zip(out, [A,B,C,D,E]): out[k].append(v)
    def stats(v):
        s = sorted(v); ce = (sum(x**(-1) for x in v)/len(v))**(-1)  # CRRA-2 certainty equivalent (harmonic form)
        return {"mean": round(statistics.mean(v),2), "p05": round(s[int(0.05*len(s))],2),
                "p50": round(statistics.median(v),2), "ce_crra2": round(ce,2)}
    return {k: stats(v) for k,v in out.items()}
def expiry_grid():
    # PV of hold-to-expiry + dark sale, by actual expiry year (term-decay illustration)
    rows=[]
    for exp in range(2030,2036):
        yrs = exp-2026
        rows.append({"expiry_year": exp, "years_of_rent_from_2026": yrs,
                     "pv_multiple_of_annual_noi": round(pv([1.0]*yrs, (1/0.0675)*0.55, yrs),2)})
    return rows
if __name__ == "__main__":
    d, m, g = det(), mc(), expiry_grid()
    # term value of extension at base caps, per $1 NOI
    ext = {"sell_now_multiple": round(1/0.0675,2), "sell_with_long_term_multiple": round(1/0.0625,2),
           "extension_uplift_pct": round(((1/0.0625)/(1/0.0675)-1)*100,1),
           "dark_sale_multiple_at_expiry": round((1/0.0675)*0.55,2)}
    payload = {"meta": {"model": "Session O normalized model v1", "seed": 20261112, "trials": 10000,
                        "unit": "PV multiple of 1.0x annual NOI (per $100k NOI, multiply by NOI/1.0 in $100k units)",
                        "warning": "Illustrative framework only. No rent, price, or tax figure is verified. See B02/B07/B09."},
               "assumptions": ASSUMPTIONS, "deterministic": d, "monte_carlo": m,
               "term_value": ext, "expiry_grid_hold_to_expiry": g}
    (ROOT/"data"/"model_output.json").write_text(json.dumps(payload, indent=1)+"\n")
    print(json.dumps(payload, indent=1))
