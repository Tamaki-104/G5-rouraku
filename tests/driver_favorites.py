"""
favorites.py のドライバ（単体テスト・ホワイトボックス）。

favorites.py は repository.get_property と Flaskセッションに依存する。
repositoryスタブ(tests/stub_repository.py)で実DBを切り離し、Flaskの test_client を
ドライバとして用いてセッションを扱う。2モードを選べる。
  ・自動モード: 400 / 追加 / 解除 / 空一覧 / 一覧表示 / 存在しないID除外を一括実行。
  ・手動モード: テスターが操作(登録・解除・一覧)とスタブ物件の有無を選び、分岐を確認する。

実行: プロジェクト直下で  python tests/driver_favorites.py

作成: チーム労楽  /  (c) 2026 チーム労楽
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

from app import app
from services import repository
import stub_repository as stub
from manual_helpers import ask_str, ask_bool, ask_choice

# スタブの差し込み：favorites が呼ぶ repository.get_property をスタブへ置き換える。
repository.get_property = stub.get_property_stub


def head(no, desc):
    print(f"[項目{no}] {desc}")


def result(expected, actual):
    print(f"    期待 : {expected}")
    print(f"    戻り値: {actual}")
    print()


def run_auto():
    """400 / 追加 / 解除 / 空一覧 / 一覧表示 / 存在しないID除外の全分岐を一括実行する。"""
    client = app.test_client()   # ドライバ：セッション付きでルートを呼び出す
    print("=" * 70)
    print(" favorites.py 単体テスト（自動・全項目／test_client＋repositoryスタブ）")
    print("=" * 70)

    head(1, "toggle_favorite / property_id 未指定 → 400 エラー")
    res = client.post("/api/favorites", json={})
    result("HTTP 400 / error メッセージ", f"HTTP {res.status_code} / {res.get_json()}")

    head(2, "toggle_favorite / 未登録の物件 → 追加(favorited=True)")
    res = client.post("/api/favorites", json={"property_id": "PRP0000001"})
    result("HTTP 200 / favorited=True", f"HTTP {res.status_code} / {res.get_json()}")

    head(3, "toggle_favorite / 登録済みの物件を再度 → 解除(favorited=False)")
    res = client.post("/api/favorites", json={"property_id": "PRP0000001"})
    result("HTTP 200 / favorited=False", f"HTTP {res.status_code} / {res.get_json()}")

    head(4, "favorites_page / お気に入りが空 → 案内文を表示")
    html = client.get("/favorites").get_data(as_text=True)
    result("空状態の案内文が表示される", f"案内文あり={'登録された物件はまだありません' in html}")

    head(5, "favorites_page / 2件登録 → スタブ物件が一覧に並ぶ")
    stub.mode = "found"
    client.post("/api/favorites", json={"property_id": "PRP0000006"})
    client.post("/api/favorites", json={"property_id": "PRP0000007"})
    html = client.get("/favorites").get_data(as_text=True)
    result("スタブ物件2件がカード表示される",
           f"カード数={html.count('<article class=\"card property-card\">')}")

    head(6, "favorites_page / 登録IDが存在しない(削除済み) → 一覧から除外")
    stub.mode = "not_found"
    html = client.get("/favorites").get_data(as_text=True)
    result("None の物件は除かれカード0件",
           f"カード数={html.count('<article class=\"card property-card\">')}")

    print("=" * 70)
    print(" 以上6項目。各分岐が期待どおりに動くかを目視で判定し、相違はIssueへ。")
    print("=" * 70)


def run_manual():
    """テスターが操作とスタブ物件の有無を選び、通った分岐と戻り値を確認する。"""
    client = app.test_client()   # 手動テスト中はセッションを保持し、登録が積み上がる
    print("=" * 70)
    print(" favorites.py 手動テスト（操作を選んで分岐を確認）")
    print("=" * 70)
    print(" 物件IDに『-』を入れると未指定(400エラー)の分岐を確認できます。\n")

    while True:
        op = ask_choice("操作を選択", [
            ("1", "お気に入り登録/解除（toggle_favorite）"),
            ("2", "お気に入り一覧を表示（favorites_page）"),
        ], "1")

        print("\n  ----- 実行 -----")
        if op == "1":
            pid = ask_str("物件ID（『-』で未指定）", "PRP0000001")
            body = {} if pid == "-" else {"property_id": pid}
            res = client.post("/api/favorites", json=body)
            print("\n  ----- 結果 -----")
            print(f"  HTTP {res.status_code} / {res.get_json()}")
        else:
            found = ask_bool("スタブ物件を存在させるか（nで削除済みを模擬）", True)
            stub.mode = "found" if found else "not_found"
            html = client.get("/favorites").get_data(as_text=True)
            cards = html.count('<article class="card property-card">')
            empty = "登録された物件はまだありません" in html
            print("\n  ----- 結果 -----")
            print(f"  カード数: {cards} / 空状態の案内: {empty}")
        print()

        if not ask_bool("続けて別の操作でテストしますか", True):
            break
    print("テストを終了します。")


if __name__ == "__main__":
    print("favorites.py ドライバ — モードを選んでください")
    print("  a) 自動（全項目を一括実行）")
    print("  m) 手動（操作を選んで分岐を確認）")
    choice = input("選択 [a]: ").strip().lower()
    if choice == "m":
        run_manual()
    else:
        run_auto()
