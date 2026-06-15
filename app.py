"""
不動産マッチングシステム（チーム労楽）— Flask アプリ本体。

画面:
  ① 条件入力        GET  /
  ② 物件提案        GET  /proposals
  ③ 物件詳細/課題   GET  /property/<id>
  ④ AIチャット      GET  /chat
  ⑤ 入居フロー      GET  /property/<id>/flow

API:
  POST /search                 条件を保存して提案へ
  POST /api/analyze/<id>       物件の課題・懸念点をAI分析
  POST /api/chat               AIコンシェルジュ応答
"""
from flask import (Flask, render_template, request, redirect,
                   url_for, session, jsonify)

import config
from services import repository, matching, ai

app = Flask(__name__)
app.secret_key = config.FLASK_SECRET_KEY  # 本番は環境変数 FLASK_SECRET_KEY で設定


@app.context_processor
def inject_chat_history():
    """全ページ共通のチャットドロワーに履歴を渡す。"""
    return {"chat_history": session.get("chat_history", [])}


# ------------------------------------------------------------------
# ① 条件入力
# ------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html",
                           condition=session.get("condition"),
                           use_mock=config.USE_MOCK)


@app.route("/search", methods=["POST"])
def search():
    """入力検証 → 条件をセッション保存 → 提案画面へ。"""
    errors = {}
    area = (request.form.get("area") or "").strip()
    layout = (request.form.get("layout") or "").strip()
    budget_raw = (request.form.get("budget") or "").strip()
    station_raw = (request.form.get("station_minutes") or "").strip()
    pet_allowed = request.form.get("pet_allowed") == "on"

    if not area:
        errors["area"] = "希望エリアを入力してください。"
    if not layout:
        errors["layout"] = "希望の間取りを入力してください。"

    budget = None
    if not budget_raw:
        errors["budget"] = "予算上限を入力してください。"
    else:
        try:
            budget = int(budget_raw)
            if budget <= 0:
                errors["budget"] = "予算は正の数で入力してください。"
        except ValueError:
            errors["budget"] = "予算は数値で入力してください。"

    station = None
    if not station_raw:
        errors["station_minutes"] = "駅からの距離（分）を入力してください。"
    else:
        try:
            station = int(station_raw)
            if station < 0:
                errors["station_minutes"] = "0以上の数値で入力してください。"
        except ValueError:
            errors["station_minutes"] = "数値で入力してください。"

    condition = {
        "area": area, "layout": layout, "budget": budget,
        "station_minutes": station, "pet_allowed": pet_allowed,
    }

    if errors:
        # 未入力をハイライトして入力画面に戻す
        return render_template("index.html", condition=condition,
                               errors=errors, use_mock=config.USE_MOCK), 400

    session["condition"] = condition
    return redirect(url_for("proposals"))


# ------------------------------------------------------------------
# ② 物件提案
# ------------------------------------------------------------------
@app.route("/proposals")
def proposals():
    condition = session.get("condition")
    if not condition:
        return redirect(url_for("index"))

    ranked = matching.match_properties(condition, repository.get_all_properties())
    # 適合度40%以上を「合致物件」とし、無ければ条件緩和候補として全件を案内
    matched = [p for p in ranked if p["score"] >= 40]
    relaxed = not matched
    display = matched if matched else ranked

    return render_template("proposals.html", condition=condition,
                           properties=display, relaxed=relaxed)


# ------------------------------------------------------------------
# ③ 物件詳細 ＋ 課題・懸念点分析
# ------------------------------------------------------------------
@app.route("/property/<property_id>")
def property_detail(property_id):
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
    prop = repository.get_property(property_id)
    if not prop:
        return jsonify({"error": "物件が見つかりません"}), 404
    condition = session.get("condition")
    if not condition:
        return jsonify({"error": "希望条件が未入力です。条件入力からやり直してください。"}), 400

    analysis = ai.analyze_property(condition, prop)
    return jsonify({"analysis": analysis})


# ------------------------------------------------------------------
# ④ AIチャット（コンシェルジュ）— 全ページ共通のドロワーから利用
# ------------------------------------------------------------------
@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "質問を入力してください。"}), 400

    reply = ai.generate_chat_reply(question, context={"condition": session.get("condition")})

    # チャット履歴を DB（chats）へ保存（Supabase接続時）。表示用にセッションにも保持。
    repository.save_chat(question, reply)
    history = session.get("chat_history", [])
    history.append({"question": question, "answer": reply})
    session["chat_history"] = history[-50:]  # 履歴は最新50件まで保持
    return jsonify({"answer": reply})


# ------------------------------------------------------------------
# ⑤ 入居までの手順確認
# ------------------------------------------------------------------
@app.route("/property/<property_id>/flow")
def move_in_flow(property_id):
    prop = repository.get_property(property_id)
    if not prop:
        return "物件が見つかりません", 404
    steps = repository.get_move_in_flow(prop["deal_type"])
    return render_template("flow.html", prop=prop, steps=steps)


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
