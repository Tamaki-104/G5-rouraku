"""
AIマッチングエンジン（設計書「AIマッチングエンジン クラス」）。

希望条件と各物件を照合し、適合度（0〜100%）を計算してソートする。
項目ごとの重み合計が100になるよう設計。
"""

# 各項目の重み（合計100）
WEIGHTS = {
    "area": 30,       # エリア一致
    "budget": 25,     # 予算内（家賃 <= 予算上限）
    "layout": 20,     # 間取り一致
    "station": 15,    # 駅からの距離条件を満たす
    "pet": 10,        # ペット条件を満たす
}


def _area_match(cond_area: str, prop_area: str) -> bool:
    """希望エリアは "新宿区/渋谷区" のように複数指定があり得る。"""
    if not cond_area:
        return False
    wanted = [a.strip() for a in cond_area.replace("／", "/").split("/") if a.strip()]
    return prop_area in wanted


def _layout_match(cond_layout: str, prop_layout: str) -> bool:
    """希望間取りも "1LDK/2LDK" のような複数指定があり得る。"""
    if not cond_layout:
        return False
    wanted = [l.strip().upper() for l in cond_layout.replace("／", "/").split("/") if l.strip()]
    return prop_layout.upper() in wanted


def calculate_score(condition: dict, prop: dict) -> dict:
    """
    1物件の適合度を計算し、内訳付きで返す。
    condition: {area, budget, layout, station_minutes, pet_allowed}
    """
    breakdown = {}
    score = 0

    # エリア
    if _area_match(condition.get("area", ""), prop["area"]):
        score += WEIGHTS["area"]
        breakdown["area"] = True
    else:
        breakdown["area"] = False

    # 予算（家賃が予算上限以下なら満たす）
    budget = condition.get("budget")
    if budget is not None and prop["rent"] <= budget:
        score += WEIGHTS["budget"]
        breakdown["budget"] = True
    else:
        breakdown["budget"] = False

    # 間取り
    if _layout_match(condition.get("layout", ""), prop["layout"]):
        score += WEIGHTS["layout"]
        breakdown["layout"] = True
    else:
        breakdown["layout"] = False

    # 駅からの距離（物件の徒歩分数 <= 希望分数以内なら満たす）
    want_min = condition.get("station_minutes")
    if want_min is not None and prop["station_minutes"] <= want_min:
        score += WEIGHTS["station"]
        breakdown["station"] = True
    else:
        breakdown["station"] = False

    # ペット（希望がペット可なら、物件もペット可である必要がある。希望が不問なら常に満たす）
    want_pet = condition.get("pet_allowed")
    if not want_pet or prop["pet_allowed"]:
        score += WEIGHTS["pet"]
        breakdown["pet"] = True
    else:
        breakdown["pet"] = False

    return {"score": score, "breakdown": breakdown}


def rank_label(score: int) -> str:
    """適合度の順位ラベル（設計書: 高い/普通 ＋ 低い を補完）。"""
    if score >= 70:
        return "高い"
    if score >= 40:
        return "普通"
    return "低い"


def match_properties(condition: dict, properties: list) -> list:
    """
    全物件の適合度を計算し、降順ソートして返す。
    各要素に score / breakdown / rank を付与。
    """
    results = []
    for prop in properties:
        calc = calculate_score(condition, prop)
        item = dict(prop)
        item["score"] = calc["score"]
        item["breakdown"] = calc["breakdown"]
        item["rank"] = rank_label(calc["score"])
        results.append(item)

    results.sort(key=lambda x: x["score"], reverse=True)
    return results
