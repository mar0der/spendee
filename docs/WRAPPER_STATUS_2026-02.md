# Wrapper Status (2026-02-17)

## Confirmed Working

- Auth/session:
  - Google Identity Toolkit + Secure Token token chain
  - `POST /v3/auth/login`
  - `POST /v3/auth/logout` (returns non-JSON/empty HTML)
- REST reads:
  - `GET /v1.4/user-get-profile`
  - `POST /v1/wallet-get-all`
  - `GET /v1.6/get-all-user-categories`
  - `GET /v1.7/get-budgets` (GET only)
  - `POST /v1.8/wallet-get-transactions` (works but ordering/pagination can be non-intuitive)
- Firestore transaction path (real app behavior):
  - Create transaction via Firestore `documents:commit` write
  - Update note via Firestore `documents:commit` write+transform
  - Update category via Firestore `documents:commit` write+transform
  - Delete transaction via Firestore document delete
- Generic read/search helpers:
  - Transaction pagination helper (`wallet_get_transactions_all`)
  - Date/amount/note/type filtered search (`search_transactions`)

## Confirmed Outdated / Removed

- `v1.4/user-login` (deprecated by backend)
- `v1.5/user-registration` (deprecated by backend)
- `v1/user-check-email` (deprecated by backend)
- Legacy REST transaction write path as primary method (`v1.5/wallet-create-transaction`) for app-visible data

## Pending Verification

- Firestore list/query helper semantics for date ranges and sort parity with app UI
- Full transaction edit surface beyond category+note (amount/time)
- Any remaining bank/aggregator actions (out of scope for current objective)

## Notes

- Spendee web app transaction mutations are done via Firestore writes, not only legacy `api.spendee.com` endpoints.
- UI visibility can diverge from legacy endpoint writes; treat Firestore path as source of truth for transaction CRUD.

## Live Operations Executed (2026-02-17)

- Deleted Firestore test transaction:
  - wallet UUID: `a9b50565-d11d-4582-a3a1-820f71b272c8`
  - transaction UUID: `fdc129b7-b677-467b-9c4e-83473a146c9c`
- Located user-created transaction (`note=asdfa`, `amount=-12`) and updated note via Firestore commit:
  - transaction UUID: `944005a4-bf48-4edc-912c-241b764e9e69`
  - updated note to: `asdfa edited <time>`
- Updated same transaction category to income category `Salary` via Firestore commit:
  - transaction UUID: `944005a4-bf48-4edc-912c-241b764e9e69`
  - category UUID set to: `21fe34fe-6cb7-40ba-91e7-c9cfc760daa6`
