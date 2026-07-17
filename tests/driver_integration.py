"""
結合テスト（段階1・2）用ドライバ — ボトムアップ結合。

単体テストと異なりスタブへ差し替えず、下位モジュール（repository×実Supabase、
ai×実Gemini）を実際に結合して動作を確認する。障害系（IT-04・IT-07）のみ、
項目表の指定どおり失敗を模擬する差し替えを行う。
結合テスト項目表の IT-01〜IT-11 に対応し、通番を表示するので結果を項目表へ転記する。

実行: .env のあるプロジェクト直下で  python tests/driver_integration.py
（.env が無い場所で実行すると実接続の項目はスキップ表示になる）

作成: チーム労楽  /  (c) 2026 チーム労楽
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

import config
from services import repository as repo
from services import matching as m
from services import ai


def head(no, desc):
    print("-" * 70)
    print(f"[{no}] {desc}")


def result(expected, actual):
    print(f"    期待 : {expected}")
    print(f"    結果 : {actual}")


print("=" * 70)
print(" 結合テスト 段階1・2 ドライバ（ボトムアップ / 実サービス結合）")
print("=" * 70)
print(f" 接続状態: Supabase={'実接続' if config.SUPABASE_ENABLED else 'モック(未接続)'}"
      f" / Gemini={'実AI' if config.GEMINI_ENABLED else 'モック(キー無し)'}")
print(" ※実接続の項目(IT-02,03,05,06)は .env のある場所で実行すること。")
print()

# ---------- 段階1: 下位結合 ----------

head("IT-01", "repository×モックデータ: get_all_properties（結合確認）")
saved = config.SUPABASE_ENABLED
config.SUPABASE_ENABLED = False
r = repo.get_all_properties()
config.SUPABASE_ENABLED = saved
result("9件・prefecture/area等を含む平坦な形",
       f"{len(r)}件 / 先頭={r[0]['name']} / prefecture={r[0].get('prefecture')!r}")

head("IT-02", "repository×実Supabase: get_all_properties（正常系）")
if config.SUPABASE_ENABLED:
    r = repo.get_all_properties()
    prefs = sorted({p.get("prefecture", "") for p in r})
    result("実DBから9件・全件に都道府県あり",
           f"{len(r)}件 / prefecture一覧={prefs} / 空の件数={sum(1 for p in r if not p.get('prefecture'))}")
else:
    print("    スキップ: Supabase未接続（.envのある場所で実行する）")

head("IT-03", "repository×実Supabase: 存在しないID → None（準正常）")
if config.SUPABASE_ENABLED:
    r = repo.get_property("PRP9999999")
    result("None（例外にならない）", r)
else:
    print("    スキップ: Supabase未接続")

head("IT-04", "Supabase取得失敗 → モックへフォールバック（障害系・失敗を模擬）")
orig_rest = repo._rest_get
def _boom(*a, **k):
    raise ConnectionError("結合テスト: Supabase停止を模擬")
repo._rest_get = _boom
saved = config.SUPABASE_ENABLED
config.SUPABASE_ENABLED = True
r = repo.get_all_properties()
repo._rest_get = orig_rest
config.SUPABASE_ENABLED = saved
result("例外を捕捉しモック9件へ切替", f"{len(r)}件 / 先頭={r[0]['name']}")

COND = {"prefecture": "東京都", "area": "渋谷区", "budget": 70000,
        "layout": "1LDK", "station_minutes": 20, "pet_allowed": False}

head("IT-05", "ai×実Gemini: analyze_property（正常系）")
if config.GEMINI_ENABLED:
    prop = repo.get_property("PRP0000002")
    text = ai.analyze_property(COND, prop)
    ends_ok = text.strip()[-1] in "。．！？!?"
    result("分析文が返り、文末が句点等で完結",
           f"{len(text)}字 / 文末完結={ends_ok} / 冒頭={text[:40]!r}")
else:
    print("    スキップ: Geminiキー無し（.envのある場所で実行する）")

head("IT-06", "ai×実Gemini: generate_chat_reply（正常系）")
if config.GEMINI_ENABLED:
    text = ai.generate_chat_reply("渋谷区で予算7万円は厳しいですか？", {"condition": COND})
    ends_ok = text.strip()[-1] in "。．！？!?"
    result("条件を踏まえた回答が完結した文で返る",
           f"{len(text)}字 / 文末完結={ends_ok} / 冒頭={text[:40]!r}")
else:
    print("    スキップ: Geminiキー無し")

head("IT-07", "Gemini障害 → モック応答へフォールバック（障害系・失敗を模擬）")
orig_gen = ai._gemini_generate
def _ai_boom(*a, **k):
    raise RuntimeError("結合テスト: Gemini障害を模擬")
ai._gemini_generate = _ai_boom
saved = config.GEMINI_ENABLED
config.GEMINI_ENABLED = True
prop = repo.get_property("PRP0000002")
text = ai.analyze_property(COND, prop)
ai._gemini_generate = orig_gen
config.GEMINI_ENABLED = saved
result("モック分析文（【…の分析】…）に切替", f"冒頭={text[:30]!r}")

# ---------- 段階2: サービス間結合 ----------

head("IT-08", "matching×repository: 実データを採点し降順に並ぶ（結合確認）")
props = repo.get_all_properties()
ranked = m.match_properties(COND, props)
scores = [p["score"] for p in ranked]
result("全件採点・スコア降順",
       f"{len(ranked)}件 / scores={scores} / 降順={scores == sorted(scores, reverse=True)}")

head("IT-09", "matching×repository: 県外物件は score=0（正常系）")
yokohama = next((p for p in props if p["area"] == "横浜区"), None)
if yokohama:
    calc = m.calculate_score(COND, yokohama)
    result("out_of_area=True・score=0",
           f"out_of_area={calc['out_of_area']} / score={calc['score']}")
else:
    print("    スキップ: 横浜区の物件がデータに無い")

head("IT-10", "ai×matching: モック分析文が採点の内訳(breakdown)と整合（結合確認）")
prop = repo.get_property("PRP0000002")
calc = m.calculate_score(COND, prop)
text = ai._mock_analyze(COND, prop)
print(f"    breakdown: {calc['breakdown']}")
print("    分析文:")
for line in text.splitlines():
    print(f"      {line}")
print("    → 合致点/懸念点が breakdown の True/False と一致していれば合格")

head("IT-11", "favorites×repository: 登録IDの物件が一覧に取得される（結合確認）")
from app import app
client = app.test_client()
client.post("/api/favorites", json={"property_id": "PRP0000001"})
client.post("/api/favorites", json={"property_id": "PRP9999999"})  # 存在しないID
html = client.get("/favorites").get_data(as_text=True)
cards = html.count('<article class="card property-card">')
result("実在ID(ホーム渋谷)のみ一覧に表示、存在しないIDは除外(カード1件)",
       f"カード数={cards} / ホーム渋谷表示={'ホーム渋谷' in html}")

print()
print("=" * 70)
print(" 段階1・2 は以上。結果を項目表(IT-01〜IT-11)へ転記する。")
print(" 段階3(IT-12〜34)はローカル起動(python app.py)しブラウザで、")
print(" 段階4(IT-35〜38)は本番URLで実施する。")
print("=" * 70)
