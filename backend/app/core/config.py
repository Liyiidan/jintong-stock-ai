from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

# Optional local model paths.
# If set, these values override remote HuggingFace repo names.
# Example (WSL): "/mnt/d/master_dynamic/backend/models/sentiment/guba_model"
LOCAL_SENTIMENT_GUBA_MODEL = ""
LOCAL_SENTIMENT_GUBA_TOKENIZER = ""
LOCAL_SENTIMENT_NEWS_MODEL = ""
LOCAL_HF_CACHE_DIR = ""


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    # database
    app_name: str = "Stock Intelligence MVP"
    api_v1_str: str = "/api/v1"
    database_url: str
    jwt_secret: str
    access_token_expire_minutes: int = 60 * 24
    allowed_origins: str = "http://localhost:5173"
    # real is the only safe default. Demo fixtures require an explicit mode.
    data_mode: Literal["real", "demo"] = "real"
    # Secrets must be supplied through environment variables or backend/.env.
    zhipu_api_key: str = ""
    zhipu_api_key_news: str = ""
    zhipu_api_key_stock_data: str = ""
    zhipu_api_key_macro: str = ""
    zhipu_api_key_financial: str = ""
    zhipu_api_key_fundamental: str = ""
    zhipu_api_key_investment: str = ""
    # glm-4.7-flash is currently returning provider 1305 (model overloaded).
    # Use the broadly available flash endpoint for production analysis.
    zhipu_model: str = "glm-4-flash"
    zhipu_base_url: str = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    llm_timeout_seconds: int = 45
    zhipu_thinking_type: str = "disabled"
    zhipu_max_tokens: int = 8192
    # LLM rate-limit and retry controls
    zhipu_retry_max_attempts: int = 3
    zhipu_retry_base_delay_seconds: float = 2.5
    zhipu_retry_max_delay_seconds: float = 20.0
    zhipu_retry_jitter_seconds: float = 0.8
    zhipu_rate_limit_interval_seconds: float = 2.0
    zhipu_allow_cross_role_key_fallback: bool = False
    # One shared API key must be paced sequentially; parallel expert calls trigger provider 429s.
    expert_parallel_workers: int = 1

    max_ranking_symbols: int = 60
    default_history_days: int = 180
    log_level: str = "INFO"
    analysis_worker_threads: int = 4
    ranking_worker_threads: int = 2
    max_background_futures: int = 1000
    seed_demo_data: bool = False
    demo_user_email: str = ""
    demo_user_password: str = ""
    # CNInfo ingestion
    cninfo_enabled: bool = True
    cninfo_base_url: str = "http://webapi.cninfo.com.cn"
    cninfo_accept_enckey: str = ""
    cninfo_cookie: str = ""
    cninfo_referer: str = "https://webapi.cninfo.com.cn/"
    cninfo_user_agent: str = "Mozilla/5.0"
    cninfo_timeout_seconds: int = 25
    cninfo_increment_rowcount: int = 1000
    cninfo_financial_strict: bool = True
    cninfo_auto_bootstrap: bool = False
    cninfo_bootstrap_headless: bool = False
    cninfo_bootstrap_retry_on_401: bool = True
    cninfo_headers_cache_file: str = ""
    cninfo_profile_dir: str = ""
    cninfo_bootstrap_wait_seconds: int = 8
    cninfo_header_max_age_seconds: int = 300

    # Public data providers may reject the default python-requests client.
    data_user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/131.0 Safari/537.36"
    data_request_timeout_seconds: int = 25

    # sentiment module
    hf_cache_dir: str = LOCAL_HF_CACHE_DIR or "/mnt/d/master_dynamic/backend/models/sentiment/.hf_cache"
    sentiment_batch_size: int = 16
    sentiment_guba_model_name: str = (
        LOCAL_SENTIMENT_GUBA_MODEL or "/mnt/d/master_dynamic/backend/models/sentiment/guba_model"
    )
    sentiment_guba_tokenizer_name: str = (
        LOCAL_SENTIMENT_GUBA_TOKENIZER or "/mnt/d/master_dynamic/backend/models/sentiment/guba_tokenizer"
    )
    sentiment_news_model_name: str = (
        LOCAL_SENTIMENT_NEWS_MODEL or "/mnt/d/master_dynamic/backend/models/sentiment/news_model"
    )


settings = Settings()
