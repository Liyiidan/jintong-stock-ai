"""Verify that the bounded real-data trial contains traceable, non-demo records."""

from __future__ import annotations

from app.core.db import SessionLocal
from app.models.company_financial import CompanyFinancial
from app.models.document import Document
from app.models.market import MarketData
from app.models.stock_quote import StockQuote


def expect(label: str, value: int) -> None:
    if value <= 0:
        raise AssertionError(f"{label}: expected at least one record, got {value}")
    print(f"PASS {label}: {value}")


def main() -> None:
    with SessionLocal() as db:
        quote_count = int(db.query(StockQuote).count())
        history_count = int(db.query(MarketData).count())
        financial_count = int(db.query(CompanyFinancial).count())
        document_count = int(db.query(Document).count())
        demo_count = int(
            db.query(CompanyFinancial).filter(CompanyFinancial.source == "demo_seed").count()
            + db.query(Document).filter(Document.source == "demo_seed").count()
        )
        expect("real quotes", quote_count)
        expect("real history", history_count)
        expect("real financials", financial_count)
        expect("real documents", document_count)
        if demo_count:
            raise AssertionError(f"demo rows detected: {demo_count}")
        print("PASS no demo rows detected")


if __name__ == "__main__":
    main()
