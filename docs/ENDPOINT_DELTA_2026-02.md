# Endpoint Delta (Wrapper vs Live Web API)

Date: 2026-02-16

## Summary

- Wrapper-defined endpoints: 27
- Endpoints extracted from current web bundle: 74
- Wrapper endpoint not seen in web bundle: `v2/providers`
- New/observed endpoints not implemented in wrapper: 48 (see below)

## Key changed/deprecated points

- `v1.4/user-login` is deprecated (`410`, "The endpoint version is no longer supported.")
- `v3/auth/login` and `v3/auth/logout` are active auth endpoints used by web client.
- `v2/providers` is not present in current web bundle.
- `v2/destroyCredentials` is present in current web bundle.
- `v1.5/user-registration` appears deprecated (`410`).
- `v1/user-check-email` appears deprecated (`410`).

## Probe notes (without user auth)

- Many `api.spendee.com` endpoints return HTTP `200` with JSON `status=ERROR`, service `api.unauthorized`, and message `Not found` when unauthenticated.
- `v2/*` aggregator endpoints generally return HTTP `401` when unauthenticated.
- Public examples:
  - `GET /v1.3/currencies` -> success
  - `POST /v2/countries` -> success

## Web-observed endpoints not currently implemented in wrapper

```text
v1.3/currencies
v1.3/delete-bank-login
v1.4/confirm-deletion
v1.4/confirm-email-change
v1.4/merge-categories
v1.4/recommendation-likelihood
v1.4/request-deletion
v1.4/request-email-change
v1.4/user-forgot-password
v1.4/user-get-profiles
v1.4/user-login
v1.4/user-logout
v1.4/user-password-change-confirmation
v1.4/wallet-create-category
v1.4/wallet-get-categories
v1.4/wallet-update-category
v1.5/change-to-two-way-transfer
v1.5/delete-transfer-transaction
v1.5/link-two-transactions-into-transfer
v1.5/revert-transfer-to-regular-transaction
v1.5/transaction-suggestions
v1.5/update-transfer
v1.5/user-fb-connect
v1.5/user-google-connect
v1.5/user-registration
v1.5/viewed-dialogs
v1.5/wallet-delete-transaction
v1.5/wallet-update-transaction
v1.6/get-transactions
v1.6/iframe-wallet-data
v1.6/reorder-wallets
v1.6/wallet-get-transaction
v1.7/reorder-budgets
v1.8/create-transaction-template
v1.8/delete-transaction-template
v1.8/wallet-get-transactions
v1/exchange-rate
v1/notification-count-unread
v1/notification-get-all
v1/notification-set
v1/user-check-email
v1/user-set-subscription
v1/wallet-accept-sharing
v1/wallet-get
v1/wallet-get-category
v1/wallet-get-users
v1/wallet-order-categories
v2/destroyCredentials
```

## Authenticated validation needed

To confirm payload schemas and methods for auth-gated routes, run tests with valid:

- `Authorization` bearer token
- `Device-Uuid`

This will allow us to replace "unauthorized but routable" assumptions with exact request/response contracts.
