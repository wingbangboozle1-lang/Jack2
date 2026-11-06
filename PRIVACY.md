# Privacy controls

Personal information is the highest-priority constraint in this project and outranks
completeness.

## Identifiers

| Entity | Reference | Stored data |
|---|---|---|
| Owner | `OWNER-01` | none — no name, entity, contact, trust, or advisor detail |
| Property | `PARCEL-01` | no street address, APN, coordinates, lot dimensions, photographs or assessor link |

The omission is deliberate and is stated as such on `/property.html`.

## What is never stored, anywhere in the repo or its history

- rent, NOI, purchase price, adjusted basis, debt, or operating statements;
- tenant identity beyond the brand name that the owner supplied;
- lease documents, estoppels, tax bills, or correspondence;
- anything derived from a private or paid source.

## Why the analysis still works

Every model result is normalised **per $1.00 of current annual NOI**. The owner can
multiply by their own NOI once and read the answer in dollars. This is the only way
to analyse an asset whose income is private without inventing a number.

## Automated enforcement

`verify.py` walks every tracked file and fails the build on:

- email addresses;
- phone numbers (public agency switchboards in cited pages are allow-listed);
- street-address patterns;
- assessor parcel-number patterns (`123-456-789`);
- latitude/longitude pairs that fall inside the Los Angeles basin.

Run `python3 verify.py` before any push.

## If personal information is discovered

Do not publish it. Record only the fact of the discovery — never the content — in
`COORDINATION.md`, remove it from the working tree, and rewrite history if it reached
a commit. The brief is explicit: anything discovered during research is for internal
use only and must not appear in the final product.
