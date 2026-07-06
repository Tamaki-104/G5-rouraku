"""
マッチングエンジン。希望条件と物件を照合して「適合度」(0〜100%)を算出し、高い順に並べる。

5項目それぞれに重みを持たせ、満たした項目の重みを合算する方式。
重みの合計は100であり、そのまま適合度(%)となる。部分点は設けない。

作成: チーム労楽  /  (c) 2026 チーム労楽
"""

# 項目ごとの重み(合計100)。この配分が「何を重視するか」を表す。
WEIGHTS = {
    "area": 30,
    "budget": 25,
    "layout": 20,
    "station": 15,
    "pet": 10,
}

# エリア名 -> 都道府県。県外判定に使用する。
# 物件提案では希望エリアを最優先とし、入力エリアと異なる県の物件は適合率0%で除外する。
# ※サンプルデータの架空区(池袋区・秋葉原区)も便宜上ここで都道府県に紐付ける。
AREA_PREFECTURES = {
    "渋谷区": "東京都",
    "新宿区": "東京都",
    "池袋区": "東京都",
    "秋葉原区": "東京都",
    "横浜区": "神奈川県",
}


def out_of_prefecture(cond_area: str, prop_area: str) -> bool:
    """物件が、希望エリアから見て県外か否かを判定する。

    入力エリアそれぞれの都道府県を集合とし、物件の都道府県がそのいずれにも
    含まれなければ県外とする。入力・物件のどちらかから都道府県を特定できない
    場合は判定不能とし、県外扱いにはしない(誤って全件除外しないため)。
    """
    wanted_prefs = {AREA_PREFECTURES[a] for a in split_multi(cond_area)
                    if a in AREA_PREFECTURES}
    prop_pref = AREA_PREFECTURES.get(prop_area)
    if not wanted_prefs or prop_pref is None:
        return False
    return prop_pref not in wanted_prefs


def split_multi(value: str) -> list:
    """"新宿区/渋谷区" のような「/」区切りの複数指定を分解する(全角／は半角に正規化)。"""
    if not value:
        return []
    return [v.strip() for v in value.replace("／", "/").split("/") if v.strip()]


def _area_match(cond_area: str, prop_area: str) -> bool:
    """希望エリア(複数可)に物件エリアが含まれるかを判定する。"""
    return prop_area in split_multi(cond_area)


def _layout_match(cond_layout: str, prop_layout: str) -> bool:
    """希望間取り(複数可)に物件の間取りが含まれるかを判定する。大文字化で表記揺れを吸収する。"""
    return prop_layout.upper() in [x.upper() for x in split_multi(cond_layout)]


def calculate_score(condition: dict, prop: dict) -> dict:
    """1物件の適合度を計算し、{"score", "breakdown", "out_of_area"} を返す。

    breakdown は項目ごとの合否(bool)。AIの課題分析で「どの条件を満たし、
    どの条件を外したか」を説明するために、スコアと併せて保持する。
    out_of_area が真の物件は score を0とし、提案一覧から除外される。
    """
    budget = condition.get("budget")
    want_min = condition.get("station_minutes")
    want_pet = condition.get("pet_allowed")

    hit = {
        "area": _area_match(condition.get("area", ""), prop["area"]),
        "budget": budget is not None and prop["rent"] <= budget,
        "layout": _layout_match(condition.get("layout", ""), prop["layout"]),
        "station": want_min is not None and prop["station_minutes"] <= want_min,
        # ペットは「可の物件のみ希望」の場合のみ問う。不問なら常にTrue(減点対象としない)。
        "pet": (not want_pet) or prop["pet_allowed"],
    }
    score = sum(WEIGHTS[key] for key, ok in hit.items() if ok)

    # 希望エリアは最重要条件。県外の物件は他項目が合致していても提案対象とせず、
    # 適合率を強制的に0%へ落とす(一覧からも除外される)。
    out_of_area = out_of_prefecture(condition.get("area", ""), prop["area"])
    if out_of_area:
        score = 0

    return {"score": score, "breakdown": hit, "out_of_area": out_of_area}


def rank_label(score: int) -> str:
    """適合度を3段階のラベルへ変換する。設計書の「高い/普通」に「低い」を補う。"""
    if score >= 70:
        return "高い"
    if score >= 40:
        return "普通"
    return "低い"


def match_properties(condition: dict, properties: list) -> list:
    """全物件を採点し、適合度の高い順に並べて返す。画面はこの並びをそのまま描画できる。"""
    results = []
    for prop in properties:
        calc = calculate_score(condition, prop)
        # 呼び出し元のデータを変更しないよう複製してから採点結果を付与する。
        item = dict(prop)
        item["score"] = calc["score"]
        item["breakdown"] = calc["breakdown"]
        item["out_of_area"] = calc["out_of_area"]
        item["rank"] = rank_label(calc["score"])
        results.append(item)

    results.sort(key=lambda x: x["score"], reverse=True)
    return results
