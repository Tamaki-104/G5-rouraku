"""
不動産マッチングシステム（チーム労楽）— Flask アプリ本体（画面遷移とAPIの入口）。

概要:
    ブラウザからのリクエストを受け、①条件入力→②物件提案→③物件詳細/課題分析→
    ④AIチャット→⑤入居フロー という一連の画面遷移をルーティングする。
    実データの取得は services.repository、適合度計算は services.matching、
    AI応答は services.ai に委譲し、本ファイルは「受け取り・振り分け・画面へ渡す」に徹する。

画面（GET）:
    /                      ① 条件入力
    /proposals             ② 物件提案（適合度の高い順）
    /property/<id>         ③ 物件詳細＋課題分析
    /property/<id>/flow    ⑤ 入居フロー（賃貸/購入で分岐）
API（POST）:
    /search                条件を検証・保存し提案画面へ
    /api/analyze/<id>      物件の課題・懸念点をAIで分析
    /api/chat              AIコンシェルジュの応答を返す

作成    : チーム労楽
Copyright (c) 2026 チーム労楽. All rights reserved.
"""
from flask import (Flask, render_template, request, redirect,
                   url_for, session, jsonify)
from jinja2 import DictLoader

import config
import ui
from services import repository, matching, ai

# 画面テンプレート・CSS・JSはすべて ui.py に集約しているため、
# Flask標準の静的フォルダ（static/）は使わない（static_folder=None）。
app = Flask(__name__, static_folder=None)
# セッションCookieの署名に使う秘密鍵。漏洩するとセッション偽造が可能なため本番は環境変数で指定。
app.secret_key = config.FLASK_SECRET_KEY

# テンプレートは .html ファイルではなく ui.py 内の文字列群から読み込む。
app.jinja_env.loader = DictLoader(ui.TEMPLATES)


@app.context_processor
def inject_chat_history():
    """全ページに常駐するチャットドロワーへ、これまでの会話履歴を渡す。

    どの画面を開いてもドロワーに過去のやり取りを表示できるよう、
    全テンプレート共通の変数 chat_history としてセッションの履歴を注入する。
    """
    return {"chat_history": session.get("chat_history", [])}


# ------------------------------------------------------------------
# ① 条件入力
# ------------------------------------------------------------------
@app.route("/")
def index():
    """条件入力画面を表示する。前回入力（セッション）があれば復元して見せる。"""
    return render_template("index.html",
                           condition=session.get("condition"),
                           use_mock=config.USE_MOCK)


@app.route("/search", methods=["POST"])
def search():
    """入力内容を検証し、問題なければ条件をセッションに保存して提案画面へ送る。

    必須項目の未入力や数値でない予算などを検出したら、入力画面に戻して
    どの項目が不正かを errors で伝える（画面側で該当欄を強調する）。
    """
    # 項目名 -> エラーメッセージ。1件でも入れば入力画面へ差し戻す判断に使う。
    errors = {}
    area = (request.form.get("area") or "").strip()
    layout = (request.form.get("layout") or "").strip()
    budget_raw = (request.form.get("budget") or "").strip()
    station_raw = (request.form.get("station_minutes") or "").strip()
    pet_allowed = request.form.get("pet_allowed") == "on"

    # 文字列項目は空でないことだけ確認する。
    if not area:
        errors["area"] = "希望エリアを入力してください。"
    if not layout:
        errors["layout"] = "希望の間取りを入力してください。"

    # 予算は「正の整数」であることを保証する（後段の家賃比較で数値として使うため）。
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

    # 駅からの距離は「0以上の整数（分）」。徒歩分数の上限として使う。
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

    # マッチング処理・画面表示で共通に使う希望条件のまとまり。
    condition = {
        "area": area, "layout": layout, "budget": budget,
        "station_minutes": station, "pet_allowed": pet_allowed,
    }

    if errors:
        # 不正入力あり: 入力値を保持したまま入力画面へ戻し、該当欄を強調表示させる（HTTP 400）。
        return render_template("index.html", condition=condition,
                               errors=errors, use_mock=config.USE_MOCK), 400

    # 検証OK: 提案画面でも参照できるよう条件をセッションに残してから遷移する。
    session["condition"] = condition
    return redirect(url_for("proposals"))


# ------------------------------------------------------------------
# ② 物件提案
# ------------------------------------------------------------------
@app.route("/proposals")
def proposals():
    """保存済みの希望条件で物件を適合度順に並べ、提案一覧を表示する。"""
    # 条件未入力で直接開かれた場合は入力画面へ誘導する。
    condition = session.get("condition")
    if not condition:
        return redirect(url_for("index"))

    ranked = matching.match_properties(condition, repository.get_all_properties())
    # 適合度40%以上を「提示に値する物件」とみなす。
    # 1件も無ければ、条件を緩めた候補として全件を提示（relaxed=Trueで画面に一言添える）。
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
    """1物件の詳細を表示する。希望条件があれば、その物件の適合度も併せて見せる。"""
    prop = repository.get_property(property_id)
    if not prop:
        return "物件が見つかりません", 404

    # 条件が未入力でも詳細自体は見せたいので、適合度は「あれば表示」に留める。
    condition = session.get("condition") or {}
    calc = matching.calculate_score(condition, prop) if condition else None
    score = calc["score"] if calc else None
    return render_template("detail.html", prop=prop, condition=condition,
                           score=score)


@app.route("/api/analyze/<property_id>", methods=["POST"])
def api_analyze(property_id):
    """詳細画面の「課題・懸念点を確認する」から呼ばれ、AI分析結果をJSONで返す。"""
    prop = repository.get_property(property_id)
    if not prop:
        return jsonify({"error": "物件が見つかりません"}), 404
    # 分析は「希望条件と物件の突き合わせ」なので、条件が無いと成立しない。
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
    """チャットドロワーからの質問を受け、AI応答を返しつつ履歴を保存する。"""
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify({"error": "質問を入力してください。"}), 400

    # 現在の希望条件を文脈として渡すと、条件を踏まえた回答が得られる。
    reply = ai.generate_chat_reply(question, context={"condition": session.get("condition")})

    # 会話は永続記録としてDB（chatsテーブル）へ保存し、
    # 併せて画面即時表示用にセッションにも積む（Supabase未接続時はセッションのみ）。
    repository.save_chat(question, reply)
    history = session.get("chat_history", [])
    history.append({"question": question, "answer": reply})
    # Cookieの肥大化を防ぐため、直近50件だけ保持する。
    session["chat_history"] = history[-50:]
    return jsonify({"answer": reply})


# ------------------------------------------------------------------
# ⑤ 入居までの手順確認
# ------------------------------------------------------------------
@app.route("/property/<property_id>/flow")
def move_in_flow(property_id):
    """物件の取引種別（賃貸/購入）に応じた入居手続きフローを表示する。"""
    prop = repository.get_property(property_id)
    if not prop:
        return "物件が見つかりません", 404
    # 賃貸と購入で手続きが異なるため、取引種別でフローを引き分ける。
    steps = repository.get_move_in_flow(prop["deal_type"])
    return render_template("flow.html", prop=prop, steps=steps)


# ローカル実行のエントリポイント（本番Vercelではこの分岐は使われず、WSGIのappが呼ばれる）。
if __name__ == "__main__":
    import os
    # ポートは環境変数PORT優先（無ければ5000）。ホスティング環境の指定に合わせるため。
    port = int(os.environ.get("PORT", 5000))
    # use_reloader=False: リローダーが子プロセスを常駐させると
    # プレビュー/サーバ管理でプロセスが残るため無効化している。
    app.run(debug=True, use_reloader=False, host="127.0.0.1", port=port)
