from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import sys
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4

from jose import jwt

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import settings
from app.core.db import SessionLocal
from app.models.user import User


BASE_URL = "http://localhost:8000/api/v1"


def request(path: str, *, method: str = "GET", body: dict | None = None, token: str | None = None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    payload = json.dumps(body).encode("utf-8") if body is not None else None
    req = Request(f"{BASE_URL}{path}", data=payload, headers=headers, method=method)
    try:
        with urlopen(req, timeout=10) as response:
            raw = response.read().decode("utf-8")
            return response.status, json.loads(raw) if raw else None
    except HTTPError as exc:
        raw = exc.read().decode("utf-8")
        return exc.code, json.loads(raw) if raw else None


def expect(label: str, actual, expected) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")
    print(f"PASS {label}")


def main() -> None:
    email = f"audit-{uuid4().hex[:12]}@example.com"
    password = "AuditPass-2026"
    token = ""
    user_id: int | None = None

    status, capabilities = request("/system/capabilities")
    expect("capability status is public", status, 200)
    capability_map = {item["id"]: item for item in capabilities.get("capabilities", [])}
    expect("core capability is ready", capability_map["core"]["status"], "ready")
    if capabilities.get("mode") not in {"real", "demo", "base", "llm"}:
        raise AssertionError("unexpected capability mode")
    print(f"PASS capability mode is {capabilities['mode']}")

    register_payload = {
        "email": email,
        "password": password,
        "profile": {"assets": 80000, "disposable_funds": 50000, "income": 120000},
    }
    status, user = request("/auth/register", method="POST", body=register_payload)
    expect("register returns 200", status, 200)
    user_id = int(user["id"])

    with SessionLocal() as db:
        stored_user = db.get(User, user_id)
        if stored_user is None:
            raise AssertionError("registered user was not stored")
        if stored_user.password_hash == password or not stored_user.password_hash.startswith("$2"):
            raise AssertionError("password was not stored as a bcrypt hash")
    print("PASS password stored as bcrypt hash")

    status, _ = request("/auth/register", method="POST", body=register_payload)
    expect("duplicate registration rejected", status, 409)

    status, _ = request(
        "/auth/login",
        method="POST",
        body={"email": email, "password": "wrong-password"},
    )
    expect("wrong password rejected", status, 401)

    status, login = request(
        "/auth/login",
        method="POST",
        body={"email": email, "password": password},
    )
    expect("correct login returns 200", status, 200)
    token = str(login["access_token"])
    expect("token type is bearer", login["token_type"], "bearer")

    claims = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    expect("JWT subject matches user", claims["sub"], str(user_id))
    if int(claims["exp"]) <= int(datetime.now(tz=timezone.utc).timestamp()):
        raise AssertionError("JWT is already expired")
    print("PASS JWT has a future expiry")

    status, _ = request("/users/me")
    expect("missing token rejected", status, 401)
    status, me = request("/users/me", token=token)
    expect("JWT authenticates current user", status, 200)
    expect("current user email matches", me["email"], email)

    expired_token = jwt.encode(
        {
            "sub": str(user_id),
            "exp": datetime.now(tz=timezone.utc) - timedelta(minutes=1),
        },
        settings.jwt_secret,
        algorithm="HS256",
    )
    status, _ = request("/users/me", token=expired_token)
    expect("expired JWT rejected", status, 401)

    status, profile = request("/profiles/me", token=token)
    expect("profile can be read", status, 200)
    expect("initial assets stored", profile["assets"], 80000.0)

    status, template = request("/profiles/questionnaire/template", token=token)
    expect("questionnaire template available", status, 200)
    if len(template.get("required_order", [])) != 5:
        raise AssertionError("questionnaire template is incomplete")
    print("PASS questionnaire template is complete")

    update = {
        "assets": 100000,
        "disposable_funds": 150000,
        "questionnaire_answers": {
            "disposable_funds": 150000,
            "loss_aversion": 3,
            "risk_comfort": 3,
            "time_horizon": 4,
            "financial_literacy": 2,
        },
    }
    status, _ = request("/profiles/me", method="PUT", body=update, token=token)
    expect("sensitive update without password rejected", status, 401)

    status, _ = request(
        "/profiles/me",
        method="PUT",
        body={**update, "current_password": "wrong-password"},
        token=token,
    )
    expect("sensitive update with wrong password rejected", status, 401)

    status, updated = request(
        "/profiles/me",
        method="PUT",
        body={**update, "current_password": password},
        token=token,
    )
    expect("profile update with current password succeeds", status, 200)
    expect("disposable funds capped by assets", updated["disposable_funds"], 100000.0)
    if "scoring" not in updated.get("questionnaire_answers", {}):
        raise AssertionError("questionnaire scoring was not stored")
    print("PASS questionnaire scoring stored")

    print(f"AUTH SMOKE TEST PASSED for temporary user {email}")


if __name__ == "__main__":
    main()
