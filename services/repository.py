"""
データアクセス層。
画面・ロジックはこの関数経由でデータを取得する。

config.SUPABASE_ENABLED が True なら Supabase（PostgREST の REST API を直接呼ぶ）、
False ならモックデータを使う。

Supabase 接続は supabase-py クライアントではなく REST を直接叩く方式にしている：
  - 新形式の publishable キー（sb_publishable_...）にも確実に対応できる
  - 依存が requests だけで済み、Vercel のサーバーレス関数が軽量になる

E-R図では「物件条件」と「住宅情報」が別テーブルなので、PostgREST の埋め込み
（?select=*,property_conditions(*)）で結合して取得し、画面用のフラットな dict に整形する。
"""
import config
from data.mock_data import (
    PROPERTY_CONDITIONS, PROPERTIES, MOVE_IN_FLOWS,
)


# ------------------------------------------------------------------
# Supabase REST ヘルパー
# ------------------------------------------------------------------
def _headers(extra=None):
    key = config.SUPABASE_ANON_KEY
    h = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    if extra:
        h.update(extra)
    return h


def _rest_get(path, params=None):
    import requests
    url = config.SUPABASE_URL.rstrip("/") + "/rest/v1/" + path
    r = requests.get(url, headers=_headers(), params=params, timeout=15)
    r.raise_for_status()
    return r.json()


# ------------------------------------------------------------------
# 結合 → フラット整形
# ------------------------------------------------------------------
def _flatten(prop: dict, cond: dict) -> dict:
    """住宅情報 × 物件条件 を結合し、画面用のフラット dict を作る。"""
    cond = cond or {}
    return {
        "id": prop["id"],
        "name": prop["name"],
        "rent": prop["rent"],
        "building_type": prop["building_type"],
        "deal_type": prop.get("deal_type", "賃貸"),
        "image_url": prop.get("image_url", ""),
        "description": prop.get("description", ""),
        # 物件条件テーブル由来
        "area": cond.get("area", ""),
        "layout": cond.get("layout", ""),
        "station_minutes": cond.get("station_minutes"),
        "pet_allowed": cond.get("pet_allowed", False),
    }


# ------------------------------------------------------------------
# 公開関数
# ------------------------------------------------------------------
def get_all_properties():
    """全物件を、物件条件と結合したフラット形で返す。"""
    if config.SUPABASE_ENABLED:
        rows = _rest_get("properties", {"select": "*,property_conditions(*)"})
        return [_flatten(r, r.get("property_conditions")) for r in rows]

    # --- モック ---
    by_id = {c["id"]: c for c in PROPERTY_CONDITIONS}
    return [_flatten(p, by_id.get(p["property_condition_id"])) for p in PROPERTIES]


def get_property(property_id: str):
    """ID で1件取得（結合済み）。見つからなければ None。"""
    if config.SUPABASE_ENABLED:
        rows = _rest_get("properties", {
            "id": f"eq.{property_id}",
            "select": "*,property_conditions(*)",
            "limit": 1,
        })
        if not rows:
            return None
        return _flatten(rows[0], rows[0].get("property_conditions"))

    for p in get_all_properties():
        if p["id"] == property_id:
            return p
    return None


def get_move_in_flow(deal_type: str):
    """取引種別（賃貸/購入）の入居手続きフローを返す。
    （入居フローは E-R図のテーブルではなく取引種別から導出する定数）。"""
    return MOVE_IN_FLOWS.get(deal_type, [])


def save_chat(question: str, answer: str):
    """チャット履歴を chats テーブルへ保存（Supabase接続時のみ）。"""
    if not config.SUPABASE_ENABLED:
        return
    try:
        import requests
        url = config.SUPABASE_URL.rstrip("/") + "/rest/v1/chats"
        requests.post(url, headers=_headers({"Prefer": "return=minimal"}),
                      json={"question": question, "answer": answer}, timeout=15)
    except Exception:
        # 保存失敗はチャット表示を妨げないよう握りつぶす
        pass
