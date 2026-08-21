"""Regression test: run the same real-data analysis twice for 000001."""

from __future__ import annotations

import json
import os
import time
import uuid
from urllib.error import HTTPError
from urllib.request import Request, urlopen


BASE_URL = os.getenv("REGRESSION_API_BASE", "http://127.0.0.1:8000/api/v1")
SYMBOL = "000001"
POLL_INTERVAL_SECONDS = 1.5
TIMEOUT_SECONDS = 1200


def request(method: str, path: str, payload: dict | None = None, token: str | None = None) -> dict:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request_obj = Request(BASE_URL + path, data=body, headers=headers, method=method)
    try:
        with urlopen(request_obj, timeout=60) as response:
            return json.load(response)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise AssertionError(f"HTTP {exc.code} {path}: {detail}") from exc


def create_test_user() -> tuple[int, str]:
    email = f"double-analysis-{uuid.uuid4().hex[:12]}@jintong.example.com"
    password = f"Regression-{uuid.uuid4().hex}-Aa1!"
    user = request(
        "POST",
        "/auth/register",
        {
            "email": email,
            "password": password,
            "profile": {"assets": 100000, "disposable_funds": 50000},
        },
    )
    login = request("POST", "/auth/login", {"email": email, "password": password})
    return int(user["id"]), str(login["access_token"])


def run_analysis(user_id: int, token: str, run_number: int) -> dict:
    task = request(
        "POST",
        "/analysis/tasks",
        {"stock_symbol": SYMBOL, "user_id": user_id},
        token,
    )
    task_id = str(task["task_id"])
    deadline = time.monotonic() + TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        current = request("GET", f"/analysis/tasks/{task_id}", token=token)
        status = current.get("status")
        if status == "completed":
            assert current.get("analysis_id"), f"run {run_number} completed without analysis_id"
            assert (current.get("result") or {}).get("stock_symbol") == SYMBOL
            print(f"run {run_number}: completed analysis_id={current['analysis_id']}")
            return current
        if status == "failed":
            raise AssertionError(f"run {run_number} failed: {current.get('error')}")
        time.sleep(POLL_INTERVAL_SECONDS)
    raise AssertionError(f"run {run_number} timed out")


def main() -> None:
    user_id, token = create_test_user()
    first = run_analysis(user_id, token, 1)
    second = run_analysis(user_id, token, 2)
    assert first["status"] == second["status"] == "completed"
    print("PASS test_double_analysis_000001")


if __name__ == "__main__":
    main()
