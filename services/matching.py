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


def _area_match(cond_area: str, prop_area: str) -> bool:
    """希望エリアに物件エリアが入っているか。希望は "新宿区/渋谷区" のような複数指定もあり。"""
    if not cond_area:
        return False
    wanted = [a.strip() for a in cond_area.replace("／", "/").split("/") if a.strip()]
    return prop_area in wanted


def _layout_match(cond_layout: str, prop_layout: str) -> bool:
    """希望間取りに物件の間取りが入っているか。大文字化して 1ldk と 1LDK の揺れを吸収する。"""
    if not cond_layout:
        return False
    wanted = [l.strip().upper() for l in cond_layout.replace("／", "/").split("/") if l.strip()]
    return prop_layout.upper() in wanted


def calculate_score(condition: dict, prop: dict) -> dict:
    """1物件の適合度を計算し、{"score", "breakdown"} を返す。

    breakdown は項目ごとの合否(bool)。あとでAIが「どこが合ってどこが外れたか」を
    説明するのに使うので、スコアと一緒に持ち回す。
    """
    budget = condition.get("budget")
    want_min = condition.get("station_minutes")
    want_pet = condition.get("pet_allowed")

    # 各条件を満たすか。満たした項目の重みだけを足していく。
    hit = {
        "area": _area_match(condition.get("area", ""), prop["area"]),
        "budget": budget is not None and prop["rent"] <= budget,
        "layout": _layout_match(condition.get("layout", ""), prop["layout"]),
        "station": want_min is not None and prop["station_minutes"] <= want_min,
        # ペットは「可の物件のみ希望」のときだけ問う。不問なら足を引っ張らないよう常にTrue。
        "pet": (not want_pet) or prop["pet_allowed"],
    }
    score = sum(WEIGHTS[key] for key, ok in hit.items() if ok)
    return {"score": score, "breakdown": hit}


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
        item["rank"] = rank_label(calc["score"])
        results.append(item)

    results.sort(key=lambda x: x["score"], reverse=True)
    return results
