"""
AI(Gemini)まわり。物件の課題分析とチャット応答の2つを提供する。

キーがあれば実際のGeminiを叩き、無ければ(または通信に失敗したら)ルールベースの
モック応答に切り替える。おかげでキー無しでも画面は普通に動くので、発表で事故らない。

作成: チーム労楽  /  (c) 2026 チーム労楽
"""
import config
from services.matching import calculate_score


# --- 呼び出し口。使う側はモックか実AIかを気にしなくていい ---

def analyze_property(condition: dict, prop: dict) -> str:
    """物件の課題・懸念点をテキストで返す。実AIが落ちてもモックで必ず何か返す。"""
    if not config.GEMINI_ENABLED:
        return _mock_analyze(condition, prop)
    try:
        return _gemini_analyze(condition, prop)
    except Exception:
        return _mock_analyze(condition, prop)  # 通信エラーやレート制限時の保険


def generate_chat_reply(question: str, context: dict | None = None) -> str:
    """コンシェルジュの返答を返す。落ちたときの挙動は analyze_property と同じ。"""
    if not config.GEMINI_ENABLED:
        return _mock_chat(question, context or {})
    try:
        return _gemini_chat(question, context or {})
    except Exception:
        return _mock_chat(question, context or {})


# --- モックAI(キー無しのときの代役) ---

def _mock_analyze(condition: dict, prop: dict) -> str:
    """適合度の内訳から、良い点と気になる点を機械的に文章化するだけの簡易版。"""
    calc = calculate_score(condition, prop)
    bd = calc["breakdown"]
    good, concerns = [], []

    # 合否を、そのまま前向きな一文か注意の一文に振り分ける。
    if bd["area"]:
        good.append(f"エリア（{prop['area']}）が希望に合致しています。")
    else:
        concerns.append(f"エリアが希望（{condition.get('area', '指定なし')}）と異なります。")

    if bd["budget"]:
        good.append(f"家賃 {prop['rent']:,}円 は予算内に収まっています。")
    else:
        # 外したときは超過額まで出す。数字があった方が判断しやすい。
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
        # 懸念ゼロで終わると素っ気ないので、締めの一言を添える。
        lines.append("特筆すべき懸念点はなく、希望条件に良くマッチしています。")

    return "\n".join(lines)


def _mock_chat(question: str, context: dict) -> str:
    """物件がらみの質問かをキーワードでざっくり判定し、話題別の定型文を返す。"""
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
# 専用ライブラリは入れず、REST APIを requests で直接叩く。依存を増やさず
# Python統一のまま軽く保つため。キーの受け渡しはURLパラメータ(Geminiの仕様)。

# 1回の生成で許すトークンの初期上限と、途切れたときに取り直す最大回数。
_BASE_MAX_TOKENS = 1024
_MAX_ATTEMPTS = 3


def _join_parts(candidate: dict) -> str:
    """候補が複数partに分かれている場合があるので、テキストを全部つないで返す。"""
    parts = (candidate.get("content") or {}).get("parts") or []
    return "".join(p.get("text", "") for p in parts)


def _trim_to_sentence(text: str) -> str:
    """末尾が文の途中で切れているとき、最後の句点(。！？等)までで綺麗に打ち切る。"""
    for i in range(len(text) - 1, -1, -1):
        if text[i] in "。．！？!?":
            return text[:i + 1]
    return text


def _gemini_generate(prompt: str, max_tokens: int = _BASE_MAX_TOKENS, attempt: int = 1) -> str:
    """プロンプトをGeminiに投げ、本文テキストを返す。途切れたら再帰で取り直す。

    2.5系は既定の「思考」がトークンを消費し、その分 maxOutputTokens が本文に足りず
    途中で切れることがある。そこで thinkingBudget=0 で思考を止め、枠を全部本文に回す。
    それでも MAX_TOKENS で打ち切られた/本文が空だった場合は、上限を倍にして
    最大 _MAX_ATTEMPTS 回まで取り直す。最後まで途切れるなら最後の句点で締める。
    通信断やレート制限・5xxのような一時障害も、少し待って同じく取り直す。
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
                    # 思考にトークンを使わせず、本文が途中で切れるのを防ぐ。
                    "thinkingConfig": {"thinkingBudget": 0},
                },
            },
            timeout=30,  # 返ってこないまま画面を待たせ続けない。
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        # 通信断や5xxのような「すぐ直る一時障害」は少し待って取り直す。
        # 429(無料枠の超過)は数十秒待たないと回復せず短時間の再試行は無意味なので、
        # 即座に諦めて呼び出し元のモック応答へ回す。恒久的な4xxも同様。
        status = getattr(e.response, "status_code", None)
        transient = status is None or status in (500, 502, 503, 504)
        if transient and attempt < _MAX_ATTEMPTS:
            time.sleep(0.8 * attempt)  # 軽くバックオフしてから再試行
            return _gemini_generate(prompt, max_tokens, attempt + 1)
        raise

    data = resp.json()

    candidates = data.get("candidates") or []
    if not candidates:
        # 安全フィルタ等で候補ゼロ。数回だけ試し、それでもダメなら例外にして呼び出し元でモックへ。
        if attempt < _MAX_ATTEMPTS:
            return _gemini_generate(prompt, max_tokens, attempt + 1)
        raise RuntimeError("Geminiが応答を返しませんでした")

    candidate = candidates[0]
    truncated = candidate.get("finishReason") == "MAX_TOKENS"
    text = _join_parts(candidate).strip()

    # 途中で切れた or 本文が空 → 枠を倍にして取り直す(再帰)。
    if (truncated or not text) and attempt < _MAX_ATTEMPTS:
        return _gemini_generate(prompt, max_tokens * 2, attempt + 1)

    # 再試行し尽くしてもまだ途切れているなら、最後の句点までで整えて返す。
    return _trim_to_sentence(text) if truncated else text


def _gemini_analyze(condition: dict, prop: dict) -> str:
    """課題分析のプロンプトを組む。データに無いことは断定させず、幻覚を抑える。"""
    prompt = (
        "あなたは不動産アドバイザーです。以下のユーザー希望条件と物件情報を比較し、"
        "希望との乖離点・住む上での注意事項・懸念点を、日本語で簡潔な箇条書きにして示してください。"
        "物件データに無い情報は推測で断定しないこと。"
        # 長さの目安を明示して、冗長にも短すぎにもならないようにする。
        "全体で300字程度、箇条書きは合計5項目以内に収め、必ず文を最後まで完結させてください。\n\n"
        f"【ユーザーの希望条件】\n{condition}\n\n【物件情報】\n{prop}\n"
    )
    return _gemini_generate(prompt)


def _gemini_chat(question: str, context: dict) -> str:
    """チャットのプロンプトを組む。今の希望条件を渡して、条件を踏まえた返答にさせる。"""
    prompt = (
        "あなたは不動産探しを手伝うAIコンシェルジュです。物件・条件・入居手続きに関する"
        "質問に、日本語で丁寧かつ簡潔に回答してください。物件探しと無関係な質問には、"
        "対象外である旨を案内してください。"
        # 長さの目安を明示。会話なので分析より短めに。
        "回答は200〜300字程度で簡潔にまとめ、必ず文を最後まで完結させてください。\n\n"
        f"【参考情報（ユーザーの現在の希望条件など）】\n{context}\n\n"
        f"【ユーザーの質問】\n{question}\n"
    )
    return _gemini_generate(prompt)
