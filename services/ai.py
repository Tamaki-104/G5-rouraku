"""
AI（GeminiAPI）クラス相当。

設計書の2機能を提供:
  - analyze_property(): 希望条件と物件を比較し、課題・懸念点・注意事項を生成
  - generate_chat_reply(): AIコンシェルジュのチャット応答を生成

USE_MOCK=True のときはルールベースの「モックAI」で動作（キー不要）。
USE_MOCK=False のときは Gemini 2.5 Flash API を呼ぶ（要 GEMINI_API_KEY）。
"""
import config
from services.matching import calculate_score


# ------------------------------------------------------------------
# 公開関数
# ------------------------------------------------------------------
def analyze_property(condition: dict, prop: dict) -> str:
    """物件の課題・懸念点を分析したテキストを返す。"""
    if not config.GEMINI_ENABLED:
        return _mock_analyze(condition, prop)
    try:
        return _gemini_analyze(condition, prop)
    except Exception:
        # API 失敗時はモック分析にフォールバック
        return _mock_analyze(condition, prop)


def generate_chat_reply(question: str, context: dict | None = None) -> str:
    """AIコンシェルジュの応答テキストを返す。"""
    if not config.GEMINI_ENABLED:
        return _mock_chat(question, context or {})
    try:
        return _gemini_chat(question, context or {})
    except Exception:
        return _mock_chat(question, context or {})


# ------------------------------------------------------------------
# モックAI（ルールベース）
# ------------------------------------------------------------------
def _mock_analyze(condition: dict, prop: dict) -> str:
    calc = calculate_score(condition, prop)
    bd = calc["breakdown"]
    good, concerns = [], []

    if bd["area"]:
        good.append(f"エリア（{prop['area']}）が希望に合致しています。")
    else:
        concerns.append(f"エリアが希望（{condition.get('area', '指定なし')}）と異なります。")

    if bd["budget"]:
        good.append(f"家賃 {prop['rent']:,}円 は予算内に収まっています。")
    else:
        over = prop["rent"] - (condition.get("budget") or 0)
        concerns.append(f"家賃が予算を約 {over:,}円 オーバーしています。")

    if bd["layout"]:
        good.append(f"間取り（{prop['layout']}）が希望どおりです。")
    else:
        concerns.append(f"間取り（{prop['layout']}）が希望（{condition.get('layout', '指定なし')}）と異なります。")

    if bd["station"]:
        good.append(f"駅から徒歩{prop['station_minutes']}分で条件を満たしています。")
    else:
        concerns.append(f"駅から徒歩{prop['station_minutes']}分で、希望よりやや遠い可能性があります。")

    if not bd["pet"]:
        concerns.append("ペット不可のため、ペット飼育を希望する場合は注意が必要です。")

    lines = [f"【{prop['name']} の分析】（適合度 {calc['score']}%）", ""]
    if good:
        lines.append("◎ 合致している点:")
        lines += [f"・{g}" for g in good]
        lines.append("")
    if concerns:
        lines.append("△ 課題・懸念点:")
        lines += [f"・{c}" for c in concerns]
    else:
        lines.append("特筆すべき懸念点はなく、希望条件に良くマッチしています。")

    return "\n".join(lines)


def _mock_chat(question: str, context: dict) -> str:
    """物件探しに関係する質問か簡易判定し、関係なければ対象外案内を返す。"""
    keywords = ["物件", "家賃", "予算", "間取り", "エリア", "駅", "ペット",
                "賃貸", "購入", "マッチ", "条件", "引越", "入居", "おすすめ", "家"]
    if not any(k in question for k in keywords):
        return "申し訳ありません。私は物件探しに関するご質問にお答えするAIコンシェルジュです。物件・条件・入居手続きなどについてお尋ねください。"

    if "家賃" in question or "予算" in question:
        return "ご予算を少し見直すと、選択肢が広がる場合があります。条件入力画面で予算上限を調整して再検索してみてください。"
    if "マッチ" in question or "おすすめ" in question:
        return "現在の希望条件に最も適合度が高い物件から順に提案しています。気になる物件は詳細画面で課題・懸念点もご確認いただけます。"
    return "ご質問ありがとうございます。希望条件に合わせて最適な物件をご提案します。条件を変更したい場合は条件入力画面からどうぞ。"


# ------------------------------------------------------------------
# Gemini 本接続（USE_MOCK=False のとき）
# ------------------------------------------------------------------
def _gemini_model():
    import google.generativeai as genai
    genai.configure(api_key=config.GEMINI_API_KEY)
    return genai.GenerativeModel(config.GEMINI_MODEL)


def _gemini_analyze(condition: dict, prop: dict) -> str:
    prompt = (
        "あなたは不動産アドバイザーです。以下のユーザー希望条件と物件情報を比較し、"
        "希望との乖離点・住む上での注意事項・懸念点を簡潔な箇条書きで日本語で示してください。\n\n"
        f"【ユーザーの希望条件】\n{condition}\n\n【物件情報】\n{prop}\n"
    )
    return _gemini_model().generate_content(prompt).text


def _gemini_chat(question: str, context: dict) -> str:
    prompt = (
        "あなたは不動産探しを手伝うAIコンシェルジュです。物件・条件・入居手続きに関する"
        "質問に日本語で丁寧に回答してください。物件探しと無関係な質問には、対象外である旨を"
        "案内してください。\n\n"
        f"【参考情報】\n{context}\n\n【ユーザーの質問】\n{question}\n"
    )
    return _gemini_model().generate_content(prompt).text
