import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analysis, auth, data_sync, documents, portfolio, profiles, sentiment, stocks, system, trades, users, workflow
from app.core.config import settings
from app.core.db import Base, engine
from app.core.logging import setup_logging
from app.core.responses import UTF8JSONResponse
from app.core.schema_compat import apply_schema_compat_migrations
from app.core.task_manager import task_manager
from app.core.db import SessionLocal
from app.services.demo_seed import seed_demo_database

# main.py 文件其实是整个后端项目的 入口程序（API 启动文件）
# 它负责启动 FastAPI 服务，并把所有 API 模块注册到服务器里。
app = FastAPI(title=settings.app_name, default_response_class=UTF8JSONResponse)

origins = [origin.strip() for origin in settings.allowed_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.api_v1_str)
app.include_router(users.router, prefix=settings.api_v1_str)
app.include_router(profiles.router, prefix=settings.api_v1_str)
app.include_router(stocks.router, prefix=settings.api_v1_str)
app.include_router(sentiment.router, prefix=settings.api_v1_str)
app.include_router(documents.router, prefix=settings.api_v1_str)
app.include_router(analysis.router, prefix=settings.api_v1_str)
app.include_router(portfolio.router, prefix=settings.api_v1_str)
app.include_router(trades.router, prefix=settings.api_v1_str)
app.include_router(workflow.router, prefix=settings.api_v1_str)
app.include_router(data_sync.router, prefix=settings.api_v1_str)
app.include_router(system.router, prefix=settings.api_v1_str)


setup_logging(settings.log_level)
logger = logging.getLogger(__name__)


@app.on_event("startup")
def bootstrap_schema() -> None:
    Base.metadata.create_all(bind=engine)
    migration_result = apply_schema_compat_migrations(engine)
    if settings.data_mode == "demo" and settings.seed_demo_data and settings.demo_user_email and settings.demo_user_password:
        try:
            with SessionLocal() as db:
                demo_result = seed_demo_database(db, settings.demo_user_email, settings.demo_user_password)
            logger.info("demo seed completed | %s", demo_result)
        except Exception:
            logger.exception("demo seed failed; backend will continue without demo rows")
    if settings.seed_demo_data and settings.data_mode != "demo":
        logger.warning("SEED_DEMO_DATA is ignored unless DATA_MODE=demo")
    logger.info("startup completed | schema_compat=%s data_mode=%s", migration_result, settings.data_mode)


@app.on_event("shutdown")
def close_background_executors() -> None:
    task_manager.shutdown()


@app.get("/")
def root() -> dict:
    return {"status": "ok", "app": settings.app_name}
