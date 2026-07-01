"""
画面テンプレート（HTML / CSS / JavaScript）を Python 内に集約したモジュール。

別ファイルの .html / .css / .js を持たず、すべて Python の文字列として保持する。
app.py で Jinja の DictLoader に TEMPLATES を渡すことで、テンプレート継承
（{% extends "base.html" %}）もそのまま機能する。
CSS / JS はブラウザに配信されるが、リポジトリのソースはすべて .py になる。
"""

# ------------------------------------------------------------------
# CSS（base に <style> で埋め込む）
# ------------------------------------------------------------------
_CSS = """
:root {
  --bg: #f4f6f9;
  --card: #ffffff;
  --primary: #2f6df0;
  --primary-dark: #1f54c4;
  --text: #1f2733;
  --muted: #6b7686;
  --border: #e2e7ef;
  --good: #1f9d55;
  --warn: #d9822b;
  --bad: #d64545;
}

* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "Segoe UI", "Hiragino Kaku Gothic ProN", "Meiryo", sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
}

/* header / footer */
.site-header {
  display: flex; align-items: center; justify-content: space-between;
  background: var(--card); padding: 0 24px; height: 60px;
  border-bottom: 1px solid var(--border);
  position: sticky; top: 0; z-index: 10;
}
.brand { font-size: 20px; font-weight: 700; color: var(--primary); text-decoration: none; }
.site-header nav a { margin-left: 18px; color: var(--text); text-decoration: none; font-size: 14px; }
.site-header nav a:hover { color: var(--primary); }
.site-footer { text-align: center; color: var(--muted); padding: 24px; }

.container { max-width: 860px; margin: 0 auto; padding: 28px 20px; }
h1 { font-size: 24px; }
.lead { color: var(--muted); }

/* card */
.card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: 12px; padding: 20px; margin: 16px 0;
  box-shadow: 0 1px 3px rgba(0,0,0,.04);
}

.badge-mock {
  display: inline-block; background: #fff7e6; color: var(--warn);
  border: 1px solid #ffe1b3; padding: 4px 10px; border-radius: 999px; font-size: 12px;
}

/* form */
.form .field { margin-bottom: 16px; }
.field label { display: block; font-weight: 600; margin-bottom: 6px; }
.field input[type=text], .field input[type=number] {
  width: 100%; padding: 10px 12px; border: 1px solid var(--border);
  border-radius: 8px; font-size: 15px;
}
.field.checkbox label { font-weight: 400; }
.field .req { color: var(--bad); font-size: 11px; margin-left: 4px; }
.field .hint { color: var(--muted); }
.field .err { color: var(--bad); }
.field.has-error input { border-color: var(--bad); background: #fff5f5; }

/* buttons */
.btn {
  display: inline-block; border: none; border-radius: 8px; cursor: pointer;
  padding: 11px 18px; font-size: 15px; text-decoration: none; text-align: center;
}
.btn.primary { background: var(--primary); color: #fff; }
.btn.primary:hover { background: var(--primary-dark); }
.btn.ghost { background: transparent; border: 1px solid var(--primary); color: var(--primary); }
.btn.small { padding: 7px 12px; font-size: 13px; }

/* proposals */
.cond-summary { font-size: 14px; }
.cond-summary .btn { margin-left: 8px; }
.notice {
  background: #fff7e6; border: 1px solid #ffe1b3; color: var(--warn);
  padding: 12px 16px; border-radius: 8px;
}
.property-card { display: flex; gap: 16px; align-items: stretch; }
.thumb { width: 200px; height: 130px; object-fit: cover; border-radius: 8px; }
.property-body { flex: 1; }
.property-head { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.property-head h2 { font-size: 18px; margin: 0; }
.meta { color: var(--muted); font-size: 13px; }
.score { font-size: 13px; font-weight: 700; padding: 4px 10px; border-radius: 999px; white-space: nowrap; }
.score-高い { background: #e3f6ec; color: var(--good); }
.score-普通 { background: #fff3e0; color: var(--warn); }
.score-低い { background: #fdeaea; color: var(--bad); }

/* detail */
.back { color: var(--muted); text-decoration: none; font-size: 14px; }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; align-items: start; }
.detail-img { width: 100%; border-radius: 12px; }
.spec { width: 100%; border-collapse: collapse; }
.spec th, .spec td { text-align: left; padding: 8px 6px; border-bottom: 1px solid var(--border); font-size: 14px; }
.spec th { color: var(--muted); width: 38%; font-weight: 600; }
.score-big { font-size: 16px; }
.desc { font-size: 14px; color: var(--text); }
.analysis {
  white-space: pre-wrap; background: #f7f9fc; border: 1px solid var(--border);
  border-radius: 8px; padding: 16px; font-family: inherit; font-size: 14px; margin-top: 14px;
}
.hidden { display: none; }

/* chat drawer (右側スライドイン) */
:root { --chat-width: 360px; }

/* 本文を左にずらして、ドロワーで隠れないようにする */
.page-wrap { transition: margin-right .25s ease; }
.site-header { transition: padding-right .25s ease; }
body.chat-open .page-wrap { margin-right: var(--chat-width); }
body.chat-open .site-header { padding-right: calc(24px + var(--chat-width)); }

/* フローティング起動ボタン */
#chat-launcher {
  position: fixed; right: 22px; bottom: 22px; z-index: 30;
  width: 56px; height: 56px; border-radius: 50%; border: none; cursor: pointer;
  background: var(--primary); color: #fff; font-size: 24px;
  box-shadow: 0 4px 14px rgba(47,109,240,.4);
  transition: right .25s ease, transform .15s ease;
}
#chat-launcher:hover { transform: scale(1.05); }
body.chat-open #chat-launcher { right: calc(22px + var(--chat-width)); }

/* ナビ内のボタン */
.nav-chat-btn {
  margin-left: 18px; background: transparent; border: none; cursor: pointer;
  color: var(--text); font-size: 14px; font-family: inherit;
}
.nav-chat-btn:hover { color: var(--primary); }

/* ドロワー本体 */
.chat-drawer {
  position: fixed; top: 0; right: 0; z-index: 40;
  width: var(--chat-width); height: 100%;
  background: var(--card); border-left: 1px solid var(--border);
  box-shadow: -4px 0 18px rgba(0,0,0,.08);
  display: flex; flex-direction: column;
  transform: translateX(100%); transition: transform .25s ease;
}
body.chat-open .chat-drawer { transform: translateX(0); }
.chat-drawer-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 16px; border-bottom: 1px solid var(--border); font-weight: 700;
}
.chat-close {
  background: none; border: none; font-size: 24px; line-height: 1;
  cursor: pointer; color: var(--muted);
}
.chat-close:hover { color: var(--text); }

.chat-window {
  flex: 1; overflow-y: auto; padding: 16px;
  display: flex; flex-direction: column; gap: 10px;
}
.chat-empty { color: var(--muted); font-size: 14px; }
.bubble { max-width: 80%; padding: 10px 14px; border-radius: 14px; font-size: 14px; }
.bubble.user { align-self: flex-end; background: var(--primary); color: #fff; border-bottom-right-radius: 4px; }
.bubble.bot { align-self: flex-start; background: #eef1f6; color: var(--text); border-bottom-left-radius: 4px; white-space: pre-wrap; }
.chat-form { display: flex; gap: 8px; padding: 12px; border-top: 1px solid var(--border); }
.chat-form input { flex: 1; padding: 11px 12px; border: 1px solid var(--border); border-radius: 8px; font-size: 15px; }

/* flow */
.flow-steps { list-style: none; padding: 0; }
.flow-step { display: flex; gap: 16px; align-items: center; }
.step-num {
  flex: none; width: 36px; height: 36px; border-radius: 50%;
  background: var(--primary); color: #fff; display: flex;
  align-items: center; justify-content: center; font-weight: 700;
}
.flow-step h3 { margin: 0 0 2px; font-size: 16px; }
.flow-step p { margin: 0; color: var(--muted); font-size: 14px; }

@media (max-width: 640px) {
  .detail-grid { grid-template-columns: 1fr; }
  .property-card { flex-direction: column; }
  .thumb { width: 100%; height: 180px; }

  /* 画面が狭い場合はパネルを縮小し、本文押し出しはせずオーバーレイ表示 */
  :root { --chat-width: 86vw; }
  body.chat-open .page-wrap { margin-right: 0; }
  body.chat-open .site-header { padding-right: 24px; }
  body.chat-open #chat-launcher { right: 22px; }
}
"""

# ------------------------------------------------------------------
# JavaScript
# ------------------------------------------------------------------
_CHAT_JS = """
// AIコンシェルジュ：右側スライドイン式ドロワー（全ページ共通）
document.addEventListener("DOMContentLoaded", () => {
  const drawer = document.getElementById("chat-drawer");
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-input");
  const win = document.getElementById("chat-window");
  if (!drawer) return;

  // --- 開閉 ---
  function openDrawer() {
    document.body.classList.add("chat-open");
    drawer.setAttribute("aria-hidden", "false");
    win.scrollTop = win.scrollHeight;
    setTimeout(() => input && input.focus(), 200);
  }
  function closeDrawer() {
    document.body.classList.remove("chat-open");
    drawer.setAttribute("aria-hidden", "true");
  }
  function toggleDrawer() {
    document.body.classList.contains("chat-open") ? closeDrawer() : openDrawer();
  }

  document.querySelectorAll("[data-chat-toggle]").forEach((el) =>
    el.addEventListener("click", toggleDrawer));
  document.querySelectorAll("[data-chat-close]").forEach((el) =>
    el.addEventListener("click", closeDrawer));
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeDrawer();
  });

  // --- 送受信 ---
  function addBubble(text, cls) {
    const empty = win.querySelector(".chat-empty");
    if (empty) empty.remove();
    const div = document.createElement("div");
    div.className = "bubble " + cls;
    div.textContent = text;
    win.appendChild(div);
    win.scrollTop = win.scrollHeight;
    return div;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const q = input.value.trim();
    if (!q) return;
    addBubble(q, "user");
    input.value = "";
    const thinking = addBubble("回答を生成中...", "bot");

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });
      const data = await res.json();
      thinking.textContent = res.ok ? data.answer : (data.error || "エラーが発生しました。");
    } catch (err) {
      thinking.textContent = "通信エラーが発生しました。";
    }
    win.scrollTop = win.scrollHeight;
  });
});
"""

_DETAIL_JS = """
// 物件詳細：課題・懸念点のAI分析をAjaxで取得して表示
document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("analyze-btn");
  const out = document.getElementById("analysis-result");
  if (!btn) return;

  btn.addEventListener("click", async () => {
    btn.disabled = true;
    const original = btn.textContent;
    btn.textContent = "分析中...";
    out.classList.remove("hidden");
    out.textContent = "AIが分析しています...";

    try {
      const res = await fetch(`/api/analyze/${btn.dataset.id}`, { method: "POST" });
      const data = await res.json();
      out.textContent = res.ok ? data.analysis : (data.error || "分析に失敗しました。");
    } catch (e) {
      out.textContent = "通信エラーが発生しました。";
    } finally {
      btn.disabled = false;
      btn.textContent = original;
    }
  });
});
"""

# ------------------------------------------------------------------
# HTML テンプレート（Jinja）
# ------------------------------------------------------------------
_BASE = """<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}宅ラーク｜不動産マッチング{% endblock %}</title>
  <style>{% raw %}__CSS__{% endraw %}</style>
</head>
<body>
  <header class="site-header">
    <a class="brand" href="{{ url_for('index') }}">🏠 宅ラーク</a>
    <nav>
      <a href="{{ url_for('index') }}">条件入力</a>
      <a href="{{ url_for('proposals') }}">物件提案</a>
      <button type="button" class="nav-chat-btn" data-chat-toggle>AIに質問</button>
    </nav>
  </header>

  <div class="page-wrap">
    <main class="container">
      {% block content %}{% endblock %}
    </main>

    <footer class="site-footer">
      <small>不動産マッチングシステム / チーム労楽 — 内部設計書ベースの試作版</small>
    </footer>
  </div>

  <!-- AIコンシェルジュ：右側スライドイン式チャットドロワー（全ページ共通） -->
  <button type="button" id="chat-launcher" data-chat-toggle aria-label="AIに質問">💬</button>

  <aside id="chat-drawer" class="chat-drawer" aria-hidden="true">
    <div class="chat-drawer-header">
      <span>🤖 AIコンシェルジュ</span>
      <button type="button" class="chat-close" data-chat-close aria-label="閉じる">×</button>
    </div>
    <div id="chat-window" class="chat-window">
      {% for msg in chat_history %}
      <div class="bubble user">{{ msg.question }}</div>
      <div class="bubble bot">{{ msg.answer }}</div>
      {% else %}
      <p class="chat-empty">物件・条件・入居手続きについてお尋ねください。<br>例：「家賃を少し上げるとより良い物件はありますか？」</p>
      {% endfor %}
    </div>
    <form id="chat-form" class="chat-form">
      <input type="text" id="chat-input" placeholder="質問を入力..." autocomplete="off">
      <button type="submit" class="btn primary">送信</button>
    </form>
  </aside>

  <script>{% raw %}__CHAT_JS__{% endraw %}</script>
  {% block scripts %}{% endblock %}
</body>
</html>
"""

_INDEX = """{% extends "base.html" %}
{% block title %}条件入力｜宅ラーク{% endblock %}
{% block content %}
<h1>① 希望条件を入力</h1>
<p class="lead">条件を入力して「物件を検索する」を押すと、AIが適合度の高い順に物件を提案します。</p>

{% if use_mock %}
<p class="badge-mock">モックモードで動作中（Supabase/Gemini未接続・サンプルデータ使用）</p>
{% endif %}

<form method="post" action="{{ url_for('search') }}" class="card form" novalidate>
  <div class="field {% if errors and errors.area %}has-error{% endif %}">
    <label for="area">希望エリア <span class="req">必須</span></label>
    <input type="text" id="area" name="area" placeholder="例：渋谷区 または 新宿区/渋谷区"
           value="{{ condition.area if condition else '' }}">
    {% if errors and errors.area %}<small class="err">{{ errors.area }}</small>{% endif %}
    <small class="hint">複数指定は「/」で区切れます。</small>
  </div>

  <div class="field {% if errors and errors.budget %}has-error{% endif %}">
    <label for="budget">予算上限（円） <span class="req">必須</span></label>
    <input type="number" id="budget" name="budget" placeholder="例：80000" min="1"
           value="{{ condition.budget if condition and condition.budget is not none else '' }}">
    {% if errors and errors.budget %}<small class="err">{{ errors.budget }}</small>{% endif %}
  </div>

  <div class="field {% if errors and errors.layout %}has-error{% endif %}">
    <label for="layout">希望の間取り <span class="req">必須</span></label>
    <input type="text" id="layout" name="layout" placeholder="例：1LDK または 1LDK/2LDK"
           value="{{ condition.layout if condition else '' }}">
    {% if errors and errors.layout %}<small class="err">{{ errors.layout }}</small>{% endif %}
  </div>

  <div class="field {% if errors and errors.station_minutes %}has-error{% endif %}">
    <label for="station_minutes">駅からの距離（分以内） <span class="req">必須</span></label>
    <input type="number" id="station_minutes" name="station_minutes" placeholder="例：20" min="0"
           value="{{ condition.station_minutes if condition and condition.station_minutes is not none else '' }}">
    {% if errors and errors.station_minutes %}<small class="err">{{ errors.station_minutes }}</small>{% endif %}
  </div>

  <div class="field checkbox">
    <label>
      <input type="checkbox" name="pet_allowed" {% if condition and condition.pet_allowed %}checked{% endif %}>
      ペット可の物件のみ
    </label>
  </div>

  <button type="submit" class="btn primary">物件を検索する</button>
</form>
{% endblock %}
"""

_PROPOSALS = """{% extends "base.html" %}
{% block title %}物件提案｜宅ラーク{% endblock %}
{% block content %}
<h1>② 物件提案</h1>

<div class="cond-summary card">
  <strong>検索条件:</strong>
  エリア {{ condition.area }} ／ 予算 {{ '{:,}'.format(condition.budget) }}円以下 ／
  間取り {{ condition.layout }} ／ 駅徒歩{{ condition.station_minutes }}分以内 ／
  ペット{{ '可のみ' if condition.pet_allowed else '不問' }}
  <a class="btn ghost small" href="{{ url_for('index') }}">条件を変更</a>
</div>

{% if relaxed %}
<p class="notice">条件に完全合致する物件が見つかりませんでした。条件を緩和した候補を適合度順に表示します。</p>
{% endif %}

<div class="property-list">
  {% for p in properties %}
  <article class="card property-card">
    <img src="{{ p.image_url }}" alt="{{ p.name }}" class="thumb">
    <div class="property-body">
      <div class="property-head">
        <h2>{{ p.name }}</h2>
        <span class="score score-{{ p.rank }}">適合度 {{ p.score }}%（{{ p.rank }}）</span>
      </div>
      <p class="meta">
        {{ p.area }} ／ {{ p.layout }} ／ 家賃 {{ '{:,}'.format(p.rent) }}円 ／
        駅徒歩{{ p.station_minutes }}分 ／ {{ p.building_type }} ／
        ペット{{ '可' if p.pet_allowed else '不可' }} ／ {{ p.deal_type }}
      </p>
      <a class="btn primary small" href="{{ url_for('property_detail', property_id=p.id) }}">詳細・課題を確認</a>
    </div>
  </article>
  {% endfor %}
</div>
{% endblock %}
"""

_DETAIL = """{% extends "base.html" %}
{% block title %}{{ prop.name }}｜宅ラーク{% endblock %}
{% block content %}
<a class="back" href="{{ url_for('proposals') }}">← 物件提案に戻る</a>
<h1>③ {{ prop.name }}</h1>

<div class="detail-grid">
  <img src="{{ prop.image_url }}" alt="{{ prop.name }}" class="detail-img">
  <div class="card">
    {% if score is not none %}<p class="score-big">あなたの条件との適合度：<strong>{{ score }}%</strong></p>{% endif %}
    <table class="spec">
      <tr><th>エリア</th><td>{{ prop.area }}</td></tr>
      <tr><th>家賃</th><td>{{ '{:,}'.format(prop.rent) }}円</td></tr>
      <tr><th>間取り</th><td>{{ prop.layout }}</td></tr>
      <tr><th>駅からの距離</th><td>徒歩{{ prop.station_minutes }}分</td></tr>
      <tr><th>建物種別</th><td>{{ prop.building_type }}</td></tr>
      <tr><th>ペット</th><td>{{ '可' if prop.pet_allowed else '不可' }}</td></tr>
      <tr><th>取引種別</th><td>{{ prop.deal_type }}</td></tr>
    </table>
    <p class="desc">{{ prop.description }}</p>
  </div>
</div>

<section class="card analyze-box">
  <h2>課題・懸念点のAI分析</h2>
  <p class="lead">この物件があなたの希望とどう違うか、注意点をAIが分析します。</p>
  <button id="analyze-btn" class="btn primary" data-id="{{ prop.id }}">課題・懸念点を確認する</button>
  <pre id="analysis-result" class="analysis hidden"></pre>
</section>

<section class="card">
  <h2>⑤ 入居までの手順</h2>
  <a class="btn ghost" href="{{ url_for('move_in_flow', property_id=prop.id) }}">入居までのフローを確認する（{{ prop.deal_type }}）</a>
</section>
{% endblock %}

{% block scripts %}
<script>{% raw %}__DETAIL_JS__{% endraw %}</script>
{% endblock %}
"""

_FLOW = """{% extends "base.html" %}
{% block title %}入居手順｜宅ラーク{% endblock %}
{% block content %}
<a class="back" href="{{ url_for('property_detail', property_id=prop.id) }}">← 物件詳細に戻る</a>
<h1>⑤ 入居までの手順（{{ prop.deal_type }}）</h1>
<p class="lead">{{ prop.name }} は「{{ prop.deal_type }}」物件です。入居（引き渡し）までの手続きは以下のとおりです。</p>

<ol class="flow-steps">
  {% for s in steps %}
  <li class="card flow-step">
    <span class="step-num">{{ s.step }}</span>
    <div>
      <h3>{{ s.title }}</h3>
      <p>{{ s.detail }}</p>
    </div>
  </li>
  {% endfor %}
</ol>
{% endblock %}
"""

# プレースホルダに CSS / JS を差し込む（f-string を使わないので波かっこの衝突なし）
_BASE = _BASE.replace("__CSS__", _CSS).replace("__CHAT_JS__", _CHAT_JS)
_DETAIL = _DETAIL.replace("__DETAIL_JS__", _DETAIL_JS)

# Jinja DictLoader に渡すテンプレート辞書
TEMPLATES = {
    "base.html": _BASE,
    "index.html": _INDEX,
    "proposals.html": _PROPOSALS,
    "detail.html": _DETAIL,
    "flow.html": _FLOW,
}
