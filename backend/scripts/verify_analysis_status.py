"""Exercise one analysis request and verify structured status metadata."""

from __future__ import annotations

import json
import os
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from uuid import uuid4


BASE_URL = os.getenv("REGRESSION_API_BASE", "http://127.0.0.1:8000/api/v1")


def request(method: str, path: str, payload: dict | None = None, token: str | None = None) -> dict:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = Request(BASE_URL + path, data=body, headers=headers, method=method)
    try:
        with urlopen(req, timeout=60) as response:
            return json.load(response)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise AssertionError(f"HTTP {exc.code} {path}: {detail}") from exc


def main() -> None:
    email = f"status-check-{uuid4().hex[:12]}@jintong.example.com"
    password = f"Status-{uuid4().hex}-Aa1!"
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
    token = login["access_token"]
    task = request(
        "POST",
        "/analysis/tasks",
        {"stock_symbol": "000001", "user_id": int(user["id"])},
        token,
    )
    deadline = time.monotonic() + 1200
    result = None
    while time.monotonic() < deadline:
        task_state = request("GET", f"/analysis/tasks/{task['task_id']}", token=token)
        if task_state.get("status") == "completed":
            result = task_state.get("result")
            break
        if task_state.get("status") == "failed":
            raise AssertionError(f"analysis task failed: {task_state.get('error')}")
        time.sleep(1.5)
    if not isinstance(result, dict):
        raise AssertionError("analysis task timed out")

    assert result["stock_symbol"] == "000001"
    source_status = result.get("data_source_status")
    assert isinstance(source_status, list) and source_status
    assert {"source", "fetched_at", "sync_status"}.issubset(source_status[0])
    assert all(item["sync_status"] in {"success", "failed", "stale"} for item in source_status)

    ai_status = result.get("ai_analysis_status")
    assert isinstance(ai_status, dict)
    assert ai_status["status"] in {"llm_success", "rules_fallback", "failed"}
    assert "fallback_components" in ai_status
    assert "fallback_reasons" in ai_status

    # Print only non-sensitive, structured status metadata for endpoint verification.
    print(json.dumps({"data_source_status": source_status, "ai_analysis_status": ai_status}, ensure_ascii=False, default=str))
    print("PASS verify_analysis_status")


if __name__ == "__main__":
    main()
