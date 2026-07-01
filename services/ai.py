"""
AI（Gemini API）連携（設計書「AI（GeminiAPI）クラス」相当）。

概要:
    2つのAI機能を提供する。
      - analyze_property()   : 希望条件と物件を比較し、課題・懸念点・注意事項を生成
      - generate_chat_reply(): AIコンシェルジュとしてチャット応答を生成
    APIキー（config.GEMINI_ENABLED）が有効なら実際の Gemini 2.5 Flash を呼び、
    無い場合やAPI失敗時はルールベースの「モックAI」に自動でフォールバックする。
    これにより、キーが無くても画面が止まらず、発表・デモを安全に行える。

作成    : チーム労楽
Copyright (c) 2026 チーム労楽. All rights reserved.
"""
import config
from services.matching import calculate_score


# ------------------------------------------------------------------
# 公開関数（呼び出し側はモック/実AIの区別を意識しなくてよい）
# ------------------------------------------------------------------
def analyze_property(condition: dict, prop: dict) -> str:
    """物件の課題・懸念点を分析したテキストを返す。

    キーが無ければモック分析。実AI呼び出しが失敗した場合も、
    利用者に空応答を見せないようモック分析へ切り替える。
    """
    if not config.GEMINI_ENABLED:
        return _mock_analyze(condition, prop)
    try:
        return _gemini_analyze(condition, prop)
    except Exception:
        # 通信エラー・レート制限などで実AIが使えないときの安全網。
        return _mock_analyze(condition, prop)


def generate_chat_reply(question: str, context: dict | None = None) -> str:
    """AIコンシェルジュの応答テキストを返す（失敗時はモック応答へフォールバック）。"""
    if not config.GEMINI_ENABLED:
        return _mock_chat(question, context or {})
    try:
        return _gemini_chat(question, context or {})
    except Exception:
        return _mock_chat(question, context or {})


# ------------------------------------------------------------------
# モックAI（APIキー不要のルールベース代替）
# ------------------------------------------------------------------
def _mock_analyze(condition: dict, prop: dict) -> str:
    """適合度の内訳をもとに、合致点と懸念点を箇条書きの文章に組み立てる。

    実AIの代わりに、breakdown（各項目の合否）から機械的に文章化する。
    """
    calc = calculate_score(condition, prop)
    bd = calc["breakdown"]
    good, concerns = [], []   # 合致点 / 懸念点をそれぞれ集める。

    # 各項目の合否を、利用者向けの前向き文（good）／注意文（concerns）に振り分ける。
    if bd["area"]:
        good.append(f"エリア（{prop['area']}）が希望に合致しています。")
    else:
        concerns.append(f"エリアが希望（{condition.get('area', '指定なし')}）と異なります。")

    if bd["budget"]:
        good.append(f"家賃 {prop['rent']:,}円 は予算内に収まっています。")
    else:
        # 予算を外した場合は、超過額を具体的に示して判断材料にしてもらう。
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

    # 見出し＋合致点＋懸念点の順に整形。懸念が無ければ好意的な締めにする。
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
    """物件探しに関係する質問かを簡易判定し、話題に応じた定型回答を返す。

    キーワードを1つも含まなければ「対象外」と案内し、
    含む場合は話題（予算/おすすめ 等）に合わせた案内文を返す。
    """
    # 物件探しに関連するとみなすキーワード群（1つでも含めば対象内と判定）。
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
# Gemini 本接続（GEMINI_API_KEY があるとき）
# 専用ライブラリを使わず REST API を requests で直接呼ぶ。
# 理由: Python統一の方針に沿い、依存を requests だけに抑えて軽量に保つため。
# ------------------------------------------------------------------
def _gemini_generate(prompt: str) -> str:
    """組み立て済みのプロンプトを Gemini REST API に投げ、生成本文だけを取り出して返す。"""
    import requests
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{config.GEMINI_MODEL}:generateContent")
    resp = requests.post(
        url,
        params={"key": config.GEMINI_API_KEY},   # キーはURLパラメータで渡す（Gemini APIの仕様）。
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            # temperature: 回答の多様性。maxOutputTokens: 応答が長くなり過ぎないよう上限。
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1024},
        },
        timeout=30,   # 応答が返らないまま画面を待たせ続けないためのタイムアウト。
    )
    resp.raise_for_status()
    data = resp.json()
    # 応答は candidates[0].content.parts[0].text にテキストが入る構造。前後の空白は除去。
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


def _gemini_analyze(condition: dict, prop: dict) -> str:
    """課題分析用のプロンプトを組み立ててGeminiに依頼する。

    「物件データに無い情報は断定しない」よう明示し、ハルシネーションを抑える。
    """
    prompt = (
        "あなたは不動産アドバイザーです。以下のユーザー希望条件と物件情報を比較し、"
        "希望との乖離点・住む上での注意事項・懸念点を、日本語で簡潔な箇条書きにして示してください。"
        "物件データに無い情報は推測で断定しないこと。\n\n"
        f"【ユーザーの希望条件】\n{condition}\n\n【物件情報】\n{prop}\n"
    )
    return _gemini_generate(prompt)


def _gemini_chat(question: str, context: dict) -> str:
    """チャット応答用のプロンプトを組み立ててGeminiに依頼する。

    現在の希望条件を参考情報として渡し、条件を踏まえた回答を促す。
    物件探しと無関係な質問には対象外案内をするよう指示する。
    """
    prompt = (
        "あなたは不動産探しを手伝うAIコンシェルジュです。物件・条件・入居手続きに関する"
        "質問に、日本語で丁寧かつ簡潔に回答してください。物件探しと無関係な質問には、"
        "対象外である旨を案内してください。\n\n"
        f"【参考情報（ユーザーの現在の希望条件など）】\n{context}\n\n"
        f"【ユーザーの質問】\n{question}\n"
    )
    return _gemini_generate(prompt)
