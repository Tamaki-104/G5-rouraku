"""
設定の集約。.env（環境変数）から動作モードと各種キーを読み込む。
キーやシークレットはソースに直書きせず、必ずここ経由で環境変数から取る。

作成: チーム労楽  /  (c) 2026 チーム労楽
"""
import os
from dotenv import load_dotenv

load_dotenv()  # ローカル開発用。本番(Vercel)は環境変数が直接入るので実質no-op。


def _as_bool(value: str, default: bool = True) -> bool:
    """環境変数の文字列を真偽値に。"1"/"true"/"yes"/"on" を真とみなす。"""
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


# True: 全部モックデータで動く / False: 本番サービス(Supabase等)へ接続。
USE_MOCK = _as_bool(os.getenv("USE_MOCK"), default=True)

# セッションCookieの署名鍵。漏れると他人になりすませるので本番は必ず環境変数で。
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "taku-raku-dev-secret")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
# 既定は無料枠が広く軽量・高速な flash-lite(2.5系)。上位品質が欲しければ環境変数で
# GEMINI_MODEL=gemini-2.5-flash に切り替え可(ただし無料枠の1日上限は小さめ)。
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

# Supabaseはモード連動（DBの切替）。接続情報が欠けていれば無効に倒す。
SUPABASE_ENABLED = (not USE_MOCK) and bool(SUPABASE_URL and SUPABASE_ANON_KEY)
# GeminiはあえてUSE_MOCKと切り離す。「モックデータのままAIだけ本物」も許したいので、
# 判定はキーの有無だけ。キーが無ければ ai.py がモック応答に切り替える。
GEMINI_ENABLED = bool(GEMINI_API_KEY)
