# Second model — independent hold/sell analysis (session `ffe3bdfd`)

This folder is a **self-contained, independently built** second analysis of the same
decision: a Jack in the Box NNN lease in Central Los Angeles, expiring 2030–2035.

It exists because two sessions worked the same problem without seeing each other.
Rather than overwrite either result, the repository keeps both: the root site is
Session B's build, Session A's site is archived under `session-1944e5a3/`, and this
folder is Session C's build. Each has its own data, model, verifier and pages, and
none of the three can silently change another's numbers.

## What is different here

| | Root site (Session B) | This folder (Session C) |
|---|---|---|
| Unit of account | dollars, from a benchmark rent assumption | **per $1.00 of NOI** — no rent is assumed |
| Model | 2026–2040 deterministic + breakevens | 20,000-path Monte Carlo, 3 expiry cases, seeded |
| Headline | sequence: extend at a reset, price 2027–28 | **sell now, §1031 into diversified net lease** |
| Margin | thin (~$247k on ~$5.9M of 2040 wealth) | wide (33.26 vs 26.70 per $1 NOI) |
| Tax | modelled with assumed basis | mechanics verified, **no after-tax number claimed** |

The direction agrees: redeploying beats holding. The magnitude does not, and the
gap is worth reading rather than hiding — it comes from the exit cap and the cost of
the rollover year. `projection.html` in this folder publishes the break-even exit
cap (~4.7%) so the disagreement can be tested rather than argued.

## Files

```
build.py            generates the pages in this folder and validates the data
verify.py           data / link / privacy / HTML gates
model/projection.py 20,000-path Monte Carlo (seed 20261106)
data/*.json         112 rows + sources + model output + decision record
content/*.md        narrative
*.html              the generated site (open index.html)
```

No external dependencies. To rebuild:

```bash
cd analysis
python3 model/projection.py && python3 build.py && python3 verify.py
```

## Privacy

Owner is `OWNER-01`, property is `PARCEL-01`. No address, APN, coordinate, rent,
NOI, basis or identity appears in this folder, its data, or its git history.
`verify.py` enforces that mechanically. See `PRIVACY.md`.
