import os
import sys
from pathlib import Path

# “演示数据生成脚本”,生成一批测试数据（Demo Data）

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.db import SessionLocal
from app.services.demo_seed import seed_demo_database


if __name__ == "__main__":
    with SessionLocal() as db:
        print(seed_demo_database(
            db,
            email=os.getenv("DEMO_USER_EMAIL", "demo@jintong.example.com"),
            password=os.getenv("DEMO_USER_PASSWORD", "Demo123456!"),
        ))
