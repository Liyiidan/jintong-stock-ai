"""Verify real mode contains no demo users or demo-seeded data rows."""

from __future__ import annotations

from app.core.config import settings
from app.core.db import SessionLocal
from app.models.ak_data_snapshot import AkDataSnapshot
from app.models.analysis import Analysis
from app.models.company_financial import CompanyFinancial
from app.models.document import Document
from app.models.market import MarketData
from app.models.stock_kline import StockKline
from app.models.stock_quote import StockQuote
from app.models.user import User


def main() -> None:
    assert settings.data_mode == "real", f"expected DATA_MODE=real, got {settings.data_mode!r}"
    assert settings.seed_demo_data is False, "SEED_DEMO_DATA must be false in real mode"

    with SessionLocal() as db:
        demo_user = db.query(User).filter(User.email == "demo@jintong.example.com").first()
        assert demo_user is None, "demo user exists in real mode"

        quote_demo_rows = [
            row
            for row in db.query(StockQuote).all()
            if isinstance(row.raw, dict) and row.raw.get("source") == "demo_seed"
        ]
        assert not quote_demo_rows, "demo_seed quote rows exist in real mode"

        source_models = (MarketData, StockKline, CompanyFinancial, Document, AkDataSnapshot)
        for model in source_models:
            rows = db.query(model).filter(model.source == "demo_seed").count()
            assert rows == 0, f"demo_seed rows exist in {model.__tablename__}: {rows}"

        # Analysis rows do not have a source column; inspect persisted metadata too.
        for analysis in db.query(Analysis).all():
            text = repr(analysis.rationale)
            assert "demo_seed" not in text, f"demo_seed metadata exists in analysis {analysis.id}"

    print("PASS test_no_demo_data_in_real_mode")


if __name__ == "__main__":
    main()
