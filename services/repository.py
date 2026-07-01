"""
データアクセス層（画面・ロジックとデータ保管先の橋渡し）。

概要:
    物件やチャット履歴の読み書きを、この層の関数に集約する。呼び出し側は
    データが Supabase から来るのかモックから来るのかを意識しなくてよい
    （config.SUPABASE_ENABLED で自動的に切り替わる）。

Supabase接続方式の選定理由:
    supabase-py クライアントではなく PostgREST の REST API を requests で直接叩く。
      - 新形式の publishable キー（sb_publishable_...）にも確実に対応できる
      - 依存が requests だけで済み、Vercel のサーバーレス関数が軽量になる

データ整形:
    E-R図では「物件条件(property_conditions)」と「住宅情報(properties)」が別テーブル。
    PostgREST の埋め込み（?select=*,property_conditions(*)）で結合取得し、
    画面が扱いやすい 1階層の dict に平坦化して返す。

作成    : チーム労楽
Copyright (c) 2026 チーム労楽. All rights reserved.
"""
import config
from data.mock_data import (
    PROPERTY_CONDITIONS, PROPERTIES, MOVE_IN_FLOWS,
)


# ------------------------------------------------------------------
# Supabase REST ヘルパー
# ------------------------------------------------------------------
def _headers(extra=None):
    """Supabase REST 呼び出しに必要な認証ヘッダを組み立てる（必要なら追加分をマージ）。"""
    key = config.SUPABASE_ANON_KEY
    # apikey と Authorization の両方にキーが必要（Supabase/PostgRESTの仕様）。
    h = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    if extra:
        h.update(extra)
    return h


def _rest_get(path, params=None):
    """PostgREST の GET を実行し、JSON（行のリスト）を返す共通処理。"""
    import requests
    url = config.SUPABASE_URL.rstrip("/") + "/rest/v1/" + path
    r = requests.get(url, headers=_headers(), params=params, timeout=15)
    r.raise_for_status()   # 4xx/5xx はここで例外化し、呼び出し側で扱えるようにする。
    return r.json()


# ------------------------------------------------------------------
# 結合 → フラット整形
# ------------------------------------------------------------------
def _flatten(prop: dict, cond: dict) -> dict:
    """住宅情報(prop) と 物件条件(cond) を1つの dict に結合し、画面用に平坦化する。

    Supabase由来（ネストした property_conditions）でもモック由来でも、
    同じ形の dict を返すことで、画面・マッチング側の処理を共通化する。
    """
    cond = cond or {}   # 結合相手が無い場合でも落ちないよう空dictで代替。
    return {
        "id": prop["id"],
        "name": prop["name"],
        "rent": prop["rent"],
        "building_type": prop["building_type"],
        "deal_type": prop.get("deal_type", "賃貸"),
        "image_url": prop.get("image_url", ""),
        "description": prop.get("description", ""),
        # ここから下は「物件条件」テーブル側の項目。
        "area": cond.get("area", ""),
        "layout": cond.get("layout", ""),
        "station_minutes": cond.get("station_minutes"),
        "pet_allowed": cond.get("pet_allowed", False),
    }


# ------------------------------------------------------------------
# 公開関数
# ------------------------------------------------------------------
def get_all_properties():
    """全物件を、物件条件と結合した平坦な dict のリストで返す。"""
    if config.SUPABASE_ENABLED:
        # PostgRESTの埋め込みで properties と property_conditions を一度に取得。
        rows = _rest_get("properties", {"select": "*,property_conditions(*)"})
        return [_flatten(r, r.get("property_conditions")) for r in rows]

    # モック時: 物件条件をID索引にしてから、各物件と結合する。
    by_id = {c["id"]: c for c in PROPERTY_CONDITIONS}
    return [_flatten(p, by_id.get(p["property_condition_id"])) for p in PROPERTIES]


def get_property(property_id: str):
    """物件IDで1件だけ取得する（結合済み）。該当が無ければ None。"""
    if config.SUPABASE_ENABLED:
        # id 完全一致で1件だけ取得（eq. は PostgREST の等価フィルタ）。
        rows = _rest_get("properties", {
            "id": f"eq.{property_id}",
            "select": "*,property_conditions(*)",
            "limit": 1,
        })
        if not rows:
            return None
        return _flatten(rows[0], rows[0].get("property_conditions"))

    # モック時: 全件を平坦化してからIDで線形探索（件数が少ないため十分）。
    for p in get_all_properties():
        if p["id"] == property_id:
            return p
    return None


def get_move_in_flow(deal_type: str):
    """取引種別（賃貸/購入）に対応する入居手続きフローを返す。

    入居フローはE-R図のテーブルではなく、取引種別から導く固定データ（定数）。
    """
    return MOVE_IN_FLOWS.get(deal_type, [])


def save_chat(question: str, answer: str):
    """チャットの1往復を chats テーブルへ保存する（Supabase接続時のみ）。"""
    if not config.SUPABASE_ENABLED:
        return   # モック時はDBが無いので何もしない。
    try:
        import requests
        url = config.SUPABASE_URL.rstrip("/") + "/rest/v1/chats"
        # Prefer=return=minimal: 挿入した行を返さない（応答を軽くする）。
        requests.post(url, headers=_headers({"Prefer": "return=minimal"}),
                      json={"question": question, "answer": answer}, timeout=15)
    except Exception:
        # 履歴保存はあくまで副次処理。失敗してもチャット表示は続けたいので握りつぶす。
        pass
