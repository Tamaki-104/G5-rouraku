"""
ai.py のドライバ（単体テスト・ホワイトボックス）。

ai.py は Gemini API に依存するため、Geminiスタブ(tests/stub_gemini.py)を差し込み、
実APIを呼ばずに分岐を検証する。config.GEMINI_ENABLED とスタブのモードを切り替えて、
「モック経路」「実AI経路」「API障害時のフォールバック」の各パスを通す。

実行: プロジェクト直下で  python tests/driver_ai.py

作成: チーム労楽  /  (c) 2026 チーム労楽
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)   # config / services
sys.path.insert(0, HERE)   # stub_gemini

import config
from services import ai
import stub_gemini as stub

# スタブの差し込み：ai が内部で呼ぶ _gemini_generate をスタブへ置き換える。
ai._gemini_generate = stub.gemini_generate_stub

COND = {"area": "渋谷区", "budget": 70000, "layout": "1LDK",
        "station_minutes": 20, "pet_allowed": False}
PROP = {"id": "PRP0000002", "name": "サンバ池袋", "area": "池袋区", "rent": 75000,
        "layout": "2LDK", "station_minutes": 20, "pet_allowed": False, "deal_type": "賃貸"}


def head(no, desc):
    print(f"[項目{no}] {desc}")


def result(expected, actual):
    print(f"    期待 : {expected}")
    print(f"    戻り値: {actual!r}")
    print()


print("=" * 70)
print(" ai.py 単体テスト（ドライバ＋Geminiスタブ）")
print("=" * 70)

# --- analyze_property の3分岐 ---
head(1, "analyze_property / GEMINI_ENABLED=False → モック分析文")
config.GEMINI_ENABLED = False
r = ai.analyze_property(COND, PROP)
result("『【サンバ池袋 の分析】…』で始まるモック文（スタブは呼ばれない）", r[:30] + "...")

head(2, "analyze_property / GEMINI_ENABLED=True・正常 → スタブ応答を返す")
config.GEMINI_ENABLED = True
stub.mode = "normal"
r = ai.analyze_property(COND, PROP)
result("スタブの応答テキスト（【スタブ応答】…）", r)

head(3, "analyze_property / API例外 → フォールバックでモック分析文")
config.GEMINI_ENABLED = True
stub.mode = "raise"
r = ai.analyze_property(COND, PROP)
result("例外を捕捉し『【サンバ池袋 の分析】…』のモック文へ", r[:30] + "...")

# --- generate_chat_reply の3分岐 ---
head(4, "generate_chat_reply / GEMINI_ENABLED=False → モック応答")
config.GEMINI_ENABLED = False
r = ai.generate_chat_reply("家賃を上げると良い物件はありますか", {})
result("予算に関するモック定型文", r)

head(5, "generate_chat_reply / 正常 → スタブ応答")
config.GEMINI_ENABLED = True
stub.mode = "normal"
r = ai.generate_chat_reply("この物件のおすすめは？", {})
result("スタブの応答テキスト", r)

head(6, "generate_chat_reply / API例外 → フォールバックでモック応答")
config.GEMINI_ENABLED = True
stub.mode = "raise"
r = ai.generate_chat_reply("家賃について教えて", {})
result("例外を捕捉しモック定型文へ", r)

# --- 純関数の分岐（スタブ不要）---
print("-" * 70)
print(" 補助：モック応答の分岐と文末整形（スタブ不要の純関数）")
print("-" * 70)

head(7, "_mock_chat / 物件と無関係な質問 → 対象外案内")
r = ai._mock_chat("今日の天気は？", {})
result("『物件探しに関するご質問に…』の対象外案内", r)

head(8, "_mock_chat / 『マッチ/おすすめ』を含む → 提案の案内")
r = ai._mock_chat("おすすめの物件は？", {})
result("適合度順に提案している旨の案内", r)

head(9, "_trim_to_sentence / 途中で切れた文を最後の句点で整える")
r = ai._trim_to_sentence("これは完全な文です。これは途中で切れ")
result("『これは完全な文です。』（句点まで）", r)

head(10, "_trim_to_sentence / 句点が無ければそのまま返す")
r = ai._trim_to_sentence("句点のない文字列")
result("『句点のない文字列』（変更なし）", r)

print("=" * 70)
print(" 以上10項目。期待どおりの経路・戻り値かを目視で判定し、相違はIssueへ。")
print("=" * 70)
