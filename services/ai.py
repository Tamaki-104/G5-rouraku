"""
AI(Gemini)連携。物件の課題分析とチャット応答の2機能を提供する。

APIキーがあれば実際のGeminiを呼び出し、無い場合や通信に失敗した場合はルールベースの
モック応答へ切り替える。キーが無くても画面が動作するため、デモ時の障害を避けられる。

作成: チーム労楽  /  (c) 2026 チーム労楽
"""
import config
from services.matching import calculate_score


# --- 公開関数。呼び出し側はモックか実AIかを意識しない ---

def analyze_property(condition: dict, prop: dict) -> str:
    """物件の課題・懸念点をテキストで返す。実AIが失敗してもモックで必ず返す。"""
    if not config.GEMINI_ENABLED:
        return _mock_analyze(condition, prop)
    try:
        return _gemini_analyze(condition, prop)
    except Exception:
        return _mock_analyze(condition, prop)  # 通信エラー・レート制限時のフォールバック


def generate_chat_reply(question: str, context: dict | None = None) -> str:
    """コンシェルジュの応答を返す。失敗時の挙動は analyze_property と同様。"""
    if not config.GEMINI_ENABLED:
        return _mock_chat(question, context or {})
    try:
        return _gemini_chat(question, context or {})
    except Exception:
        return _mock_chat(question, context or {})


# --- モックAI(キーが無い場合の代替) ---

def _mock_analyze(condition: dict, prop: dict) -> str:
    """適合度の内訳から、合致点と懸念点を文章化する簡易版。"""
    calc = calculate_score(condition, prop)
    bd = calc["breakdown"]
    good, concerns = [], []

    # 各項目の合否を、前向きな一文(good)と注意の一文(concerns)に振り分ける。
    if bd["area"]:
        good.append(f"エリア（{prop['area']}）が希望に合致しています。")
    else:
        concerns.append(f"エリアが希望（{condition.get('area', '指定なし')}）と異なります。")

    if bd["budget"]:
        good.append(f"家賃 {prop['rent']:,}円 は予算内に収まっています。")
    else:
        # 予算を外した場合は超過額を提示し、判断材料とする。
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
    """物件関連の質問かをキーワードで簡易判定し、話題別の定型文を返す。"""
    keywords = ["物件", "家賃", "予算", "間取り", "エリア", "駅", "ペット",
                "賃貸", "購入", "マッチ", "条件", "引越", "入居", "おすすめ", "家"]
    if not any(k in question for k in keywords):
        return "申し訳ありません。私は物件探しに関するご質問にお答えするAIコンシェルジュです。物件・条件・入居手続きなどについてお尋ねください。"

    if "家賃" in question or "予算" in question:
        return "ご予算を少し見直すと、選択肢が広がる場合があります。条件入力画面で予算上限を調整して再検索してみてください。"
    if "マッチ" in question or "おすすめ" in question:
        return "現在の希望条件に最も適合度が高い物件から順に提案しています。気になる物件は詳細画面で課題・懸念点もご確認いただけます。"
    return "ご質問ありがとうございます。希望条件に合わせて最適な物件をご提案します。条件を変更したい場合は条件入力画面からどうぞ。"


# --- Gemini本接続 ---
# 専用ライブラリは使用せず、REST APIを requests で直接呼び出す。依存を requests のみに
# 抑え、Python統一のまま軽量に保つため。キーはURLパラメータで渡す(Geminiの仕様)。

# 1回の生成で許容するトークンの初期上限と、途切れ時に取り直す最大回数。
_BASE_MAX_TOKENS = 1024
_MAX_ATTEMPTS = 3


def _join_parts(candidate: dict) -> str:
    """候補が複数partに分割されている場合があるため、テキストを全て連結して返す。"""
    parts = (candidate.get("content") or {}).get("parts") or []
    return "".join(p.get("text", "") for p in parts)


def _trim_to_sentence(text: str) -> str:
    """末尾が文の途中で切れている場合、最後の句点(。！？等)までで打ち切る。"""
    for i in range(len(text) - 1, -1, -1):
        if text[i] in "。．！？!?":
            return text[:i + 1]
    return text


def _gemini_generate(prompt: str, max_tokens: int = _BASE_MAX_TOKENS, attempt: int = 1) -> str:
    """プロンプトをGeminiに送信し、本文テキストを返す。途切れた場合は再帰で取り直す。

    2.5系は既定の「思考」がトークンを消費し、その分 maxOutputTokens が本文に不足して
    途中で切れることがある。そこで thinkingBudget=0 で思考を無効化し、全枠を本文に充てる。
    それでも MAX_TOKENS で打ち切られた／本文が空の場合は、上限を倍にして
    最大 _MAX_ATTEMPTS 回まで取り直す。最後まで途切れる場合は最後の句点で整える。
    通信断・レート制限・5xx等の一時障害も、短時間待機して同様に取り直す。
    """
    import requests
    import time
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{config.GEMINI_MODEL}:generateContent")
    try:
        resp = requests.post(
            url,
            params={"key": config.GEMINI_API_KEY},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": max_tokens,
                    # 思考にトークンを使わせず、本文の途中打ち切りを防ぐ。
                    "thinkingConfig": {"thinkingBudget": 0},
                },
            },
            timeout=30,  # 応答が返らないまま画面を待たせ続けない。
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        # 通信断や5xx等の一時障害は短時間待機して取り直す。
        # 429(無料枠超過)は数十秒待たないと回復せず短時間の再試行は無意味なため、
        # 即座に諦めて呼び出し元のモック応答へ回す。恒久的な4xxも同様。
        status = getattr(e.response, "status_code", None)
        transient = status is None or status in (500, 502, 503, 504)
        if transient and attempt < _MAX_ATTEMPTS:
            time.sleep(0.8 * attempt)  # バックオフしてから再試行
            return _gemini_generate(prompt, max_tokens, attempt + 1)
        raise

    data = resp.json()

    candidates = data.get("candidates") or []
    if not candidates:
        # 安全フィルタ等で候補が空。数回のみ再試行し、なお不可なら例外として呼び出し元でモックへ。
        if attempt < _MAX_ATTEMPTS:
            return _gemini_generate(prompt, max_tokens, attempt + 1)
        raise RuntimeError("Geminiが応答を返しませんでした")

    candidate = candidates[0]
    truncated = candidate.get("finishReason") == "MAX_TOKENS"
    text = _join_parts(candidate).strip()

    # 途中で切れた、または本文が空の場合は、上限を倍にして取り直す(再帰)。
    if (truncated or not text) and attempt < _MAX_ATTEMPTS:
        return _gemini_generate(prompt, max_tokens * 2, attempt + 1)

    # 再試行を尽くしてもなお途切れている場合は、最後の句点までで整えて返す。
    return _trim_to_sentence(text) if truncated else text


def _gemini_analyze(condition: dict, prop: dict) -> str:
    """課題分析用プロンプトを構築する。データに無い情報は断定させず、幻覚を抑制する。"""
    prompt = (
        "あなたは不動産アドバイザーです。以下のユーザー希望条件と物件情報を比較し、"
        "希望との乖離点・住む上での注意事項・懸念点を、日本語で簡潔な箇条書きにして示してください。"
        "物件データに無い情報は推測で断定しないこと。"
        # 冗長・過短のいずれにもならないよう長さの目安を明示する。
        "全体で300字程度、箇条書きは合計5項目以内に収め、必ず文を最後まで完結させてください。\n\n"
        f"【ユーザーの希望条件】\n{condition}\n\n【物件情報】\n{prop}\n"
    )
    return _gemini_generate(prompt)


def _gemini_chat(question: str, context: dict) -> str:
    """チャット応答用プロンプトを構築する。現在の希望条件を渡し、条件を踏まえた回答を促す。"""
    prompt = (
        "あなたは不動産探しを手伝うAIコンシェルジュです。物件・条件・入居手続きに関する"
        "質問に、日本語で丁寧かつ簡潔に回答してください。物件探しと無関係な質問には、"
        "対象外である旨を案内してください。"
        # 会話のため分析より短めに、長さの目安を明示する。
        "回答は200〜300字程度で簡潔にまとめ、必ず文を最後まで完結させてください。\n\n"
        f"【参考情報（ユーザーの現在の希望条件など）】\n{context}\n\n"
        f"【ユーザーの質問】\n{question}\n"
    )
    return _gemini_generate(prompt)
