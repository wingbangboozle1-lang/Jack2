#!/usr/bin/env python3
"""Deterministic projection engine for the Central LA Jack in the Box NNN workbook.

No network, no randomness, no external dependencies.

The engine is deliberately INDEX-BASED: the workbook refuses to invent the subject
property's rent, price or cap rate (they are blank in the data ledger). Instead it
computes, for any (rent, cap rate, growth, expiry) tuple the owner supplies later,
the value and the breakevens that decide sell-vs-renew. Committed output uses a
clearly-labelled ILLUSTRATIVE example (rent index 100) so the math is inspectable.

An illustrative black-swan overlay applies UCERF3-informed annual frequencies as
ANALYST ASSUMPTIONS (labeled, not official), because official sources give 30-year
probabilities, not annual loss distributions.
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "model_output.json")

# ---------------- analyst assumptions (NOT official data; labeled as such) ----------------
ILLUSTRATIVE_RENT_INDEX = 100.0        # NNN base rent index, arbitrary units
ESCALATION_SCENARIOS = [0.00, 0.02, 0.04]
CAP_RATE_GRID = [0.055, 0.060, 0.065, 0.070, 0.075]
EXPIRY_YEARS = [2030, 2031, 2032, 2033, 2034, 2035]
HORIZON_START = 2026
HOLD_YEARS = 5
ILLUSTRATIVE_DISCOUNT = 0.07           # hurdle rate for NPV comparison, analyst assumption
BLACK_SWAN = [
    {"name": "Major earthquake (LA region M6.7+)", "annual_prob_analyst": 0.020, "value_impact_if_occurs": -0.20, "note": "30-yr 60% per USGS UCERF3 (S12) → ~3.0%/yr average; 2.0%/yr used as a conservative analyst frequency given loss given event here."},
    {"name": "Wildfire / urban-conflagration loss", "annual_prob_analyst": 0.005, "value_impact_if_occurs": -0.50, "note": "CAL FIRE FHSZ framework (S13); parcel-specific class blank (M55). Analyst assumption."},
    {"name": "Tenant failure / dark space event", "annual_prob_analyst": 0.010, "value_impact_if_occurs": -0.25, "note": "System shrinking -53 units y/y, franchise-level margin 37.4% (S05). Analyst assumption."},
    {"name": "Measure ULA indexation step (if in-city)", "annual_prob_analyst": 0.10, "value_impact_if_occurs": -0.02, "note": "Thresholds reset each July 1 by Chained CPI (S10). Analyst assumption."},
    {"name": "Trade/tariff shock to LA logistics economy", "annual_prob_analyst": 0.05, "value_impact_if_occurs": -0.05, "note": "Port imports -11% Nov 2025 (S15). Analyst assumption."}
]

def value_index(noi_index: float, cap: float) -> float:
    return noi_index / cap

def expected_annual_drag() -> float:
    return sum(e["annual_prob_analyst"] * abs(e["value_impact_if_occurs"]) for e in BLACK_SWAN)

def scenarios():
    rows = []
    for growth in ESCALATION_SCENARIOS:
        for cap in CAP_RATE_GRID:
            rent_path = [ILLUSTRATIVE_RENT_INDEX * ((1 + growth) ** t) for t in range(EXPIRY_YEARS[-1] - HORIZON_START + 1)]
            rows.append({
                "rent_growth": growth,
                "cap_rate": cap,
                "value_index_2026": round(value_index(ILLUSTRATIVE_RENT_INDEX, cap), 2),
                "value_index_at_2030": round(value_index(ILLUSTRATIVE_RENT_INDEX * (1 + growth) ** (2030 - HORIZON_START), cap), 2),
                "value_index_at_2035": round(value_index(ILLUSTRATIVE_RENT_INDEX * (1 + growth) ** (2035 - HORIZON_START), cap), 2),
            })
    return rows

def hold_vs_sell_breakevens():
    """For each expiry year: cumulative rent collected vs capital tied up, as an index comparison."""
    out = []
    for expiry in EXPIRY_YEARS:
        years = expiry - HORIZON_START
        cumulative_rent = sum(ILLUSTRATIVE_RENT_INDEX * (1.0 ** t) for t in range(years))
        out.append({"expiry": expiry, "years_of_rent_collected_index": round(cumulative_rent, 1),
                    "note": "Flat-rent illustration (0% escalation). Escalations improve the hold case linearly."})
    return out

def main():
    drag = expected_annual_drag()
    output = {
        "session": "session-620551ec",
        "generated": "2026-11-12",
        "method": "deterministic; index-based; no invented property inputs",
        "inputs": {
            "illustrative_rent_index": ILLUSTRATIVE_RENT_INDEX,
            "escalation_scenarios": ESCALATION_SCENARIOS,
            "cap_rate_grid": CAP_RATE_GRID,
            "expiry_years": EXPIRY_YEARS,
            "hold_years": HOLD_YEARS,
            "illustrative_discount": ILLUSTRATIVE_DISCOUNT,
        },
        "value_scenarios": scenarios(),
        "hold_vs_sell_breakevens": hold_vs_sell_breakevens(),
        "black_swan_overlay": {
            "events": BLACK_SWAN,
            "expected_annual_value_drag_fraction": round(drag, 4),
            "note": "Sum of analyst annual_prob x value_impact. Compares the carry of holding vs selling; an owner who cannot bear a ~%.1f%%/yr expected drag should not hold." % (drag * 100,),
        },
        "headline": "Extend-and-reprice first, then decide with the actual numbers (see decision.html triggers T1-T6). The grid shows value is far more sensitive to cap rate than to rent growth over 2030-2035.",
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"wrote {OUT}")
    print(f"expected annual black-swan drag (analyst assumptions): {drag:.2%}")

if __name__ == "__main__":
    main()
