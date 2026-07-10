"""
favorites.py のドライバ（単体テスト・ホワイトボックス）。

favorites.py は repository.get_property と Flaskセッションに依存する。
repositoryスタブ(tests/stub_repository.py)で実DBを切り離し、Flaskの test_client を
ドライバとして用いてセッションを扱う。「property_id 未指定→400」「未登録→追加」
「登録済み→解除」「空一覧」「一覧に物件を並べる」の各分岐を通す。

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

# スタブの差し込み：favorites が呼ぶ repository.get_property をスタブへ置き換える。
repository.get_property = stub.get_property_stub

client = app.test_client()   # ドライバ：セッション付きでルートを呼び出す


def head(no, desc):
    print(f"[項目{no}] {desc}")


def result(expected, actual):
    print(f"    期待 : {expected}")
    print(f"    戻り値: {actual}")
    print()


print("=" * 70)
print(" favorites.py 単体テスト（ドライバ=test_client ＋ repositoryスタブ）")
print("=" * 70)

# --- toggle_favorite の分岐 ---
head(1, "toggle_favorite / property_id 未指定 → 400 エラー")
res = client.post("/api/favorites", json={})
result("HTTP 400 / error メッセージ", f"HTTP {res.status_code} / {res.get_json()}")

head(2, "toggle_favorite / 未登録の物件 → 追加(favorited=True)")
res = client.post("/api/favorites", json={"property_id": "PRP0000001"})
result("HTTP 200 / favorited=True", f"HTTP {res.status_code} / {res.get_json()}")

head(3, "toggle_favorite / 登録済みの物件を再度 → 解除(favorited=False)")
res = client.post("/api/favorites", json={"property_id": "PRP0000001"})
result("HTTP 200 / favorited=False", f"HTTP {res.status_code} / {res.get_json()}")

# --- favorites_page の分岐 ---
head(4, "favorites_page / お気に入りが空 → 案内文を表示")
# 直前の項目で解除済みのため空。念のため再確認する。
html = client.get("/favorites").get_data(as_text=True)
empty = "登録された物件はまだありません" in html
result("空状態の案内文が表示される", f"案内文あり={empty}")

head(5, "favorites_page / 2件登録 → スタブ物件が一覧に並ぶ")
stub.mode = "found"
client.post("/api/favorites", json={"property_id": "PRP0000006"})
client.post("/api/favorites", json={"property_id": "PRP0000007"})
html = client.get("/favorites").get_data(as_text=True)
cards = html.count('<article class="card property-card">')
result("スタブ物件2件がカード表示される", f"カード数={cards}")

head(6, "favorites_page / 登録IDが存在しない(削除済み) → 一覧から除外")
stub.mode = "not_found"     # get_property が None を返す
html = client.get("/favorites").get_data(as_text=True)
cards = html.count('<article class="card property-card">')
result("None の物件は除かれカード0件", f"カード数={cards}")

print("=" * 70)
print(" 以上6項目。各分岐が期待どおりに動くかを目視で判定し、相違はIssueへ。")
print("=" * 70)
