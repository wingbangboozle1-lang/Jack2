# Shared task board

## Active session and branch policy

- Session ID: `50002478` (Arena agent session).
- Work branch: `arena/50002478-jack2`. Arena requires all work, commits, and pushes to remain on this fixed session branch; no alternate session branches will be created.
- Initial repository inspection: only `README.md` (two lines: a project heading and a blank line). No existing application, datasets, lease, offering memorandum, property identifier, or personal-information records were present.
- Privacy: public outputs use `[PROPERTY]`, `[OWNER]`, and other nonidentifying placeholders. Do not add addresses, parcel numbers, names, contacts, account data, or identifying financial documents to the repository or website.
- This session is responsible for research, implementation, and final integration sequentially. No other claims were present when work began. Check this board before each push; do not overwrite another session's work.

## Claims

| Task | Status | Owner | Files / scope |
|---|---|---|---|
| T01 — Official-source research register | in progress | 50002478 | `data/research.json`, `research/` |
| T02 — Scenario methodology and risk analysis | in progress | 50002478 | `data/analysis.json`, `scripts/model.mjs`, `tests/model.test.mjs` |
| T03 — Accessible dashboard and category pages | in progress | 50002478 | `site/`, `scripts/build.mjs`, `package.json`, `package-lock.json` |
| T04 — Verification and privacy checks | in progress | 50002478 | `scripts/verify.mjs`, `tests/verify.test.mjs`, `reports/` |
| T05 — Final integration, pull request, Pages deployment | in progress | 50002478 | `README.md`, `.github/workflows/`, `index.html`, `COORDINATION.md`, generated `dist/` (not tracked) |

All scopes were unclaimed at initial inspection. Shared index/navigation is generated only during T05 after data and verification checks. The user requested autonomous completion; no manual-input gate is used. Missing facts remain blank and are flagged, not guessed.

## Work and verification log

- Claimed T01–T05 for session `50002478`; initial source control state was clean at `1430b4f`.
- Repository review: `README.md:1` contains `# Jack2`; `README.md:2` is blank. No factual claims or personal information to verify or redact.
- Research rule: official-government, official-company SEC, or issuing-agency sources only. Regional statistics are context, not evidence of the subject property's performance or precise location. Historical observations and analytical assumptions must be labeled separately.
- No lease, rent roll, sale price, exact expiration date, tenant options, parcel, or financial records supplied. These fields will remain unverified in public outputs.

## Completion record

Pending: source verification, deterministic model tests, build and link validation, privacy audit, integration PR, merge, and live Pages verification.
