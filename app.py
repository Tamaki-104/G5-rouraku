"""
Flaskアプリ本体。リクエストを受けて画面を出し分ける薄い層であり、
実データ取得は repository、採点は matching、AI応答は ai に委譲する。

画面: /(条件入力) → /proposals(提案) → /property/<id>(詳細+分析) → /property/<id>/flow(入居手順)
API : /search(条件保存)  /api/analyze/<id>(課題分析)  /api/chat(チャット)

作成: チーム労楽  /  (c) 2026 チーム労楽
"""
from flask import (Flask, render_template, request, redirect,
                   url_for, session, jsonify)
from jinja2 import DictLoader

import config
import ui
from services import repository, matching, ai

# HTML/CSS/JSは全て ui.py に集約しているため、静的フォルダ(static/)は使用しない。
app = Flask(__name__, static_folder=None)
app.secret_key = config.FLASK_SECRET_KEY
# テンプレートは .html ファイルではなく ui.py 内の文字列群から読み込む。
app.jinja_env.loader = DictLoader(ui.TEMPLATES)


@app.context_processor
def inject_chat_history():
    """チャットドロワーは全ページ共通のため、履歴を全テンプレートへ渡す。"""
    return {"chat_history": session.get("chat_history", [])}


def _parse_int(raw, *, minimum, empty_msg, nan_msg, small_msg):
    """必須の整数入力を検証し (値, エラー文) を返す。問題が無ければエラー文は None。

    予算と駅距離で同一の検証を繰り返すため、本関数に集約する。下限のみ引数で変える。
    """
    if not raw:
        return None, empty_msg
    try:
        value = int(raw)
    except ValueError:
        return None, nan_msg
    if value < minimum:
        return None, small_msg
    return value, None


# --- ① 条件入力 ---

@app.route("/")
def index():
    """条件入力画面。前回の入力が残っていれば復元して表示する。"""
    return render_template("index.html",
                           condition=session.get("condition"),
                           use_mock=config.USE_MOCK)


@app.route("/search", methods=["POST"])
def search():
    """入力を検証し、通れば条件をセッションへ保存して提案画面へ遷移する。"""
    errors = {}  # 項目名 -> エラー文。1件でも存在すれば入力画面へ差し戻す。
    area = (request.form.get("area") or "").strip()
    layout = (request.form.get("layout") or "").strip()
    pet_allowed = request.form.get("pet_allowed") == "on"

    if not area:
        errors["area"] = "希望エリアを入力してください。"
    if not layout:
        errors["layout"] = "希望の間取りを入力してください。"

    # 予算は正の整数(家賃と大小比較するため数値であることが必須)。
    budget, err = _parse_int(
        (request.form.get("budget") or "").strip(), minimum=1,
        empty_msg="予算上限を入力してください。",
        nan_msg="予算は数値で入力してください。",
        small_msg="予算は正の数で入力してください。")
    if err:
        errors["budget"] = err

    # 駅からの距離は0以上の整数(徒歩何分以内、の上限として使用)。
    station, err = _parse_int(
        (request.form.get("station_minutes") or "").strip(), minimum=0,
        empty_msg="駅からの距離（分）を入力してください。",
        nan_msg="数値で入力してください。",
        small_msg="0以上の数値で入力してください。")
    if err:
        errors["station_minutes"] = err

    condition = {
        "area": area, "layout": layout, "budget": budget,
        "station_minutes": station, "pet_allowed": pet_allowed,
    }

    if errors:
        # 入力値を保持したまま差し戻し、該当欄を強調表示する。ステータスは400。
        return render_template("index.html", condition=condition,
                               errors=errors, use_mock=config.USE_MOCK), 400

    # 提案画面でも参照するため、条件をセッションへ保存してから遷移する。
    session["condition"] = condition
    return redirect(url_for("proposals"))


# --- ② 物件提案 ---

@app.route("/proposals")
def proposals():
    """保存済みの条件で物件を採点し、適合度の高い順に並べて表示する。"""
    condition = session.get("condition")
    if not condition:
        return redirect(url_for("index"))  # 条件なしで直接開かれた場合は入力画面へ誘導

    all_props = repository.get_all_properties()
    ranked = matching.match_properties(condition, all_props)
    # 希望エリアが最優先条件のため、県外(適合率0%)の物件は一覧に表示しない。
    ranked = [p for p in ranked if not p["out_of_area"]]
    # 40%以上を提示対象とする。0件の場合は条件を緩めた候補として残りを表示し、
    # 画面には relaxed で「緩和した候補である」旨を添える。
    matched = [p for p in ranked if p["score"] >= 40]
    relaxed = bool(ranked) and not matched
    display = matched or ranked

    # 入力エリアのうち物件データに存在しない表記(誤字・「区」抜け等)を抽出し、注意喚起に用いる。
    known_areas = {p["area"] for p in all_props}
    unknown_areas = [a for a in matching.split_multi(condition.get("area", ""))
                     if a not in known_areas]

    return render_template("proposals.html", condition=condition,
                           properties=display, relaxed=relaxed,
                           unknown_areas=unknown_areas)


# --- ③ 物件詳細 ＋ 課題分析 ---

@app.route("/property/<property_id>")
def property_detail(property_id):
    """物件詳細。条件があれば当該物件の適合度も表示する(条件が無くても詳細は表示)。"""
    prop = repository.get_property(property_id)
    if not prop:
        return "物件が見つかりません", 404

    condition = session.get("condition") or {}
    calc = matching.calculate_score(condition, prop) if condition else None
    score = calc["score"] if calc else None
    return render_template("detail.html", prop=prop, condition=condition,
                           score=score)


@app.route("/api/analyze/<property_id>", methods=["POST"])
def api_analyze(property_id):
    """「課題・懸念点を確認する」から呼ばれ、AI分析結果をJSONで返す。"""
    prop = repository.get_property(property_id)
    if not prop:
        return jsonify({"error": "物件が見つかりません"}), 404
    # 分析は条件と物件の突き合わせであり、条件が無ければ成立しない。
    condition = session.get("condition")
    if not condition:
        return jsonify({"error": "希望条件が未入力です。条件入力からやり直してください。"}), 400

    return jsonify({"analysis": ai.analyze_property(condition, prop)})


# --- ④ AIチャット(全ページ共通ドロワー) ---

@app.route("/api/chat", methods=["POST"])
def api_chat():
    """質問を受けてAI応答を返し、履歴を保存する。"""
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "質問を入力してください。"}), 400

    # 現在の希望条件を渡すことで、条件を踏まえた応答が得られる。
    reply = ai.generate_chat_reply(question, context={"condition": session.get("condition")})

    # 永続記録はDBへ、画面の即時表示用にセッションへ保持する。DB未接続時はセッションのみ。
    repository.save_chat(question, reply)
    history = session.get("chat_history", [])
    history.append({"question": question, "answer": reply})
    session["chat_history"] = history[-50:]  # Cookieの肥大化を防ぐ
    return jsonify({"answer": reply})


# --- ⑤ 入居手順 ---

@app.route("/property/<property_id>/flow")
def move_in_flow(property_id):
    """賃貸/購入で手続きが異なるため、取引種別に応じたフローを表示する。"""
    prop = repository.get_property(property_id)
    if not prop:
        return "物件が見つかりません", 404
    steps = repository.get_move_in_flow(prop["deal_type"])
    return render_template("flow.html", prop=prop, steps=steps)


# ローカル起動用。本番(Vercel)ではWSGIの app が直接呼ばれ、この分岐は実行されない。
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # ホスティングの指定に合わせPORTを優先
    # リローダーは子プロセスを常駐させ、プレビュー/サーバ管理を妨げるため無効化する。
    app.run(debug=True, use_reloader=False, host="127.0.0.1", port=port)
