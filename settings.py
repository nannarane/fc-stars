# settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

APP_ENV = os.getenv("APP_ENV", "dev").strip().lower()

print(f"Running in {APP_ENV} environment.")


# dev: SQLite, prod: Firestore
USE_FIRESTORE = APP_ENV in {"prod", "production", "live"}

# SQLite
SQLITE_DB_PATH = BASE_DIR / "fc_stars.db"
SQLITE_SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"
SQLITE_SEED_PATH = BASE_DIR / "sql" / "sample_data.sql"

# Streamlit / Firebase
STREAMLIT_SECRETS_KEY = "firebase_service_account"
FIREBASE_APP_NAME = "fc_stars"

# 로고 이미지 URL (공용 접근 가능하도록 외부 호스팅)
LOGO_URL_LARGE = "img/title.png"
FAVICON_URL = "img/favicon.png"