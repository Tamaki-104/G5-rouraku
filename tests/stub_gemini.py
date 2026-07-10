"""
Geminiスタブ。ai.py が依存する _gemini_generate の代役。

実際のGemini APIを呼ばず、設定したモードに応じて固定の戻り値を返す、または
例外を送出する。呼び出し・引数・戻り値をすべて表示する（授業資料10.6の留意点に準拠）。
これにより ai.py 側の「実AI経路」「API障害時のフォールバック」を切り分けて検証できる。

作成: チーム労楽  /  (c) 2026 チーム労楽
"""

# 戻り値の切替。ドライバがテスト項目ごとに設定する。
#   "normal": 正常な生成テキストを返す
#   "raise" : API障害を模擬して例外を送出（呼び出し側のフォールバックを検証）
mode = "normal"

NORMAL_TEXT = "【スタブ応答】物件と希望条件を比較した分析文です。"


def gemini_generate_stub(prompt, max_tokens=1024, attempt=1):
    """ai._gemini_generate と同じ引数・戻り値の型で振る舞う代役。"""
    print("    [STUB Gemini] _gemini_generate が呼び出された")
    print(f"    [STUB Gemini]   引数 prompt(先頭50字) = {prompt[:50]!r}")
    print(f"    [STUB Gemini]   引数 max_tokens = {max_tokens} / attempt = {attempt}")
    print(f"    [STUB Gemini]   モード = {mode}")
    if mode == "raise":
        print("    [STUB Gemini]   → 例外を送出（API障害を模擬）")
        raise RuntimeError("スタブ: Gemini API 障害を模擬")
    print(f"    [STUB Gemini]   → 戻り値 = {NORMAL_TEXT!r}")
    return NORMAL_TEXT
