from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from requests import Session
from requests.exceptions import RequestException

from .exceptions import SpendeeError


class Spendee(Session):
    """
    Slim Spendee client containing only confirmed working paths.

    Confirmed API hosts:
    - https://api.spendee.com/ (legacy REST reads + auth bootstrap)
    - https://firestore.googleapis.com/ (real app transaction writes)
    """
    WEB_LOGIN_URL = "https://app.spendee.com"
    BROWSER_BOOTSTRAP_INSTRUCTIONS = """Spendee browser bootstrap (Apple/Google SSO):

1. Open {web_login_url} and sign in.
2. Open browser DevTools:
   - Chrome: Cmd+Option+I (macOS) or Ctrl+Shift+I (Linux/Windows)
3. Go to Network tab.
4. Filter requests by: api.spendee.com
5. Click request: user-get-profile (or any /v1.4/... API request).
6. In Request Headers, copy:
   - Authorization: Bearer ...
   - device-uuid: ...
7. (Optional, recommended) capture Firebase refreshToken if available.
8. Pass values to wrapper:
   client.bootstrap_from_browser(
       authorization="Bearer <token>",
       device_uuid="<device-uuid>",
       refresh_token="<optional-refresh-token>",
       email="<optional-email>",
   )
"""

    def __init__(
        self,
        email: str = "",
        password: Optional[str] = None,
        base_url: str = "https://api.spendee.com/",
        firestore_project: str = "spendee-app",
        google_client_id: str = "AIzaSyCCJPDxVNVFEARQ-LxH7q2aZtdQJGGFO84",
        access_token: Optional[str] = None,
        device_uuid: Optional[str] = None,
        refresh_token: Optional[str] = None,
        credential_store_path: Optional[str] = None,
        persist_credentials: bool = True,
    ):
        self.base_url = base_url
        self.firestore_project = firestore_project
        self._email = email
        self._password = password
        self._google_client_id = google_client_id
        self._access_token = access_token
        self._device_uuid = device_uuid
        self._refresh_token = refresh_token
        self._persist_credentials = persist_credentials
        self._credential_store_path = Path(credential_store_path).expanduser() if credential_store_path else self._default_credential_store_path()
        super().__init__()
        self._load_credentials()

    def set_session(self, access_token: str, device_uuid: Optional[str] = None) -> None:
        self._access_token = access_token
        self._device_uuid = device_uuid
        self._save_credentials()

    @staticmethod
    def parse_bearer(authorization: str) -> str:
        value = (authorization or "").strip()
        if not value:
            raise SpendeeError("Missing Authorization value.")
        if value.lower().startswith("bearer "):
            token = value[7:].strip()
            if not token:
                raise SpendeeError("Bearer token is empty.")
            return token
        return value

    def bootstrap_from_browser(
        self,
        authorization: str,
        device_uuid: str,
        refresh_token: Optional[str] = None,
        email: Optional[str] = None,
    ) -> None:
        self._access_token = self.parse_bearer(authorization)
        self._device_uuid = device_uuid.strip()
        if not self._device_uuid:
            raise SpendeeError("Missing device_uuid.")
        if refresh_token:
            self._refresh_token = refresh_token.strip()
        if email:
            self._email = email.strip()
        self._save_credentials()

    @classmethod
    def get_browser_bootstrap_instructions(cls) -> str:
        return cls.BROWSER_BOOTSTRAP_INSTRUCTIONS.format(web_login_url=cls.WEB_LOGIN_URL).strip()

    @classmethod
    def print_browser_bootstrap_instructions(cls) -> None:
        print(cls.get_browser_bootstrap_instructions())

    @staticmethod
    def _default_credential_store_path() -> Path:
        return Path.home() / ".config" / "spendee" / "credentials.json"

    def _load_credentials(self) -> None:
        if not self._persist_credentials:
            return
        if not self._credential_store_path.exists():
            return

        try:
            raw = self._credential_store_path.read_text()
            data = json.loads(raw)
        except Exception:
            return

        stored_email = data.get("email") or ""
        if self._email and stored_email and self._email != stored_email:
            return

        if not self._email and stored_email:
            self._email = stored_email

        if not self._refresh_token:
            self._refresh_token = data.get("refresh_token")
        if not self._device_uuid:
            self._device_uuid = data.get("device_uuid")

    def _save_credentials(self) -> None:
        if not self._persist_credentials:
            return
        if not self._refresh_token and not self._device_uuid:
            return

        self._credential_store_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "email": self._email,
            "refresh_token": self._refresh_token,
            "device_uuid": self._device_uuid,
        }
        self._credential_store_path.write_text(json.dumps(payload))
        os.chmod(self._credential_store_path, 0o600)

    def _build_url(self, version: str, endpoint: str) -> str:
        if endpoint.startswith("http"):
            return endpoint
        return f"{self.base_url}{version}/{endpoint}"

    def _headers(self, include_auth: bool = True) -> Dict[str, str]:
        headers = {
            "Spendee-Platform": "web",
            "Spendee-Version": "master",
        }
        if include_auth and self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"
        if include_auth and self._device_uuid:
            headers["Device-Uuid"] = self._device_uuid
        return headers

    def _raw_request(self, method: str, url: str, **kwargs):
        return Session.request(self, method=method, url=url, **kwargs)

    def request(self, method: str, url: str, version: str = "v1", headers=None, params=None, **kwargs):
        if params is None:
            params = {
                "clientVersion": "master",
                "clientPlatform": "WEB",
            }
        if headers is None:
            headers = self._headers(include_auth=True)

        if not self._access_token and "googleapis" not in url:
            self.user_login()
            headers = self._headers(include_auth=True)

        target = self._build_url(version, url)

        response = None
        try:
            response = super().request(method=method, url=target, headers=headers, params=params, **kwargs)
            if response.status_code == 401 and "auth/login" not in target:
                self._access_token = None
                self.user_login()
                headers = self._headers(include_auth=True)
                response = super().request(method=method, url=target, headers=headers, params=params, **kwargs)
            response.raise_for_status()
        except RequestException as exc:
            raise SpendeeError("Spendee returned a non-200 HTTP code.", response=response) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise SpendeeError("Response can't be serialized", response=response) from exc

        if isinstance(payload, dict) and payload.get("status") not in (None, "SUCCESS"):
            message = payload.get("error", {}).get("message") or payload.get("message") or "Unexpected error on the Spendee side"
            raise SpendeeError(message, response=response)

        return payload.get("result") if isinstance(payload, dict) and "result" in payload else payload

    # --------- Auth (confirmed) ---------

    def _get_refresh_token(self, email: Optional[str] = None, password: Optional[str] = None) -> str:
        user_email = email or self._email
        user_password = password or self._password
        if not user_email or not user_password:
            raise SpendeeError("Missing email/password and no stored refresh token available.")

        body = {
            "email": user_email,
            "password": user_password,
            "returnSecureToken": True,
        }
        url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={self._google_client_id}"
        response = self._raw_request("POST", url=url, json=body)
        response.raise_for_status()
        return response.json()["refreshToken"]

    def _get_access_token(self, refresh_token: str) -> str:
        body = {
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        url = f"https://securetoken.googleapis.com/v1/token?key={self._google_client_id}"
        response = self._raw_request("POST", url=url, json=body)
        response.raise_for_status()
        return response.json()["access_token"]

    def user_login(self, timezone_id: str = "Asia/Dubai", global_currency: str = "AED") -> Dict[str, Any]:
        if not self._refresh_token:
            self._refresh_token = self._get_refresh_token()
            self._save_credentials()
        self._access_token = self._get_access_token(self._refresh_token)

        payload = {
            "global_currency": global_currency,
            "default_wallet_name": "Cash Wallet",
            "timezone": timezone_id,
            "platform": "web",
            "version": "master",
            "credential": None,
        }
        result = self.post(url="auth/login", version="v3", json=payload)
        if isinstance(result, dict) and result.get("device_uuid"):
            self._device_uuid = result["device_uuid"]
        self._save_credentials()
        return result

    def user_logout(self):
        result = self.post(url="auth/logout", version="v3", json={})
        self._access_token = None
        return result

    # --------- Legacy REST reads (confirmed) ---------

    def user_get_profile(self):
        return self.get(url="user-get-profile", version="v1.4")

    def wallet_get_all(self):
        return self.post(url="wallet-get-all", version="v1", json={})

    def get_all_user_categories(self):
        return self.get(url="get-all-user-categories", version="v1.6")

    def list_categories(
        self,
        category_type: Optional[str] = None,
        wallet_uuid: Optional[str] = None,
        active_only: bool = True,
    ) -> List[Dict[str, Any]]:
        categories = self.get_all_user_categories()
        filtered: List[Dict[str, Any]] = []

        for category in categories:
            if active_only and category.get("status") != "active":
                continue
            if category_type and category.get("type") != category_type:
                continue

            if wallet_uuid:
                settings = category.get("wallets_settings") or []
                if settings:
                    visible = any(
                        setting.get("wallet_uuid") == wallet_uuid and setting.get("visible") in (1, True)
                        for setting in settings
                    )
                    if not visible:
                        continue

            filtered.append(category)

        return filtered

    def get_budgets(self):
        # Confirmed: GET works, POST returns 405.
        return self.get(url="get-budgets", version="v1.7")

    def wallet_get_transactions(self, wallet_id: Optional[int] = None, offset: int = 0, limit: int = 100):
        payload: Dict[str, Any] = {"offset": offset, "limit": limit}
        if wallet_id is not None:
            payload["wallet_id"] = wallet_id
        return self.post(url="wallet-get-transactions", version="v1.8", json=payload)

    @staticmethod
    def _parse_transaction_datetime(value: Optional[str], offset: Optional[str]) -> Optional[datetime]:
        if not value:
            return None

        parsed: Optional[datetime] = None
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                parsed = datetime.strptime(value, fmt)
                break
            except ValueError:
                continue
        if parsed is None:
            return None

        if offset and len(offset) == 6 and offset[0] in ("+", "-") and offset[3] == ":":
            sign = 1 if offset[0] == "+" else -1
            try:
                hours = int(offset[1:3])
                minutes = int(offset[4:6])
                tz = timezone(sign * timedelta(hours=hours, minutes=minutes))
                return parsed.replace(tzinfo=tz)
            except ValueError:
                pass

        return parsed.replace(tzinfo=timezone.utc)

    @staticmethod
    def _decimal_from_any(value: Any) -> Optional[Decimal]:
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except Exception:
            return None

    def wallet_get_transactions_all(
        self,
        wallet_id: int,
        *,
        page_limit: int = 100,
        max_pages: int = 20,
        stop_before: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        transactions: List[Dict[str, Any]] = []
        offset = 0

        for _ in range(max_pages):
            page = self.wallet_get_transactions(wallet_id=wallet_id, offset=offset, limit=page_limit) or []
            if not page:
                break
            transactions.extend(page)

            if stop_before is not None:
                oldest: Optional[datetime] = None
                for tx in page:
                    tx_dt = self._parse_transaction_datetime(tx.get("start_date"), tx.get("offset"))
                    if tx_dt is None:
                        continue
                    if oldest is None or tx_dt < oldest:
                        oldest = tx_dt
                if oldest is not None and oldest <= stop_before:
                    break

            if len(page) < page_limit:
                break
            offset += len(page)

        return transactions

    def search_transactions(
        self,
        *,
        wallet_id: int,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        amount: Optional[Decimal] = None,
        amount_tolerance: Decimal = Decimal("0.01"),
        note_query: Optional[str] = None,
        type_filter: Optional[str] = None,
        include_pending: Optional[bool] = None,
        page_limit: int = 100,
        max_pages: int = 20,
    ) -> List[Dict[str, Any]]:
        stop_before = start - timedelta(days=2) if start is not None else None
        rows = self.wallet_get_transactions_all(
            wallet_id=wallet_id,
            page_limit=page_limit,
            max_pages=max_pages,
            stop_before=stop_before,
        )

        note_query_norm = (note_query or "").strip().lower()
        results: List[Dict[str, Any]] = []
        for tx in rows:
            tx_dt = self._parse_transaction_datetime(tx.get("start_date"), tx.get("offset"))
            if start is not None:
                if tx_dt is None or tx_dt < start:
                    continue
            if end is not None:
                if tx_dt is None or tx_dt > end:
                    continue

            if amount is not None:
                tx_amount = self._decimal_from_any(tx.get("amount"))
                if tx_amount is None:
                    continue
                if abs(tx_amount - amount) > amount_tolerance:
                    continue

            if type_filter:
                if str(tx.get("type", "")).upper() != type_filter.upper():
                    continue

            if include_pending is not None:
                tx_pending = bool(tx.get("is_pending"))
                if tx_pending != include_pending:
                    continue

            if note_query_norm:
                note = str(tx.get("note") or "").lower()
                description = str(tx.get("description") or "").lower()
                if note_query_norm not in note and note_query_norm not in description:
                    continue

            results.append(tx)

        return results

    # --------- Firestore helpers (confirmed app path) ---------

    def _firestore_doc_url(self, doc_path: str) -> str:
        return f"https://firestore.googleapis.com/v1/{doc_path}"

    def _firestore_commit_url(self) -> str:
        return f"https://firestore.googleapis.com/v1/projects/{self.firestore_project}/databases/(default)/documents:commit"

    def _firestore_headers(self) -> Dict[str, str]:
        if not self._access_token:
            self.user_login()
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def _format_utc_timestamp(value: datetime) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        value = value.astimezone(timezone.utc)
        return value.strftime("%Y-%m-%dT%H:%M:%S.000000000Z")

    @staticmethod
    def _decimal_str(value: Decimal) -> str:
        return format(value.normalize(), "f")

    def wallet_uuid_map(self) -> Dict[int, str]:
        wallets = self.wallet_get_all()
        return {int(wallet["id"]): wallet["uuid"] for wallet in wallets if wallet.get("id") and wallet.get("uuid")}

    def category_uuid_for_wallet(self, wallet_uuid: str, category_type: str = "expense") -> Optional[str]:
        categories = self.get_all_user_categories()
        for category in categories:
            if category.get("status") != "active":
                continue
            if category.get("type") != category_type:
                continue
            settings = category.get("wallets_settings") or []
            if not settings:
                return category.get("uuid")
            for setting in settings:
                if setting.get("wallet_uuid") == wallet_uuid and setting.get("visible") in (1, True):
                    return category.get("uuid")
        return None

    def get_transaction_firestore(self, user_uuid: str, wallet_uuid: str, transaction_uuid: str) -> Dict[str, Any]:
        doc_path = f"projects/{self.firestore_project}/databases/(default)/documents/users/{user_uuid}/wallets/{wallet_uuid}/transactions/{transaction_uuid}"
        response = self._raw_request("GET", self._firestore_doc_url(doc_path), headers=self._firestore_headers())
        response.raise_for_status()
        return response.json()

    def delete_transaction_firestore(self, user_uuid: str, wallet_uuid: str, transaction_uuid: str) -> bool:
        doc_path = f"projects/{self.firestore_project}/databases/(default)/documents/users/{user_uuid}/wallets/{wallet_uuid}/transactions/{transaction_uuid}"
        response = self._raw_request("DELETE", self._firestore_doc_url(doc_path), headers=self._firestore_headers())
        response.raise_for_status()
        return True

    def create_transaction_firestore(
        self,
        user_uuid: str,
        wallet_uuid: str,
        category_uuid: str,
        amount: Decimal,
        note: str,
        made_at: Optional[datetime] = None,
        made_at_timezone: str = "Asia/Dubai",
        made_at_timezone_offset: int = 14400,
        exchange_rate: Decimal = Decimal("0.27229408"),
    ) -> Dict[str, Any]:
        if made_at is None:
            made_at = datetime.now(timezone.utc)

        tx_uuid = str(uuid4())
        doc_path = (
            f"projects/{self.firestore_project}/databases/(default)/documents/"
            f"users/{user_uuid}/wallets/{wallet_uuid}/transactions/{tx_uuid}"
        )

        usd_amount = (amount * exchange_rate).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)

        payload = {
            "writes": [
                {
                    "update": {
                        "name": doc_path,
                        "fields": {
                            "note": {"stringValue": note},
                            "type": {"stringValue": "regular"},
                            "category": {"stringValue": category_uuid},
                            "modelVersion": {"integerValue": "1"},
                            "madeAtTimezone": {"stringValue": made_at_timezone},
                            "madeAtTimezoneOffset": {"integerValue": str(made_at_timezone_offset)},
                            "madeAt": {"timestampValue": self._format_utc_timestamp(made_at)},
                            "amount": {"stringValue": self._decimal_str(amount)},
                            "usdValue": {
                                "mapValue": {
                                    "fields": {
                                        "exchangeRate": {"stringValue": self._decimal_str(exchange_rate)},
                                        "amount": {"stringValue": self._decimal_str(usd_amount)},
                                    }
                                }
                            },
                            "path": {
                                "mapValue": {
                                    "fields": {
                                        "user": {"stringValue": user_uuid},
                                        "wallet": {"stringValue": wallet_uuid},
                                        "transaction": {"stringValue": tx_uuid},
                                    }
                                }
                            },
                            "author": {"stringValue": user_uuid},
                        },
                    }
                },
                {
                    "transform": {
                        "document": doc_path,
                        "fieldTransforms": [
                            {"fieldPath": "updatedAt", "setToServerValue": "REQUEST_TIME"}
                        ],
                    },
                    "currentDocument": {"exists": True},
                },
            ]
        }

        response = self._raw_request("POST", self._firestore_commit_url(), headers=self._firestore_headers(), json=payload)
        response.raise_for_status()
        return {
            "transaction_uuid": tx_uuid,
            "commit": response.json(),
            "document_path": doc_path,
        }

    def update_transaction_note_firestore(
        self,
        user_uuid: str,
        wallet_uuid: str,
        transaction_uuid: str,
        note: str,
    ) -> Dict[str, Any]:
        doc_path = (
            f"projects/{self.firestore_project}/databases/(default)/documents/"
            f"users/{user_uuid}/wallets/{wallet_uuid}/transactions/{transaction_uuid}"
        )

        payload = {
            "writes": [
                {
                    "update": {
                        "name": doc_path,
                        "fields": {
                            "note": {"stringValue": note},
                        },
                    },
                    "updateMask": {"fieldPaths": ["note"]},
                    "currentDocument": {"exists": True},
                },
                {
                    "transform": {
                        "document": doc_path,
                        "fieldTransforms": [
                            {"fieldPath": "updatedAt", "setToServerValue": "REQUEST_TIME"}
                        ],
                    },
                    "currentDocument": {"exists": True},
                },
            ]
        }

        response = self._raw_request("POST", self._firestore_commit_url(), headers=self._firestore_headers(), json=payload)
        response.raise_for_status()
        return response.json()

    def update_transaction_category_firestore(
        self,
        user_uuid: str,
        wallet_uuid: str,
        transaction_uuid: str,
        category_uuid: str,
    ) -> Dict[str, Any]:
        doc_path = (
            f"projects/{self.firestore_project}/databases/(default)/documents/"
            f"users/{user_uuid}/wallets/{wallet_uuid}/transactions/{transaction_uuid}"
        )

        payload = {
            "writes": [
                {
                    "update": {
                        "name": doc_path,
                        "fields": {
                            "category": {"stringValue": category_uuid},
                        },
                    },
                    "updateMask": {"fieldPaths": ["category"]},
                    "currentDocument": {"exists": True},
                },
                {
                    "transform": {
                        "document": doc_path,
                        "fieldTransforms": [
                            {"fieldPath": "updatedAt", "setToServerValue": "REQUEST_TIME"}
                        ],
                    },
                    "currentDocument": {"exists": True},
                },
            ]
        }

        response = self._raw_request("POST", self._firestore_commit_url(), headers=self._firestore_headers(), json=payload)
        response.raise_for_status()
        return response.json()
