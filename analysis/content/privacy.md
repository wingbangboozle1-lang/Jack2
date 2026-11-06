# Privacy

## The rule

Personal information is the highest-priority constraint in this project. It outranks completeness, and it outranks convenience.

## What was done

| Control | Implementation |
|---|---|
| Identity removed at intake | The owner is referred to only as `OWNER-01`. No name, initials, contact detail, entity name or trust name is stored. |
| Property de-identified | The asset is `PARCEL-01`. No street address, APN, assessor link, coordinate, lot dimension or photograph is stored — including in git history. |
| No reverse-engineering | No figure was derived from an address, a parcel record, a title document or a personal record. All market data is aggregate and public. |
| No private sources | Nothing was obtained from a paid data service, a broker's private comp set, a title company or a personal file. |
| No financial disclosure | Rent, NOI, purchase price, adjusted basis and debt are absent from the dataset and from every page. The model is normalised to $1.00 of NOI precisely so that no dollar figure need be published. |
| Publication-safe | The entire site can be read by a stranger without revealing who the owner is or which corner the building sits on. |

## Where personal data could still leak, and what is done about it

1. **The lease document** contains names and rent. It is not in this repository and should not be committed to it. Gate G1 requires it for analysis; it does not require it to be published.
2. **The file name** of any uploaded statement or tax bill can itself identify a person. Files are not stored here at all.
3. **The git history** is public once pushed. Nothing was committed before de-identification, and no scratch file containing identifiers was ever created in the repository.
4. **A future session** could add an address in good faith. The build script's source check does not catch that, so `PRIVACY.md` and `COORDINATION.md` carry the instruction explicitly, and the Property page states the omission as deliberate.

## If personal information is discovered

Do not publish it. Record only the fact of the discovery — never the content — in `COORDINATION.md`, remove it from any file, and rewrite history if it reached a commit. The task brief is explicit that anything discovered during research is for internal use only and must not appear in the final product.

## What this costs the analysis

It costs precision, and that cost is stated rather than hidden:

- No trade-area (1/3/5-mile) demographics, only city and county aggregates.
- No parcel-level zoning, entitlement or assessed-value data.
- No rent or NOI, so every result is a multiple of NOI rather than a dollar figure.
- No after-tax comparison, because adjusted basis is unknown.

Each of these is flagged on the site as a known limitation. None of them changes the direction of the recommendation, which turns on a 130 bp yield gap and a 19–40% tenant-default probability — both of which are measurable without knowing the address.
