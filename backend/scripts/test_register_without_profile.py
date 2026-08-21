"""Regression test for registration without an optional profile payload."""

from __future__ import annotations

import json
import os
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4


BASE_URL = os.getenv("REGRESSION_API_BASE", "http://127.0.0.1:8000/api/v1")


def request(method: str, path: str, payload: dict | None = None) -> tuple[int, dict]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = Request(
        BASE_URL + path,
        data=body,
        headers={"Content-Type": "application/json"},
        method=method,
    )
    try:
        with urlopen(req, timeout=30) as response:
            raw = response.read().decode("utf-8")
            return response.status, json.loads(raw) if raw else {}
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise AssertionError(f"HTTP {exc.code} {path}: {detail}") from exc


def main() -> None:
    email = f"no-profile-{uuid4().hex[:12]}@jintong.example.com"
    password = f"Register-{uuid4().hex}-Aa1!"

    status, user = request(
        "POST",
        "/auth/register",
        {"email": email, "password": password},
    )
    assert status == 200, f"expected registration HTTP 200, got {status}"
    assert user.get("id"), "registration response did not include a user id"

    status, login = request(
        "POST",
        "/auth/login",
        {"email": email, "password": password},
    )
    assert status == 200, f"expected login HTTP 200, got {status}"
    assert login.get("access_token"), "login response did not include an access token"
    print("PASS test_register_without_profile")


if __name__ == "__main__":
    main()
