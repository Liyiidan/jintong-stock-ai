"""Verify the analysis API exposes a rate-limit rules fallback status."""

from __future__ import annotations

from unittest.mock import PropertyMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient
from app.core.config import settings
from app.core.db import SessionLocal
from app.core.security import create_access_token, get_password_hash
from app.main import app
from app.models.profile import UserProfile
from app.models.user import User
from app.services.experts_v2.orchestrator import expert_orchestrator
from app.services.llm.zhipu_client import LLMClientError, zhipu_client


def main() -> None:
    with SessionLocal() as db:
        for stale_user in db.query(User).filter(User.email.like("rate-limit-test-%@jintong.example.com")).all():
            for analysis in list(stale_user.analyses):
                db.delete(analysis)
            if stale_user.profile:
                db.delete(stale_user.profile)
            db.delete(stale_user)
        db.commit()

    email = f"rate-limit-test-{uuid4().hex[:12]}@jintong.example.com"
    password_hash = get_password_hash(f"RateLimit-{uuid4().hex}-Aa1!")
    with SessionLocal() as db:
        user = User(email=email, password_hash=password_hash)
        db.add(user)
        db.flush()
        db.add(UserProfile(user_id=user.id, assets=100000.0, disposable_funds=50000.0, income=0.0))
        db.commit()
        user_id = int(user.id)

    token = create_access_token(str(user_id))
    rate_limit_error = LLMClientError("Error code: 429 rate limit")
    coverage = {
        "before": {"news_count": 1, "macro_count": 1, "market_data_count": 1, "financial_count": 1, "financial_event_count": 0, "has_fundamental": True},
        "after": {"news_count": 1, "macro_count": 1, "market_data_count": 1, "financial_count": 1, "financial_event_count": 0, "has_fundamental": True},
        "repairs": {},
        "errors": {},
    }

    def raise_rate_limit(*_args, **_kwargs):
        raise rate_limit_error

    try:
        with (
            TestClient(app) as client,
            patch.object(zhipu_client.__class__, "enabled", new_callable=PropertyMock, return_value=True),
            patch.object(expert_orchestrator, "_call_expert_llm", side_effect=raise_rate_limit),
            patch.object(expert_orchestrator, "_call_investment_llm", side_effect=raise_rate_limit),
            patch("app.api.routes.analysis.akshare_service.sync_symbol_hot_data", return_value={"refreshed": {}}),
            patch("app.api.routes.analysis._ensure_analysis_data_ready", return_value=coverage),
        ):
            response = client.post(
                "/api/v1/analysis",
                json={"stock_symbol": "000001", "user_id": user_id},
                headers={"Authorization": f"Bearer {token}"},
            )
        assert response.status_code == 200, response.text
        payload = response.json()
        ai_status = payload["ai_analysis_status"]
        assert ai_status["status"] == "rules_fallback", ai_status
        assert "rate_limited" in set(ai_status["fallback_reasons"].values()), ai_status
        print("PASS test_llm_rate_limit_fallback")
    finally:
        with SessionLocal() as db:
            user = db.get(User, user_id)
            if user:
                for analysis in list(user.analyses):
                    db.delete(analysis)
                if user.profile:
                    db.delete(user.profile)
                db.delete(user)
                db.commit()


if __name__ == "__main__":
    main()
