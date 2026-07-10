"""
matching.py のドライバ（単体テスト・ホワイトボックス）。

matching.py は外部依存を持たない純ロジックのため、スタブは不要でドライバのみで
テストできる。各関数の分岐（真偽両方・境界値）を通すよう項目を並べ、引数と戻り値を
表示する。合否は仕様と照らして手作業で判定する（期待値も併記）。

実行: プロジェクト直下で  python tests/driver_matching.py

作成: チーム労楽  /  (c) 2026 チーム労楽
"""
import os
import sys

# config / services を import するためプロジェクト直下を検索パスへ。
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from services import matching as m


def item(no, desc, args, expected, actual):
    """1テスト項目を、引数・期待値・実際の戻り値の形で表示する。"""
    print(f"[項目{no}] {desc}")
    print(f"    引数   : {args}")
    print(f"    期待値 : {expected}")
    print(f"    戻り値 : {actual}")
    print(f"    参考判定: {'一致' if actual == expected else '不一致（要確認）'}")
    print()


print("=" * 70)
print(" matching.py 単体テスト（ドライバ／スタブ不要）")
print("=" * 70)

# --- split_multi：区切り分解 ---
item(1, "split_multi：空文字は空リスト", '""', [], m.split_multi(""))
item(2, "split_multi：全角／と半角/を正規化して分解",
     '"新宿区／渋谷区"', ["新宿区", "渋谷区"], m.split_multi("新宿区／渋谷区"))

# --- _area_match：エリア一致（真偽両方）---
item(3, "_area_match：複数希望のいずれかに一致（真）",
     'cond="新宿区/渋谷区", prop="渋谷区"', True,
     m._area_match("新宿区/渋谷区", "渋谷区"))
item(4, "_area_match：一致しない（偽）",
     'cond="新宿区", prop="渋谷区"', False, m._area_match("新宿区", "渋谷区"))

# --- _layout_match：大文字化で表記揺れ吸収 ---
item(5, "_layout_match：小文字1ldkでも一致（真）",
     'cond="1ldk", prop="1LDK"', True, m._layout_match("1ldk", "1LDK"))

# --- out_of_prefecture：県外判定の4分岐 ---
item(6, "out_of_prefecture：同一都道府県は県外でない（偽）",
     '"渋谷区","池袋区"', False, m.out_of_prefecture("渋谷区", "池袋区"))
item(7, "out_of_prefecture：別の都道府県は県外（真）",
     '"渋谷区","横浜区"', True, m.out_of_prefecture("渋谷区", "横浜区"))
item(8, "out_of_prefecture：希望エリア不明は判定不能→県外にしない（偽）",
     '"大阪市","渋谷区"', False, m.out_of_prefecture("大阪市", "渋谷区"))
item(9, "out_of_prefecture：物件エリア不明は判定不能→県外にしない（偽）",
     '"渋谷区","大阪市"', False, m.out_of_prefecture("渋谷区", "大阪市"))

# --- calculate_score：全一致 / 各項目ミス / 県外0% ---
cond = {"area": "渋谷区", "budget": 70000, "layout": "1LDK",
        "station_minutes": 20, "pet_allowed": True}
prop_full = {"area": "渋谷区", "rent": 60000, "layout": "1LDK",
             "station_minutes": 15, "pet_allowed": True}
r = m.calculate_score(cond, prop_full)
item(10, "calculate_score：全項目一致は100点・県外でない",
     "cond=渋谷/7万/1LDK/20分/ペット可, prop=一致",
     "{'score':100, 'out_of_area':False}",
     f"{{'score':{r['score']}, 'out_of_area':{r['out_of_area']}}}")

prop_over = {"area": "渋谷区", "rent": 90000, "layout": "1LDK",
             "station_minutes": 15, "pet_allowed": True}
r = m.calculate_score(cond, prop_over)
item(11, "calculate_score：予算超過は budget を外す（100-25=75）",
     "prop.rent=90000 > budget=70000", "{'score':75, budget:False}",
     f"{{'score':{r['score']}, budget:{r['breakdown']['budget']}}}")

cond_pet_ok = dict(cond, pet_allowed=False)
prop_pet_ng = dict(prop_full, pet_allowed=False)
r = m.calculate_score(cond_pet_ok, prop_pet_ng)
item(12, "calculate_score：ペット不問なら物件不可でも加点（pet=True）",
     "cond.pet_allowed=False, prop.pet=False", "pet:True",
     f"pet:{r['breakdown']['pet']}")

prop_out = {"area": "横浜区", "rent": 60000, "layout": "1LDK",
            "station_minutes": 15, "pet_allowed": True}
r = m.calculate_score(cond, prop_out)
item(13, "calculate_score：県外物件は強制0%",
     "cond=渋谷(東京), prop=横浜(神奈川)", "{'score':0, 'out_of_area':True}",
     f"{{'score':{r['score']}, 'out_of_area':{r['out_of_area']}}}")

# --- rank_label：境界値 70 / 40 ---
item(14, "rank_label：境界70は『高い』", "70", "高い", m.rank_label(70))
item(15, "rank_label：境界40は『普通』", "40", "普通", m.rank_label(40))
item(16, "rank_label：39は『低い』", "39", "低い", m.rank_label(39))

# --- match_properties：降順ソート・元データ非破壊 ---
props = [dict(prop_full, id="A"), dict(prop_over, id="B")]
before = props[0].copy()          # 破壊されていないか確認するための控え
ranked = m.match_properties(cond, props)
item(17, "match_properties：適合度の高い順に並ぶ",
     "A(100点), B(75点)", ["A", "B"],
     [p["id"] for p in ranked])
item(18, "match_properties：元の物件dictを変更しない（scoreキーが増えない）",
     "props[0] に score を書き込まないこと", "score無し（元のまま）",
     "score有り（破壊）" if "score" in props[0] else "score無し（元のまま）")

print("=" * 70)
print(" 以上18項目。『参考判定』が全て一致なら合格。不一致はGitHub Issueへ。")
print("=" * 70)
