"""
設定の集約。.env（環境変数）から動作モードと各種キーを読み込む。
キーやシークレットはソースに直書きせず、必ず本モジュール経由で環境変数から取得する。

作成: チーム労楽  /  (c) 2026 チーム労楽
"""
import os
from dotenv import load_dotenv

load_dotenv()  # ローカル開発用。本番(Vercel)では環境変数が直接注入されるため実質no-op。


def _as_bool(value: str, default: bool = True) -> bool:
    """環境変数の文字列を真偽値へ変換する。"1"/"true"/"yes"/"on" を真とみなす。"""
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


# True: 全てモックデータで動作 / False: 本番サービス(Supabase等)へ接続。
USE_MOCK = _as_bool(os.getenv("USE_MOCK"), default=True)

# セッションCookieの署名鍵。漏洩するとなりすましが可能になるため本番は必ず環境変数で指定する。
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "taku-raku-dev-secret")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
# 既定は無料枠が広く軽量・高速な flash-lite(2.5系)。上位品質が必要な場合は環境変数
# GEMINI_MODEL=gemini-2.5-flash に切替可能(ただし無料枠の1日上限は小さい)。
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

# SupabaseはUSE_MOCKに連動する(DBの切替)。接続情報が欠けている場合は無効とする。
SUPABASE_ENABLED = (not USE_MOCK) and bool(SUPABASE_URL and SUPABASE_ANON_KEY)
# GeminiはUSE_MOCKと切り離す。「モックデータのままAIのみ実接続」という構成も許容するため、
# 判定はキーの有無のみとする。キーが無い場合は ai.py がモック応答へ切り替える。
GEMINI_ENABLED = bool(GEMINI_API_KEY)
