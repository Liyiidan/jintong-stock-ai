from __future__ import annotations

import importlib.util

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.models.company_financial import CompanyFinancial
from app.models.data_sync_log import DataSyncLog
from app.models.document import Document
from app.models.market import MarketData
from app.models.stock_quote import StockQuote
from app.services.llm import zhipu_client


router = APIRouter(prefix="/system", tags=["system"])


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _data_status(db: Session) -> dict:
    """Return freshness metadata without exposing raw credentials or payloads."""
    quote_count = int(db.query(func.count(StockQuote.id)).scalar() or 0)
    market_count = int(db.query(func.count(MarketData.id)).scalar() or 0)
    financial_count = int(db.query(func.count(CompanyFinancial.id)).scalar() or 0)
    document_count = int(db.query(func.count(Document.id)).scalar() or 0)
    demo_financial_count = int(
        db.query(func.count(CompanyFinancial.id)).filter(CompanyFinancial.source == "demo_seed").scalar() or 0
    )
    demo_document_count = int(
        db.query(func.count(Document.id)).filter(Document.source == "demo_seed").scalar() or 0
    )
    latest_quote = db.query(StockQuote).order_by(StockQuote.quote_time.desc()).first()
    latest_market = db.query(MarketData).order_by(MarketData.fetched_at.desc()).first()
    latest_financial = db.query(CompanyFinancial).order_by(CompanyFinancial.updated_at.desc()).first()
    latest_document = db.query(Document).order_by(Document.created_at.desc()).first()
    latest_sync = db.query(DataSyncLog).order_by(DataSyncLog.started_at.desc()).first()

    def iso(value):
        return value.isoformat() if value else None

    return {
        "mode": settings.data_mode,
        "demo_rows_detected": demo_financial_count + demo_document_count,
        "datasets": [
            {
                "id": "quotes",
                "label": "最新行情",
                "row_count": quote_count,
                "source": (latest_quote.raw or {}).get("source", "unknown") if latest_quote else "unknown",
                "updated_at": iso(db.query(func.max(StockQuote.quote_time)).scalar()),
                "status": "available" if quote_count else "empty",
            },
            {
                "id": "history",
                "label": "历史 K 线",
                "row_count": market_count,
                "source": latest_market.source if latest_market else "unknown",
                "updated_at": iso(latest_market.fetched_at) if latest_market else None,
                "status": "available" if market_count else "empty",
            },
            {
                "id": "financials",
                "label": "财报数据",
                "row_count": financial_count,
                "source": latest_financial.source or "unknown" if latest_financial else "unknown",
                "updated_at": iso(db.query(func.max(CompanyFinancial.updated_at)).scalar()),
                "status": "available" if financial_count else "empty",
            },
            {
                "id": "documents",
                "label": "新闻与资料",
                "row_count": document_count,
                "source": latest_document.source or "unknown" if latest_document else "unknown",
                "updated_at": iso(db.query(func.max(Document.created_at)).scalar()),
                "status": "available" if document_count else "empty",
            },
        ],
        "last_sync": {
            "status": latest_sync.status if latest_sync else "never",
            "started_at": iso(latest_sync.started_at) if latest_sync else None,
            "finished_at": iso(latest_sync.finished_at) if latest_sync else None,
            "error_message": latest_sync.error_message if latest_sync else None,
        },
    }


@router.get("/capabilities")
def get_capabilities(db: Session = Depends(get_db)) -> dict:
    """Expose dependency readiness without exposing secrets or credentials."""
    llm_sdk_ready = _module_available("zai")
    llm_key_ready = zhipu_client.enabled
    akshare_ready = _module_available("akshare")
    sentiment_ready = _module_available("transformers") and _module_available("torch")
    cninfo_ready = bool(
        settings.cninfo_enabled
        and str(settings.cninfo_accept_enckey or "").strip()
        and str(settings.cninfo_cookie or "").strip()
    )

    if llm_key_ready and llm_sdk_ready:
        llm_status = "ready"
        llm_message = "智谱 AI 已配置，可生成多专家分析。"
    elif not llm_key_ready:
        llm_status = "not_configured"
        llm_message = "未配置智谱 API Key，分析会使用本地规则回退。"
    else:
        llm_status = "unavailable"
        llm_message = "已配置智谱 Key，但后端未安装 zai-sdk。"

    if akshare_ready:
        market_status = "ready"
        market_message = "AkShare 行情与财经数据采集可用。"
    else:
        market_status = "not_installed"
        market_message = "未安装 AkShare；账户、画像和已有数据库内容仍可用。"

    if sentiment_ready:
        sentiment_status = "optional"
        sentiment_message = "本地情绪模型依赖已安装，首次使用仍需模型文件或下载模型。"
    else:
        sentiment_status = "not_installed"
        sentiment_message = "未安装 Transformers/PyTorch，本地情绪模型暂不可用。"

    status = _data_status(db)
    demo_rows_detected = status["demo_rows_detected"]
    demo_status = "warning" if settings.data_mode == "real" and demo_rows_detected else "optional"
    demo_message = (
        f"真实模式检测到 {demo_rows_detected} 条样例数据残留，请清空数据库或重新创建 volume。"
        if demo_rows_detected and settings.data_mode == "real"
        else "演示模式使用固定样例数据；这些内容不能用于投资判断。"
        if settings.data_mode == "demo"
        else "真实模式未启用样例数据。"
    )
    return {
        "mode": settings.data_mode,
        "data_status": status,
        "capabilities": [
            {
                "id": "core",
                "label": "账户与投资者画像",
                "status": "ready",
                "message": "PostgreSQL、注册登录、JWT 和画像功能可用。",
                "requires_api_key": False,
            },
            {
                "id": "fallback_analysis",
                "label": "基础分析回退",
                "status": "ready",
                "message": "没有 AI Key 时不会伪装成实时结论；仅在数据库存在已验证数据时运行规则分析。",
                "requires_api_key": False,
            },
            *([
                {
                    "id": "demo_data",
                    "label": "本地样例数据",
                    "status": demo_status,
                    "message": demo_message,
                    "requires_api_key": False,
                }
            ] if settings.data_mode == "demo" or demo_rows_detected else []),
            {
                "id": "market_data",
                "label": "行情与财经数据",
                "status": market_status,
                "message": market_message,
                "requires_api_key": False,
            },
            {
                "id": "cninfo",
                "label": "巨潮资讯财报",
                "status": "ready" if cninfo_ready else "not_configured",
                "message": "CNInfo 请求头已配置。" if cninfo_ready else "未配置 CNInfo 请求头，将跳过该数据源。",
                "requires_api_key": False,
            },
            {
                "id": "sentiment_models",
                "label": "本地情绪模型",
                "status": sentiment_status,
                "message": sentiment_message,
                "requires_api_key": False,
            },
            {
                "id": "llm",
                "label": "智谱 AI 多专家分析",
                "status": llm_status,
                "message": llm_message,
                "requires_api_key": True,
            },
        ],
    }
