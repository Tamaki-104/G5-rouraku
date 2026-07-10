"""
repository.py のドライバ（単体テスト・ホワイトボックス）。

repository.py は Supabase(PostgREST) に依存するため、Supabaseスタブ
(tests/stub_supabase.py)を差し込み、実DBを呼ばずに分岐を検証する。2モードを選べる。
  ・自動モード: モック経路 / Supabase正常 / 0件 / 取得失敗フォールバックの全項目を実行。
  ・手動モード: テスターが経路(モード)と関数を選び、通った分岐と戻り値を確認する。

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
from manual_helpers import ask_str, ask_bool, ask_choice

# スタブの差し込み：repository が内部で呼ぶ _rest_get をスタブへ置き換える。
repo._rest_get = stub.rest_get_stub


def head(no, desc):
    print(f"[項目{no}] {desc}")


def result(expected, actual):
    print(f"    期待 : {expected}")
    print(f"    戻り値: {actual}")
    print()


def _apply_mode(mode):
    """手動モードの経路選択を config / スタブへ反映する。"""
    if mode == "1":                         # モック
        config.SUPABASE_ENABLED = False
    else:                                   # Supabase（正常/0件/失敗）
        config.SUPABASE_ENABLED = True
        stub.mode = {"2": "rows", "3": "empty", "4": "raise"}[mode]


def run_auto():
    """モック / Supabase正常 / 0件 / 取得失敗フォールバックの全分岐を一括実行する。"""
    print("=" * 70)
    print(" repository.py 単体テスト（自動・全項目／Supabaseスタブ）")
    print("=" * 70)

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
    result("例外を捕捉しモックの『ホーム渋谷』へ", None if r is None else r["name"])

    print("=" * 70)
    print(" 以上6項目。各分岐が期待どおりに動くかを目視で判定し、相違はIssueへ。")
    print("=" * 70)


def run_manual():
    """テスターが経路と関数を選び、通った分岐と戻り値を確認する。"""
    print("=" * 70)
    print(" repository.py 手動テスト（経路と関数を選んで分岐を確認）")
    print("=" * 70)
    print(" [STUB Supabase]行が出れば実DB経路(スタブ)、出なければモック経路です。\n")

    while True:
        mode = ask_choice("経路を選択", [
            ("1", "モックデータ（SUPABASE_ENABLED=False）"),
            ("2", "Supabase正常（スタブが行を返す）"),
            ("3", "Supabase 0件（該当なし）"),
            ("4", "Supabase取得失敗（フォールバックを確認）"),
        ], "1")
        func = ask_choice("関数を選択", [
            ("1", "get_all_properties（全件取得）"),
            ("2", "get_property（ID指定で1件取得）"),
        ], "1")
        _apply_mode(mode)

        print("\n  ----- 実行 -----")
        if func == "1":
            r = repo.get_all_properties()
            summary = f"{len(r)}件" + (f" / 先頭={r[0]['name']}" if r else "")
        else:
            pid = ask_str("物件IDを入力", "PRP0000001")
            r = repo.get_property(pid)
            summary = "None（該当なし）" if r is None else f"{r['name']} / area={r['area']}"
        print("\n  ----- 結果 -----")
        print(f"  戻り値: {summary}")
        print()

        if not ask_bool("続けて別の経路でテストしますか", True):
            break
    print("テストを終了します。")


if __name__ == "__main__":
    print("repository.py ドライバ — モードを選んでください")
    print("  a) 自動（全項目を一括実行）")
    print("  m) 手動（経路・関数を選んで分岐を確認）")
    choice = input("選択 [a]: ").strip().lower()
    if choice == "m":
        run_manual()
    else:
        run_auto()
