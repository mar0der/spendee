# Spendee API Reverse Engineering Notes (2026-02-16)

These notes document currently observed behavior from the live Spendee web app and API hosts.

## Scope

- Date checked: 2026-02-16
- Web app: `https://app.spendee.com`
- API hosts:
  - `https://api.spendee.com/`
  - `https://api2.spendee.com/`

## Runtime config observed in web app

The app injects:

- `SERVER_API_URL = https://api.spendee.com/`
- `SERVER_BANK_API_URL = https://api2.spendee.com/`
- `APP_VERSION = master`

## Auth and headers

Headers used by the web client:

- `Authorization: Bearer <token>`
- `Device-Uuid: <uuid>`
- `Spendee-Platform: web`
- `Spendee-Version: master`

Observed auth endpoints:

- `POST /v3/auth/login` (active)
- `POST /v3/auth/logout` (active)

Deprecated endpoint:

- `POST /v1.4/user-login` returns an API deprecation error.

## Endpoint inventory extracted from client bundle

`api.spendee.com` endpoints observed in JavaScript:

- `v1.3/*` (`banks-get-all`, `category-image-ids`, `currencies`, `delete-bank-login`)
- `v1.4/*` (`user-get-profile`, `wallet-create-category`, etc.)
- `v1.5/*` (transaction and transfer actions)
- `v1.6/*` (`get-transactions`, `wallet-get-transaction`, etc.)
- `v1.7/*` (budgets)
- `v1.8/*` (`wallet-get-transactions`, templates)
- `v1/*` (wallet/category and notification actions)
- `v3/auth/login`, `v3/auth/logout`

`api2.spendee.com` endpoints observed in JavaScript:

- `v2/countries`
- `v2/url?clientVersion=<...>&clientPlatform=WEB`
- `v2/logins/refresh?clientVersion=<...>&clientPlatform=WEB`
- `v2/visible`
- `v2/destroyCredentials`

## Live probe highlights

Unauthenticated success:

- `GET https://api.spendee.com/v1.3/currencies`
- `POST https://api2.spendee.com/v2/countries`

Auth-required (return unauthorized without valid token):

- `POST /v1/wallet-get-all`
- `POST /v1.8/wallet-get-transactions`
- `POST /v1.7/get-budgets`
- `POST /v1/notification-get-all`
- `POST /v3/auth/login` (returns HTTP 401 without valid bearer token)

## Notes for maintainers

- Keep login flow aligned with current Firebase/Google token behavior and `v3/auth/login`.
- Validate endpoints periodically; this API is unofficial and may change without notice.
