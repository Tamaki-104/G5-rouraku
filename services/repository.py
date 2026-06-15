"""
データアクセス層。
画面・ロジックはこの関数経由でデータを取得する。

config.SUPABASE_ENABLED が True なら Supabase、False ならモックデータを使う。
E-R図では「物件条件」と「住宅情報」が別テーブルなので、
get_all_properties() は両者を結合（JOIN相当）して、画面が使う
フラットな1物件 dict（エリア・間取り等を含む）を返す。
"""
import config
from data.mock_data import (
    PROPERTY_CONDITIONS, PROPERTIES, MOVE_IN_FLOWS,
)

_client = None


def _supabase():
    """Supabase クライアント（遅延初期化のシングルトン）。"""
    global _client
    if _client is None:
        from supabase import create_client
        _client = create_client(config.SUPABASE_URL, config.SUPABASE_ANON_KEY)
    return _client


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


def get_all_properties():
    """全物件を、物件条件と結合したフラット形で返す。"""
    if config.SUPABASE_ENABLED:
        # property_conditions をネスト取得して結合
        rows = (_supabase().table("properties")
                .select("*, property_conditions(*)").execute().data)
        return [_flatten(r, r.get("property_conditions")) for r in rows]

    # --- モック ---
    by_id = {c["id"]: c for c in PROPERTY_CONDITIONS}
    return [_flatten(p, by_id.get(p["property_condition_id"])) for p in PROPERTIES]


def get_property(property_id: str):
    """ID で1件取得（結合済み）。見つからなければ None。"""
    if config.SUPABASE_ENABLED:
        rows = (_supabase().table("properties")
                .select("*, property_conditions(*)")
                .eq("id", property_id).limit(1).execute().data)
        if not rows:
            return None
        r = rows[0]
        return _flatten(r, r.get("property_conditions"))

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
        _supabase().table("chats").insert(
            {"question": question, "answer": answer}).execute()
    except Exception:
        # 保存失敗はチャット表示を妨げないよう握りつぶす
        pass
