# Privacy Policy & Zero-PII Data Protection Standard

**Workspace:** `session-24d6cd5f` (Central Los Angeles Jack in the Box NNN Decision Support Workbook)  
**Effective Date:** 2026-11-08

## 1. Non-Exposure of Personal and Parcel-Identifying Information

This repository and its published static web dashboard strictly prohibit committing, storing, or displaying any Personal Information (PI) or parcel-identifying data, including:

- **No Street Addresses or Parcel Identifiers:** No street number, street name, Assessor's Parcel Number (APN), tract/lot legal description, latitude/longitude coordinates, or 1-mile/3-mile census-tract lookup that could reverse-identify `[REDACTED-PROPERTY-01]`.
- **No Party Names or Contact Information:** No property owner names, entity LLCs, franchisee names, lender names, email addresses, telephone numbers, or personal tax identifiers.
- **No Private Contract Terms:** Private annual rent / NOI, exact day/month lease expiration date within the 2030–2035 window, purchase basis, accumulated depreciation, loan balance, or store-level unit sales are omitted from all verified data files and left strictly blank (`""`) in public tables until entered locally by the user.

## 2. 100% Client-Side Execution Guarantee (Interactive Simulator)

All interactive tools on `projection-model.html` execute **exclusively inside the visitor's local browser memory**:

- **Zero Backend Transmission:** No `fetch()`, `XMLHttpRequest`, `navigator.sendBeacon()`, WebSocket, form submission, or external CDN call is executed anywhere on the site.
- **Zero Persistence or Tracking:** No cookies, `localStorage`, `sessionStorage`, analytics beacons, third-party fonts, or tracking pixels are used. Private inputs entered into the browser calculator disappear immediately when the tab closes or when the Reset button is clicked.
- **Public Verification Parity:** All static model projections normalize outcomes per `$100,000` of current annual NNN Net Operating Income (NOI), allowing rigorous strategy ranking without exposing private dollar amounts.

## 3. Automated PII & Link Enforcement

Every build runs `session-24d6cd5f/scripts/verify.py` and the repository-wide `tools/check_site.py` regex scanner prior to commit and via GitHub Actions CI, blocking deployment if any email, telephone sequence, street-address pattern, APN pattern, `http://` external link, or localhost reference appears in any data file, document, or HTML page.
