"""
repository.py のドライバ（単体テスト・ホワイトボックス）。

repository.py は Supabase(PostgREST) に依存するため、Supabaseスタブ
(tests/stub_supabase.py)を差し込み、実DBを呼ばずに分岐を検証する。
config.SUPABASE_ENABLED とスタブのモードを切り替え、「モック経路」「Supabase正常取得」
「取得0件」「取得失敗→モックへフォールバック」の各パスを通す。

実行: プロジェクト直下で  python tests/driver_repository.py

作成: チーム労楽  /  (c) 2026 チーム労楽
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

import config
from services import repository as repo
import stub_supabase as stub

# スタブの差し込み：repository が内部で呼ぶ _rest_get をスタブへ置き換える。
repo._rest_get = stub.rest_get_stub


def head(no, desc):
    print(f"[項目{no}] {desc}")


def result(expected, actual):
    print(f"    期待 : {expected}")
    print(f"    戻り値: {actual}")
    print()


print("=" * 70)
print(" repository.py 単体テスト（ドライバ＋Supabaseスタブ）")
print("=" * 70)

# --- get_all_properties の3分岐 ---
head(1, "get_all_properties / SUPABASE_ENABLED=False → モックデータ全件")
config.SUPABASE_ENABLED = False
r = repo.get_all_properties()
result("モックの物件9件（スタブは呼ばれない）", f"{len(r)}件 / 先頭={r[0]['name']}")

head(2, "get_all_properties / SUPABASE有効・正常 → スタブ行を整形して返す")
config.SUPABASE_ENABLED = True
stub.mode = "rows"
r = repo.get_all_properties()
result("スタブ物件1件（エリア等が平坦化されている）",
       f"{len(r)}件 / 先頭={r[0]['name']} / area={r[0]['area']}")

head(3, "get_all_properties / SUPABASE有効・取得失敗 → モックへフォールバック")
config.SUPABASE_ENABLED = True
stub.mode = "raise"
r = repo.get_all_properties()
result("例外を捕捉しモック9件へ切替", f"{len(r)}件 / 先頭={r[0]['name']}")

# --- get_property の分岐 ---
head(4, "get_property / SUPABASE有効・該当あり → 1件を平坦化")
config.SUPABASE_ENABLED = True
stub.mode = "rows"
r = repo.get_property("PRP_STUB01")
result("スタブ物件dict（name/area等を含む）",
       None if r is None else f"{r['name']} / area={r['area']}")

head(5, "get_property / SUPABASE有効・該当なし(0件) → None")
config.SUPABASE_ENABLED = True
stub.mode = "empty"
r = repo.get_property("PRP_NOTEXIST")
result("None", r)

head(6, "get_property / SUPABASE有効・取得失敗 → モックから検索")
config.SUPABASE_ENABLED = True
stub.mode = "raise"
r = repo.get_property("PRP0000001")
result("例外を捕捉しモックの『ホーム渋谷』へ",
       None if r is None else r["name"])

print("=" * 70)
print(" 以上6項目。各分岐が期待どおりに動くかを目視で判定し、相違はIssueへ。")
print("=" * 70)
