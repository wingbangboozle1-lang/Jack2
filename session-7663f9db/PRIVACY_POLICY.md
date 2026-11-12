# Privacy & Anonymization Policy — Session P (`session-7663f9db`)

**Classification:** Strict zero-PII public static dashboard. Internal private asset facts are represented strictly via anonymized placeholders (`Subject Property (Central Los Angeles)`, `[REDACTED-ADDRESS]`, `[REDACTED-APN]`, `[REDACTED-OWNER]`, `[REDACTED-LEASE-ID]`).

## Hard Privacy Rules Enforced
1. **No personal or parcel identifiers anywhere in Git or on the published site:** Zero owner names, LLC/trust names, street addresses, APNs, tax account numbers, phone numbers, email addresses, Social Security / EIN numbers, bank/loan account numbers, or tenant/franchisee contact details.
2. **Internal-only handling of supplied confidential records:** Any lease document, rent roll, operating reconciliation, appraisal, tax return, or loan statement supplied privately stays strictly offline in owner/advisor workrooms and is never uploaded to GitHub or rendered in static HTML. Any interactive calculators on the dashboard execute 100% locally in browser memory with zero network transmission.
3. **Public-agency street address flag:** An earlier research file in the shared repository (`research/04-education.md`, line 11) records the public headquarters street address of LAUSD on Beaudry. While public, it triggers automated street-address PII scanners. Session P flags it in `flagged.html` without reproducing any street address anywhere inside `session-7663f9db/`.
4. **Automated gate:** `session-7663f9db/scripts/verify.py` scans every HTML, CSS, JS, JSON, Markdown, and Python file in `session-7663f9db/` and exits non-zero if any email, SSN, phone, APN, or street-address regex pattern matches.
