# Spendee (Slim Wrapper)

Python client focused on **confirmed working** Spendee integrations as of February 17, 2026.

## What This Wrapper Supports

- Login/session bootstrap:
  - Firebase token chain
  - `v3/auth/login`
  - Existing session injection via `set_session(...)`
  - Browser-assisted token bootstrap (Apple/Google SSO friendly)
  - Automatic refresh-token persistence (Linux-friendly)
- Confirmed REST reads:
  - User profile
  - Wallet list
  - Categories
  - Budgets (GET)
  - Legacy transaction list endpoint
- Firestore transaction CRUD (real app path):
  - Create transaction
  - Update transaction note
  - Delete transaction
  - Fetch transaction document

## Why Slim

The previous wrapper included many endpoints that are deprecated or unverified against current app behavior. This version keeps only confirmed paths and removes known outdated surface area.

## Install

1. Python 3.8+
2. `pip install spendee`

## Credential Persistence (Linux/OpenClaw)

- Password is only needed once to bootstrap.
- Wrapper stores:
  - `refresh_token`
  - `device_uuid`
  - `email`
- Default path:
  - `~/.config/spendee/credentials.json`
- File mode is set to `600`.
- On next runs, wrapper uses stored `refresh_token` to mint fresh access tokens automatically.

## Apple/Google Sign-In (No Password)

Use browser-assisted bootstrap:

1. Open [https://app.spendee.com](https://app.spendee.com) and sign in with Apple/Google.
2. In browser DevTools Network, copy:
   - `Authorization` header value (`Bearer ...`)
   - `device-uuid` header value
   - Optional but recommended: Firebase `refreshToken` if available
3. Call `bootstrap_from_browser(...)` once.
4. Wrapper persists credentials for next OpenClaw runs.
5. If needed, print built-in user instructions:
   - `Spendee.print_browser_bootstrap_instructions()`

## Verification Matrix

See:

- `docs/WRAPPER_STATUS_2026-02.md`
- `docs/REVERSE_ENGINEERING_2026-02.md`
- `docs/ENDPOINT_DELTA_2026-02.md`

## Example (session-based)

```python
from spendee import Spendee
from decimal import Decimal

client = Spendee(email="", password="")
client.set_session(access_token="<bearer>", device_uuid="<device-uuid>")

profile = client.user_get_profile()
wallets = client.wallet_get_all()
wallet_map = client.wallet_uuid_map()
```

## Example (password once, then auto-refresh)

```python
from spendee import Spendee

# First run: provide password once
client = Spendee(email="you@example.com", password="your_password")
client.user_login(timezone_id="Asia/Dubai", global_currency="AED")

# Next runs: no password needed, refresh token is loaded from ~/.config/spendee/credentials.json
client2 = Spendee(email="you@example.com")
profile = client2.user_get_profile()
```

## Example (browser-assisted bootstrap for SSO)

```python
from spendee import Spendee

client = Spendee(email="you@example.com")
client.bootstrap_from_browser(
    authorization="Bearer <copied-bearer>",
    device_uuid="<copied-device-uuid>",
    refresh_token="<optional-refresh-token>",
)

profile = client.user_get_profile()
```

## Example (LLM/helper prompt output)

```python
from spendee import Spendee

instructions = Spendee.get_browser_bootstrap_instructions()
print(instructions)
```
