"""Run the bounded AkShare trial set from a backend container or local venv."""

from __future__ import annotations

import argparse
import json
from datetime import date

from app.core.db import SessionLocal
from app.services.data_ingest.akshare_service import AkshareServiceError
from app.services.data_ingest import akshare_service


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync 3-5 real A-share symbols through AkShare")
    parser.add_argument("symbols", nargs="+", help="3-5 stock symbols, e.g. 000001 000333 000651")
    parser.add_argument("--trade-date", default=date.today().isoformat())
    parser.add_argument("--history-days", type=int, default=120)
    parser.add_argument("--no-news", action="store_true")
    args = parser.parse_args()
    if not 3 <= len(args.symbols) <= 5:
        parser.error("provide between 3 and 5 symbols")

    with SessionLocal() as db:
        log = akshare_service.start_sync_log(db, job_type="minimal_real_sync", scope=",".join(args.symbols))
        try:
            result = akshare_service.minimal_real_sync(
                db,
                symbols=args.symbols,
                trade_date=date.fromisoformat(args.trade_date),
                history_days=args.history_days,
                include_news=not args.no_news,
            )
            sync_status = "completed" if result.get("status") == "completed" else "partial"
            akshare_service.finish_sync_log(db, log=log, status=sync_status, detail=result)
        except AkshareServiceError as exc:
            db.rollback()
            akshare_service.finish_sync_log(db, log=log, status="failed", detail={}, error_message=str(exc))
            raise
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
