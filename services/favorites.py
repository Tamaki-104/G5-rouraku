"""
お気に入り機能。物件のお気に入り登録/解除(トグル)と一覧表示を提供する Blueprint。

保存先はFlaskのセッション(署名Cookie)。ユーザーごとに保持でき、Vercelの
サーバーレスでも状態が残る(モジュール変数だとインスタンス間で共有されず消えるため)。
発表用の簡易実装であり、恒久保存が必要なら Supabase のテーブルへ移す。

作成: チーム労楽  /  (c) 2026 チーム労楽
"""
from flask import Blueprint, jsonify, request, session, render_template

from services import repository

favorites_bp = Blueprint("favorites", __name__)


def favorite_ids():
    """現在のお気に入り物件IDのリスト(登録順)を返す。"""
    return session.get("favorites", [])


@favorites_bp.route("/api/favorites", methods=["POST"])
def toggle_favorite():
    """物件のお気に入りを登録/解除し、結果の状態(favorited)を返す。"""
    data = request.get_json(silent=True) or {}
    property_id = data.get("property_id")
    if not property_id:
        return jsonify({"error": "property_id が必要です"}), 400

    favorites = session.get("favorites", [])
    if property_id in favorites:
        favorites.remove(property_id)
        favorited = False
    else:
        favorites.append(property_id)
        favorited = True
    session["favorites"] = favorites
    return jsonify({"property_id": property_id, "favorited": favorited})


@favorites_bp.route("/favorites")
def favorites_page():
    """お気に入りに登録した物件の一覧を表示する。"""
    # 登録順に物件を取得し、存在しないID(削除済み等)は除く。
    props = [p for p in (repository.get_property(i) for i in favorite_ids()) if p]
    return render_template("favorites.html", properties=props)
