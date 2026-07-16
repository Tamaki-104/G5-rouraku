"""
matching.py のドライバ（単体テスト・ホワイトボックス）。

matching.py は外部依存を持たない純ロジックのため、スタブは不要でドライバのみで
テストできる。実行時に2モードを選べる。
  ・自動モード: あらかじめ用意した全項目を一括実行し、期待値と戻り値を表示する。
  ・手動モード: テスターが希望条件・物件の引数を入力し、各条件の合否(分岐)を確認する。

実行: プロジェクト直下で  python tests/driver_matching.py

作成: チーム労楽  /  (c) 2026 チーム労楽
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)   # config / services
sys.path.insert(0, HERE)   # manual_helpers

from services import matching as m
from manual_helpers import ask_str, ask_int, ask_bool


def item(no, desc, args, expected, actual):
    """1テスト項目を、引数・期待値・実際の戻り値の形で表示する。"""
    print(f"[項目{no}] {desc}")
    print(f"    引数   : {args}")
    print(f"    期待値 : {expected}")
    print(f"    戻り値 : {actual}")
    print(f"    参考判定: {'一致' if actual == expected else '不一致（要確認）'}")
    print()


def run_auto():
    """あらかじめ用意した全項目を一括実行する（ホワイトボックス／全分岐）。"""
    print("=" * 70)
    print(" matching.py 単体テスト（自動・全項目）")
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

    # --- out_of_prefecture：県外判定の4分岐（希望都道府県 vs 物件の都道府県）---
    item(6, "out_of_prefecture：同一都道府県は県外でない（偽）",
         '"東京都","東京都"', False, m.out_of_prefecture("東京都", "東京都"))
    item(7, "out_of_prefecture：別の都道府県は県外（真）",
         '"東京都","神奈川県"', True, m.out_of_prefecture("東京都", "神奈川県"))
    item(8, "out_of_prefecture：希望の都道府県が空なら判定不能→県外にしない（偽）",
         '"","東京都"', False, m.out_of_prefecture("", "東京都"))
    item(9, "out_of_prefecture：物件の都道府県が空なら判定不能→県外にしない（偽）",
         '"東京都",""', False, m.out_of_prefecture("東京都", ""))

    # --- calculate_score：全一致 / 各項目ミス / 県外0% ---
    cond = {"prefecture": "東京都", "area": "渋谷区", "budget": 70000,
            "layout": "1LDK", "station_minutes": 20, "pet_allowed": True}
    prop_full = {"prefecture": "東京都", "area": "渋谷区", "rent": 60000,
                 "layout": "1LDK", "station_minutes": 15, "pet_allowed": True}
    r = m.calculate_score(cond, prop_full)
    item(10, "calculate_score：全項目一致は100点・県外でない",
         "cond=渋谷/7万/1LDK/20分/ペット可, prop=一致",
         "{'score':100, 'out_of_area':False}",
         f"{{'score':{r['score']}, 'out_of_area':{r['out_of_area']}}}")

    prop_over = {"prefecture": "東京都", "area": "渋谷区", "rent": 90000,
                 "layout": "1LDK", "station_minutes": 15, "pet_allowed": True}
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

    prop_out = {"prefecture": "神奈川県", "area": "横浜区", "rent": 60000,
                "layout": "1LDK", "station_minutes": 15, "pet_allowed": True}
    r = m.calculate_score(cond, prop_out)
    item(13, "calculate_score：県外物件は強制0%",
         "cond=東京都/渋谷区, prop=神奈川県/横浜区", "{'score':0, 'out_of_area':True}",
         f"{{'score':{r['score']}, 'out_of_area':{r['out_of_area']}}}")

    # --- rank_label：境界値 70 / 40 ---
    item(14, "rank_label：境界70は『高い』", "70", "高い", m.rank_label(70))
    item(15, "rank_label：境界40は『普通』", "40", "普通", m.rank_label(40))
    item(16, "rank_label：39は『低い』", "39", "低い", m.rank_label(39))

    # --- match_properties：降順ソート・元データ非破壊 ---
    props = [dict(prop_full, id="A"), dict(prop_over, id="B")]
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


def run_manual():
    """テスターが引数を入力し、各条件の合否(分岐)と適合度を確認する。"""
    print("=" * 70)
    print(" matching.py 手動テスト（引数を入力して分岐を確認）")
    print("=" * 70)
    print(" ヒント: 物件の都道府県を『神奈川県』にすると県外分岐(適合度0%)を確認できます。")
    print("         予算より高い家賃、希望と違う間取り等で各項目の合否が変わります。\n")

    while True:
        print("[希望条件を入力]")
        cond = {
            "prefecture": ask_str("希望都道府県", "東京都"),
            "area": ask_str("希望エリア(地区)", "渋谷区"),
            "budget": ask_int("予算上限(円)", 70000),
            "layout": ask_str("希望間取り", "1LDK"),
            "station_minutes": ask_int("駅からの距離(分以内)", 20),
            "pet_allowed": ask_bool("ペット可の物件のみ希望", False),
        }
        print("[物件を入力]")
        prop = {
            "prefecture": ask_str("物件の都道府県", "東京都"),
            "area": ask_str("物件エリア(地区)", "渋谷区"),
            "rent": ask_int("物件の家賃(円)", 60000),
            "layout": ask_str("物件の間取り", "1LDK"),
            "station_minutes": ask_int("物件の駅からの距離(分)", 15),
            "pet_allowed": ask_bool("物件はペット可か", True),
        }

        calc = m.calculate_score(cond, prop)
        bd = calc["breakdown"]
        print("\n  ----- 結果 -----")
        print(f"  適合度       : {calc['score']}%  （順位: {m.rank_label(calc['score'])}）")
        print(f"  県外判定     : {calc['out_of_area']}")
        print("  各条件の合否（＝通った分岐）:")
        labels = {"area": "エリア", "budget": "予算", "layout": "間取り",
                  "station": "駅距離", "pet": "ペット"}
        for key in ("area", "budget", "layout", "station", "pet"):
            print(f"    {labels[key]:6s}: {bd[key]}")
        print()

        if not ask_bool("続けて別の引数でテストしますか", True):
            break
    print("テストを終了します。")


if __name__ == "__main__":
    print("matching.py ドライバ — モードを選んでください")
    print("  a) 自動（全項目を一括実行）")
    print("  m) 手動（引数を入力して分岐を確認）")
    choice = input("選択 [a]: ").strip().lower()
    if choice == "m":
        run_manual()
    else:
        run_auto()
