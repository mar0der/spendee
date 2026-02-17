# Spendee (Slim Wrapper)

Python client focused on **confirmed working** Spendee integrations as of February 17, 2026.

## What This Wrapper Supports

- Login/session bootstrap:
  - Firebase token chain
  - `v3/auth/login`
  - Existing session injection via `set_session(...)`
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
