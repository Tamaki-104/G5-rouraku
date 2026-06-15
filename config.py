"""アプリ全体の設定。環境変数 .env を読み込む。"""
import os
from dotenv import load_dotenv

load_dotenv()


def _as_bool(value: str, default: bool = True) -> bool:
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


# モードの基本フラグ（True: 全部モック / False: 本接続）
USE_MOCK = _as_bool(os.getenv("USE_MOCK"), default=True)

# Flask セッション署名キー（本番は必ず環境変数で設定）
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "taku-raku-dev-secret")

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

# 機能ごとの有効判定（USE_MOCK=False でも、キーが無ければ自動でモックにフォールバック）
SUPABASE_ENABLED = (not USE_MOCK) and bool(SUPABASE_URL and SUPABASE_ANON_KEY)
GEMINI_ENABLED = (not USE_MOCK) and bool(GEMINI_API_KEY)
