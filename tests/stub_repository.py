"""
repositoryスタブ。favorites.py が依存する repository.get_property の代役。

実際のデータ層(Supabase/モック)を呼ばず、モードに応じて固定の物件dictを返す、
またはNone(該当なし)を返す。呼び出し・引数・戻り値をすべて表示する（授業資料10.6準拠）。
favorites.py 側の「一覧に物件を並べる」「存在しないIDを除外する」を切り分けて検証できる。

作成: チーム労楽  /  (c) 2026 チーム労楽
"""

# 戻り値の切替。ドライバがテスト項目ごとに設定する。
#   "found"    : 物件dictを返す
#   "not_found": None を返す（削除済み等を模擬）
mode = "found"

FAKE_PROPERTY = {
    "id": "PRP_STUB01", "name": "スタブ物件A", "rent": 50000,
    "building_type": "マンション", "deal_type": "賃貸",
    "image_url": "", "description": "スタブ物件A",
    "area": "渋谷区", "layout": "1LDK", "station_minutes": 12, "pet_allowed": True,
}


def get_property_stub(property_id):
    """repository.get_property と同じ引数・戻り値の型で振る舞う代役。"""
    print("    [STUB repository] get_property が呼び出された")
    print(f"    [STUB repository]   引数 property_id = {property_id!r} / モード = {mode}")
    if mode == "not_found":
        print("    [STUB repository]   → 戻り値 = None")
        return None
    # 要求されたIDを反映した物件を返す（一覧表示の確認用）。
    prop = dict(FAKE_PROPERTY, id=property_id)
    print(f"    [STUB repository]   → 戻り値 = {prop!r}")
    return prop
