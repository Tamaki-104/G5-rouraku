"""
マッチングエンジン。希望条件と物件を照合して「適合度」(0〜100%)を出し、高い順に並べる。

考え方はシンプルで、5項目それぞれに重みを持たせ、満たした項目の重みを足すだけ。
重みの合計が100なので、そのまま「何%合っているか」になる。部分点は付けない。

作成: チーム労楽  /  (c) 2026 チーム労楽
"""

# 項目ごとの重み(合計100)。この数字の大小が、そのまま「何を重視するか」。
WEIGHTS = {
    "area": 30,
    "budget": 25,
    "layout": 20,
    "station": 15,
    "pet": 10,
}

# エリア名 -> 都道府県。県外判定に使う。
# 物件提案では希望エリアを最優先とし、入力エリアと違う県の物件は適合率0%で足切りする。
# ※サンプルデータの架空区(池袋区・秋葉原区)も便宜上ここで都道府県に紐付けておく。
AREA_PREFECTURES = {
    "渋谷区": "東京都",
    "新宿区": "東京都",
    "池袋区": "東京都",
    "秋葉原区": "東京都",
    "横浜区": "神奈川県",
}


def out_of_prefecture(cond_area: str, prop_area: str) -> bool:
    """物件が、希望エリアから見て「県外」かどうか。

    入力エリアそれぞれの都道府県を集め、物件の都道府県がそのどれにも
    入っていなければ県外。入力・物件のどちらかから都道府県が特定できない
    場合は判定不能なので県外扱いにはしない(誤って全滅させないため)。
    """
    wanted_prefs = {AREA_PREFECTURES[a] for a in split_multi(cond_area)
                    if a in AREA_PREFECTURES}
    prop_pref = AREA_PREFECTURES.get(prop_area)
    if not wanted_prefs or prop_pref is None:
        return False
    return prop_pref not in wanted_prefs


def split_multi(value: str) -> list:
    """"新宿区/渋谷区" のような「/」区切りの複数指定を分解する(全角／も半角に寄せる)。"""
    if not value:
        return []
    return [v.strip() for v in value.replace("／", "/").split("/") if v.strip()]


def _area_match(cond_area: str, prop_area: str) -> bool:
    """希望エリア(複数可)に物件エリアが含まれるか。"""
    return prop_area in split_multi(cond_area)


def _layout_match(cond_layout: str, prop_layout: str) -> bool:
    """希望間取り(複数可)に物件の間取りが含まれるか。1ldk/1LDK の揺れは大文字化で吸収。"""
    return prop_layout.upper() in [x.upper() for x in split_multi(cond_layout)]


def calculate_score(condition: dict, prop: dict) -> dict:
    """1物件の適合度を計算し、{"score", "breakdown"} を返す。

    breakdown は項目ごとの合否(bool)。あとでAIが「どこが合ってどこが外れたか」を
    説明するのに使うので、スコアと一緒に持ち回す。
    """
    budget = condition.get("budget")
    want_min = condition.get("station_minutes")
    want_pet = condition.get("pet_allowed")

    hit = {
        "area": _area_match(condition.get("area", ""), prop["area"]),
        "budget": budget is not None and prop["rent"] <= budget,
        "layout": _layout_match(condition.get("layout", ""), prop["layout"]),
        "station": want_min is not None and prop["station_minutes"] <= want_min,
        # ペットは「可の物件のみ希望」のときだけ問う。不問なら足を引っ張らないよう常にTrue。
        "pet": (not want_pet) or prop["pet_allowed"],
    }
    score = sum(WEIGHTS[key] for key, ok in hit.items() if ok)

    # 希望エリアは最重要条件。県外の物件は他の項目がいくら合っていても
    # 提案する意味がないので、適合率を強制的に0%へ落とす(一覧からも除外される)。
    out_of_area = out_of_prefecture(condition.get("area", ""), prop["area"])
    if out_of_area:
        score = 0

    return {"score": score, "breakdown": hit, "out_of_area": out_of_area}


def rank_label(score: int) -> str:
    """適合度をひと目で分かる3段階に。設計書の「高い/普通」に「低い」を足した。"""
    if score >= 70:
        return "高い"
    if score >= 40:
        return "普通"
    return "低い"


def match_properties(condition: dict, properties: list) -> list:
    """全物件を採点し、適合度の高い順で返す。画面はこの並びをそのまま出せばよい。"""
    results = []
    for prop in properties:
        calc = calculate_score(condition, prop)
        # 元データを汚さないよう複製してから採点結果を足す。
        item = dict(prop)
        item["score"] = calc["score"]
        item["breakdown"] = calc["breakdown"]
        item["out_of_area"] = calc["out_of_area"]
        item["rank"] = rank_label(calc["score"])
        results.append(item)

    results.sort(key=lambda x: x["score"], reverse=True)
    return results
