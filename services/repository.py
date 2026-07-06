"""
データアクセス層。物件やチャットの読み書きを集約し、呼び出し側は
「Supabaseかモックか」を意識しない(config.SUPABASE_ENABLED により自動で切り替わる)。

Supabaseは supabase-py を使わず、PostgREST を requests で直接呼び出す。
新形式の publishable キーでも確実に通ること、依存が requests のみで済み
Vercel のサーバーレスが軽量になること、の2点が理由。

物件は E-R図どおり「物件条件」と「住宅情報」が別テーブルのため、PostgREST の
埋め込み(?select=*,property_conditions(*))で結合し、画面が扱いやすい平坦な dict に整形する。

作成: チーム労楽  /  (c) 2026 チーム労楽
"""
import config
from data.mock_data import (
    PROPERTY_CONDITIONS, PROPERTIES, MOVE_IN_FLOWS,
)


# --- Supabase REST ヘルパー ---

def _headers(extra=None):
    """PostgREST用の認証ヘッダを構築する。apikey と Authorization の両方にキーが必要。"""
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
    """GETして行の配列(JSON)を返す薄いラッパ。4xx/5xxはここで例外化する。"""
    import requests
    url = config.SUPABASE_URL.rstrip("/") + "/rest/v1/" + path
    r = requests.get(url, headers=_headers(), params=params, timeout=15)
    r.raise_for_status()
    return r.json()


# --- 結合して平坦化 ---

def _flatten(prop: dict, cond: dict) -> dict:
    """住宅情報 × 物件条件 を1つの dict に結合する。

    Supabase由来(ネスト)でもモック由来でも同一の形に揃え、画面とマッチングの
    処理を共通化する。結合相手が無くても落ちないよう空dictで受ける。
    """
    cond = cond or {}
    return {
        "id": prop["id"],
        "name": prop["name"],
        "rent": prop["rent"],
        "building_type": prop["building_type"],
        "deal_type": prop.get("deal_type", "賃貸"),
        "image_url": prop.get("image_url", ""),
        "description": prop.get("description", ""),
        # 以下は物件条件テーブル側の項目。
        "area": cond.get("area", ""),
        "layout": cond.get("layout", ""),
        "station_minutes": cond.get("station_minutes"),
        "pet_allowed": cond.get("pet_allowed", False),
    }


# --- 公開関数 ---

def _mock_all_properties():
    """モックデータから全物件を組み立てる。Supabase障害時のフォールバック先でもある。"""
    by_id = {c["id"]: c for c in PROPERTY_CONDITIONS}
    return [_flatten(p, by_id.get(p["property_condition_id"])) for p in PROPERTIES]


def get_all_properties():
    """全物件を、物件条件と結合した平坦な dict のリストで返す。

    Supabaseは無料プランでは無操作が続くと自動一時停止するため、
    取得に失敗した場合は画面を止めずモックデータへフォールバックする。
    """
    if config.SUPABASE_ENABLED:
        try:
            rows = _rest_get("properties", {"select": "*,property_conditions(*)"})
            return [_flatten(r, r.get("property_conditions")) for r in rows]
        except Exception:
            pass  # 以下のモックデータで代替
    return _mock_all_properties()


def get_property(property_id: str):
    """物件IDで1件のみ取得する(結合済み)。該当が無ければ None。

    get_all_properties と同様、Supabaseへの取得失敗時はモックデータで代替する。
    """
    if config.SUPABASE_ENABLED:
        try:
            rows = _rest_get("properties", {
                "id": f"eq.{property_id}",      # eq. はPostgRESTの完全一致フィルタ
                "select": "*,property_conditions(*)",
                "limit": 1,
            })
            if not rows:
                return None
            return _flatten(rows[0], rows[0].get("property_conditions"))
        except Exception:
            pass  # 以下のモックデータで代替

    # モックは件数が少ないため線形探索で十分。
    for p in _mock_all_properties():
        if p["id"] == property_id:
            return p
    return None


def get_move_in_flow(deal_type: str):
    """賃貸/購入それぞれの入居手順を返す。フローはDBではなく取引種別から導く固定データ。"""
    return MOVE_IN_FLOWS.get(deal_type, [])


def save_chat(question: str, answer: str):
    """チャット1往復を chats テーブルへ記録する(Supabase接続時のみ)。"""
    if not config.SUPABASE_ENABLED:
        return
    try:
        import requests
        url = config.SUPABASE_URL.rstrip("/") + "/rest/v1/chats"
        # return=minimal により挿入行を返さない(応答を軽量化)。
        requests.post(url, headers=_headers({"Prefer": "return=minimal"}),
                      json={"question": question, "answer": answer}, timeout=15)
    except Exception:
        # 記録は副次処理。失敗しても会話表示を止めないよう例外を無くす。
        pass
