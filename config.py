"""
アプリ全体の設定値を1か所に集約するモジュール。

概要:
    .env ファイル（環境変数）から接続情報や動作モードを読み込み、他モジュールが
    参照する定数として公開する。秘密情報（APIキー等）はコードに直書きせず、
    必ず環境変数から取り込む方針。

作成    : チーム労楽
Copyright (c) 2026 チーム労楽. All rights reserved.
"""
import os
from dotenv import load_dotenv

# プロジェクト直下の .env を環境変数として読み込む（ローカル開発用。本番はVercelの環境変数）。
load_dotenv()


def _as_bool(value: str, default: bool = True) -> bool:
    """環境変数の文字列を真偽値に変換する（"true"/"1"/"yes"/"on" を真とみなす）。

    環境変数は常に文字列で渡ってくるため、フラグとして扱う前にここで正規化する。
    未設定（None）のときは default を返す。
    """
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


# 動作モードの基本フラグ。True: すべてモックデータ / False: 本番サービスへ接続。
USE_MOCK = _as_bool(os.getenv("USE_MOCK"), default=True)

# Flask セッションCookieの署名キー。漏洩=セッション偽造につながるため本番は必ず環境変数で指定。
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "taku-raku-dev-secret")

# Gemini（AI）接続情報。
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Supabase（DB）接続情報。
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

# --- 機能ごとの有効判定 ---
# Supabase: DBの切替なので USE_MOCK に従い、かつ接続情報が揃っている場合のみ有効。
SUPABASE_ENABLED = (not USE_MOCK) and bool(SUPABASE_URL and SUPABASE_ANON_KEY)
# Gemini: DBとは独立させ、「APIキーがあれば実AI・無ければモックAI」とする。
# こうすることで、モックデータのままでもAIだけ本物、という組み合わせが可能。
GEMINI_ENABLED = bool(GEMINI_API_KEY)
