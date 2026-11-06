# Privacy & Redaction Protocol (`PRIVACY_POLICY.md`)

**Priority Level:** Top Priority / Highest Urgency  
**Applies To:** All repository files, JSON datasets, analytical scripts, Markdown reports, Pull Request descriptions, and published GitHub Pages HTML/CSS/JS assets.

---

## 1. Mandatory Anonymization Rules

1. **Zero Personal Information on Website or Public Data:** No personal names of property owners, investors, family members, trustees, private lease signatories, residential addresses, personal email addresses, phone numbers, Social Security Numbers (SSNs), Taxpayer Identification Numbers (TINs) of individuals, financial account numbers, or Assessor Parcel Numbers (APNs) identifying the private owner may appear anywhere in the final website product or repository datasets.
2. **Standardized Placeholders:**
   - Individual Investor / Property Owner: `[REDACTED-OWNER-01]`
   - Subject Commercial Real Estate Parcel: `[REDACTED-PROPERTY-01]`
   - Street Address / Legal Description / APN: `[REDACTED-PARCEL-ID]`
   - Private Lease Instrument / Signatory: `[REDACTED-LEASE-01]`
   - Commit Metadata Email Discovered During Audit: `[REDACTED-EMAIL-01]`
3. **Internal-Only Audit Finding Handling:** During line-by-line review of initial commit `1430b4f`, git commit header metadata was observed to contain a personal email address rather than a GitHub `noreply` address. Per strict privacy policy, that string is treated as internal-only, excluded from every data file and web page, referenced solely as `[REDACTED-EMAIL-01]` in the repository audit log, and blocked by an automated build-time PII regex and blocklist check in `scripts/verify_all.py`.
4. **Client-Side Only Interactive Calculator:** The interactive Property & 1031 Decision Simulator on `projections-decisions.html` executes 100% locally in the user's browser memory with zero network transmissions, zero cookies, zero `localStorage` persistence, and zero third-party analytics scripts.
