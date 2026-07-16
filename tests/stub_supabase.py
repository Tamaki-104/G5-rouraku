"""
Supabaseスタブ。repository.py が依存する _rest_get の代役。

実際のSupabase(PostgREST)へアクセスせず、モードに応じて行データを返す、空を返す、
または例外を送出する。呼び出し・引数・戻り値をすべて表示する（授業資料10.6準拠）。
repository.py 側の「Supabase正常取得」「取得0件」「取得失敗→モックへフォールバック」を
切り分けて検証できる。

作成: チーム労楽  /  (c) 2026 チーム労楽
"""

# 戻り値の切替。ドライバがテスト項目ごとに設定する。
#   "rows"  : Supabase由来の行(ネスト構造)を返す
#   "empty" : 0件([])を返す（該当なしを模擬）
#   "raise" : 取得失敗を模擬して例外を送出（フォールバックを検証）
mode = "rows"

# Supabaseが返す形（住宅情報に物件条件がネストされた構造）を模した固定行。
FAKE_ROWS = [
    {
        "id": "PRP_STUB01", "name": "スタブ物件A", "rent": 50000,
        "building_type": "マンション", "deal_type": "賃貸",
        "image_url": "", "description": "スタブ物件A",
        "property_conditions": {
            "prefecture": "東京都", "area": "渋谷区", "layout": "1LDK",
            "station_minutes": 12, "pet_allowed": True,
        },
    },
]


def rest_get_stub(path, params=None):
    """repository._rest_get と同じ引数・戻り値の型で振る舞う代役。"""
    print("    [STUB Supabase] _rest_get が呼び出された")
    print(f"    [STUB Supabase]   引数 path = {path!r} / params = {params!r}")
    print(f"    [STUB Supabase]   モード = {mode}")
    if mode == "raise":
        print("    [STUB Supabase]   → 例外を送出（取得失敗を模擬）")
        raise ConnectionError("スタブ: Supabase 取得失敗を模擬")
    rows = [] if mode == "empty" else FAKE_ROWS
    print(f"    [STUB Supabase]   → 戻り値 = {rows!r}")
    return rows
