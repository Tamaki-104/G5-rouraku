"""
AIマッチングエンジン（設計書「AIマッチングエンジン クラス」相当）。

概要:
    ユーザーの希望条件と各物件を項目ごとに突き合わせ、どれだけ合致するかを
    0〜100%の「適合度」として数値化する。5項目の重み合計が100になるよう設計し、
    合致した項目の重みを加算する（部分点は設けず、満たすか満たさないかの二択）。
    最後に適合度の高い順へ並べ替えて提案の順位付けに使う。

作成    : チーム労楽
Copyright (c) 2026 チーム労楽. All rights reserved.
"""

# 各項目の重み（合計100）。この配分がそのまま「どの条件を重視するか」を表す。
WEIGHTS = {
    "area": 30,       # エリア一致を最重視
    "budget": 25,     # 予算内（家賃 <= 予算上限）
    "layout": 20,     # 間取り一致
    "station": 15,    # 駅からの距離条件を満たす
    "pet": 10,        # ペット条件を満たす
}


def _area_match(cond_area: str, prop_area: str) -> bool:
    """希望エリアに物件のエリアが含まれるか判定する。

    希望は "新宿区/渋谷区" のように「/」区切りで複数指定され得るため、
    分解したいずれかに一致すれば合致とみなす（全角「／」も半角に正規化）。
    """
    if not cond_area:
        return False
    wanted = [a.strip() for a in cond_area.replace("／", "/").split("/") if a.strip()]
    return prop_area in wanted


def _layout_match(cond_layout: str, prop_layout: str) -> bool:
    """希望間取りに物件の間取りが含まれるか判定する。

    間取りも "1LDK/2LDK" のように複数指定され得る。表記ゆれを避けるため
    大文字化して比較する（例: 1ldk と 1LDK を同一視）。
    """
    if not cond_layout:
        return False
    wanted = [l.strip().upper() for l in cond_layout.replace("／", "/").split("/") if l.strip()]
    return prop_layout.upper() in wanted


def calculate_score(condition: dict, prop: dict) -> dict:
    """1物件の適合度を算出し、スコアと項目ごとの合否内訳を返す。

    condition: {area, budget, layout, station_minutes, pet_allowed}
    戻り値   : {"score": int(0-100), "breakdown": {項目名: bool}}
    breakdown は後段のAI課題分析で「どの条件を満たし/外したか」を説明するのに使う。
    """
    breakdown = {}   # 各項目を満たしたか（True/False）。加点理由の記録も兼ねる。
    score = 0

    # エリア: 希望エリア（複数可）に含まれれば加点。
    if _area_match(condition.get("area", ""), prop["area"]):
        score += WEIGHTS["area"]
        breakdown["area"] = True
    else:
        breakdown["area"] = False

    # 予算: 家賃が予算上限以下に収まっていれば加点。
    budget = condition.get("budget")
    if budget is not None and prop["rent"] <= budget:
        score += WEIGHTS["budget"]
        breakdown["budget"] = True
    else:
        breakdown["budget"] = False

    # 間取り: 希望間取り（複数可）に含まれれば加点。
    if _layout_match(condition.get("layout", ""), prop["layout"]):
        score += WEIGHTS["layout"]
        breakdown["layout"] = True
    else:
        breakdown["layout"] = False

    # 駅からの距離: 物件の徒歩分数が希望の上限（分）以内なら加点。
    want_min = condition.get("station_minutes")
    if want_min is not None and prop["station_minutes"] <= want_min:
        score += WEIGHTS["station"]
        breakdown["station"] = True
    else:
        breakdown["station"] = False

    # ペット: 「ペット可のみ希望」なら物件もペット可である必要がある。
    # 希望が不問（want_pet が偽）の場合はこの条件で減点しないため常に加点。
    want_pet = condition.get("pet_allowed")
    if not want_pet or prop["pet_allowed"]:
        score += WEIGHTS["pet"]
        breakdown["pet"] = True
    else:
        breakdown["pet"] = False

    return {"score": score, "breakdown": breakdown}


def rank_label(score: int) -> str:
    """適合度を人が読みやすい3段階ラベルに変換する。

    設計書の「高い/普通」に、実用上必要な「低い」を補って3段階にしている。
    """
    if score >= 70:
        return "高い"
    if score >= 40:
        return "普通"
    return "低い"


def match_properties(condition: dict, properties: list) -> list:
    """全物件の適合度を計算し、高い順に並べ替えた一覧を返す。

    元の物件dictを壊さないよう複製し、score / breakdown / rank を付け足す。
    戻り値は提案画面がそのまま描画できる形（適合度降順）。
    """
    results = []
    for prop in properties:
        calc = calculate_score(condition, prop)
        item = dict(prop)   # 呼び出し元の物件データを変更しないための複製。
        item["score"] = calc["score"]
        item["breakdown"] = calc["breakdown"]
        item["rank"] = rank_label(calc["score"])
        results.append(item)

    # 適合度の高い物件ほど上に来るよう降順ソートする。
    results.sort(key=lambda x: x["score"], reverse=True)
    return results
