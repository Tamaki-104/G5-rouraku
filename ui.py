"""
画面テンプレート（HTML / CSS / JavaScript）を Python 内に集約したモジュール。

概要:
    別ファイルの .html / .css / .js を持たず、すべて Python の文字列として保持する。
    app.py で Jinja の DictLoader に TEMPLATES を渡すことで、テンプレート継承
    （{% extends "base.html" %}）もそのまま機能する。CSS / JS はブラウザに配信
    されるが、リポジトリのソースはすべて .py に統一される（言語Python統一の方針）。

構成:
    _CSS / _CHAT_JS / _DETAIL_JS … 見た目・挙動の素材（base/detailに埋め込む）
    _BASE / _INDEX / _PROPOSALS / _DETAIL / _FLOW … 各画面のHTML
    TEMPLATES … 上記をテンプレート名で引けるようにした辞書（app.pyが読み込む）

作成    : チーム労楽
Copyright (c) 2026 チーム労楽. All rights reserved.
"""

# ------------------------------------------------------------------
# CSS（base に <style> で埋め込む）— エディトリアル調のスタイリッシュUI
# ------------------------------------------------------------------
_CSS = """
:root {
  --bg: #f5f2ea;
  --surface: #ffffff;
  --surface-2: #faf7f0;
  --ink: #1b1915;
  --ink-soft: #433d34;
  --muted: #857e71;
  --line: #e7e1d4;
  --accent: #1f5b45;
  --accent-hover: #133c2d;
  --accent-soft: #e9f0ea;
  --sand: #b1854a;
  --sand-soft: #f5edda;
  --danger: #b0432d;
  --danger-soft: #f6e9e5;
  --radius: 14px;
  --radius-sm: 9px;
  --shadow: 0 1px 2px rgba(27,25,21,.04), 0 8px 24px -12px rgba(27,25,21,.18);
  --font-sans: "Noto Sans JP", system-ui, -apple-system, sans-serif;
  --font-display: "Zen Kaku Gothic New", "Noto Sans JP", sans-serif;
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  font-family: var(--font-sans);
  background:
    radial-gradient(1200px 500px at 100% -10%, #eef3ec 0%, rgba(238,243,236,0) 60%),
    var(--bg);
  color: var(--ink);
  line-height: 1.7;
  -webkit-font-smoothing: antialiased;
}
::selection { background: var(--accent); color: #fff; }
a { color: inherit; }

/* header */
.site-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 clamp(20px, 5vw, 44px); height: 66px;
  background: rgba(245,242,234,.82);
  backdrop-filter: saturate(140%) blur(10px);
  border-bottom: 1px solid var(--line);
  position: sticky; top: 0; z-index: 20;
  transition: padding-right .28s ease;
}
.brand {
  display: inline-flex; align-items: center; gap: 10px;
  font-family: var(--font-display); font-weight: 900; font-size: 20px;
  letter-spacing: .02em; color: var(--ink); text-decoration: none;
}
.brand-mark {
  width: 22px; height: 22px; border-radius: 7px;
  background: linear-gradient(135deg, var(--accent), #3f8c6e);
  position: relative; box-shadow: inset 0 0 0 2px rgba(255,255,255,.28);
}
.brand-mark::after {
  content: ""; position: absolute; inset: 6px 6px auto 6px; height: 6px;
  border-radius: 2px; background: rgba(255,255,255,.9);
}
.site-header nav { display: flex; align-items: center; gap: 6px; }
.nav-link, .nav-chat-btn {
  font-family: var(--font-sans); font-size: 14px; color: var(--ink-soft);
  text-decoration: none; background: none; border: none; cursor: pointer;
  padding: 7px 12px; border-radius: 8px; position: relative; transition: color .18s, background .18s;
}
.nav-link:hover, .nav-chat-btn:hover { color: var(--accent); background: var(--accent-soft); }
.nav-chat-btn { display: inline-flex; align-items: center; gap: 6px; font-weight: 600; }

/* layout */
.container { max-width: 940px; margin: 0 auto; padding: clamp(28px, 5vw, 56px) 22px 72px; }
.site-footer { text-align: center; color: var(--muted); padding: 40px 22px; font-size: 12.5px; letter-spacing: .02em; }

/* typography / hero */
.eyebrow {
  display: inline-block; font-size: 11.5px; font-weight: 700;
  letter-spacing: .18em; text-transform: uppercase; color: var(--accent);
  margin-bottom: 10px;
}
.page-hero { margin-bottom: 28px; }
h1 {
  font-family: var(--font-display); font-weight: 900; letter-spacing: .01em;
  font-size: clamp(26px, 4vw, 34px); line-height: 1.25; margin: 0;
}
h2 { font-family: var(--font-display); font-weight: 700; font-size: 19px; letter-spacing: .01em; }
.lead { color: var(--muted); font-size: 15px; margin: 12px 0 0; max-width: 60ch; }
.back {
  display: inline-block; color: var(--muted); text-decoration: none;
  font-size: 13px; margin-bottom: 14px; transition: color .18s;
}
.back:hover { color: var(--accent); }

/* card */
.card {
  background: var(--surface); border: 1px solid var(--line);
  border-radius: var(--radius); padding: 24px; margin: 18px 0;
  box-shadow: var(--shadow);
}

.badge-mock {
  display: inline-flex; align-items: center; gap: 7px;
  background: var(--sand-soft); color: #8a6a2f;
  border: 1px solid #ecdcba; padding: 6px 13px; border-radius: 999px; font-size: 12px; font-weight: 600;
}
.badge-mock::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: var(--sand); }

/* form */
.form .field { margin-bottom: 20px; }
.field label { display: block; font-weight: 600; font-size: 13.5px; margin-bottom: 8px; letter-spacing: .01em; }
.field input[type=text], .field input[type=number] {
  width: 100%; padding: 12px 14px; border: 1px solid var(--line);
  border-radius: var(--radius-sm); font-size: 15px; font-family: inherit;
  background: var(--surface-2); color: var(--ink); transition: border-color .18s, box-shadow .18s, background .18s;
}
.field input::placeholder { color: #b3ab9d; }
.field input:focus {
  outline: none; border-color: var(--accent); background: #fff;
  box-shadow: 0 0 0 4px var(--accent-soft);
}
.field.checkbox label { font-weight: 500; display: inline-flex; align-items: center; gap: 9px; cursor: pointer; }
.field.checkbox input { width: 17px; height: 17px; accent-color: var(--accent); }
.field .req { color: var(--danger); font-size: 10.5px; font-weight: 700; margin-left: 6px; letter-spacing: .08em; }
.field .hint { color: var(--muted); font-size: 12px; margin-top: 6px; display: block; }
.field .err { color: var(--danger); font-size: 12.5px; margin-top: 6px; display: block; }
.field.has-error input { border-color: var(--danger); background: var(--danger-soft); }

/* buttons */
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  border: 1px solid transparent; border-radius: var(--radius-sm); cursor: pointer;
  padding: 12px 22px; font-size: 14.5px; font-weight: 600; font-family: inherit;
  letter-spacing: .01em; text-decoration: none; transition: transform .16s, box-shadow .16s, background .18s, border-color .18s;
}
.btn.primary { background: var(--accent); color: #fff; box-shadow: 0 8px 18px -10px rgba(31,91,69,.7); }
.btn.primary:hover { background: var(--accent-hover); transform: translateY(-1px); box-shadow: 0 12px 22px -10px rgba(31,91,69,.75); }
.btn.ghost { background: transparent; border-color: var(--line); color: var(--ink); }
.btn.ghost:hover { border-color: var(--accent); color: var(--accent); background: var(--accent-soft); }
.btn.small { padding: 9px 15px; font-size: 13px; }
.btn.block { width: 100%; margin-top: 6px; }

/* proposals */
.cond-summary {
  display: flex; flex-wrap: wrap; align-items: center; gap: 10px 14px;
  font-size: 13.5px; color: var(--ink-soft); padding: 16px 20px;
}
.cond-summary strong { color: var(--ink); font-weight: 700; }
.cond-summary .btn { margin-left: auto; }
.notice {
  background: var(--sand-soft); border: 1px solid #ecdcba; color: #8a6a2f;
  padding: 14px 18px; border-radius: var(--radius-sm); font-size: 13.5px;
}

.property-list { display: flex; flex-direction: column; gap: 18px; margin-top: 20px; }
.property-card { display: flex; gap: 22px; padding: 18px; align-items: stretch; }
.property-card .thumb {
  width: 232px; height: 164px; border-radius: 10px; overflow: hidden;
  flex: none; background: var(--surface-2); position: relative;
}
.property-card .thumb img { width: 100%; height: 100%; object-fit: cover; display: block; }
.property-body { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.property-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 18px; }
.eyebrow-inline { font-size: 11px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }
.property-head h2 { margin: 3px 0 0; }
.tags { display: flex; flex-wrap: wrap; gap: 7px; margin: 12px 0 16px; }
.tag {
  font-size: 12.5px; color: var(--ink-soft); background: var(--surface-2);
  border: 1px solid var(--line); padding: 4px 11px; border-radius: 999px;
}
.tag.rent { color: var(--accent); font-weight: 700; background: var(--accent-soft); border-color: #cfe1d5; }
.property-body .btn { align-self: flex-start; margin-top: auto; }

/* score */
.score-wrap { min-width: 132px; text-align: right; flex: none; }
.score-top { display: flex; align-items: baseline; justify-content: flex-end; gap: 8px; }
.score-pct { font-family: var(--font-display); font-weight: 900; font-size: 30px; line-height: 1; color: var(--ink); }
.score-pct small { font-size: 14px; font-weight: 700; color: var(--muted); margin-left: 1px; }
.score-rank { font-size: 11px; font-weight: 700; padding: 3px 9px; border-radius: 999px; letter-spacing: .04em; }
.rank-高い { background: var(--accent-soft); color: var(--accent); }
.rank-普通 { background: var(--sand-soft); color: #8a6a2f; }
.rank-低い { background: var(--danger-soft); color: var(--danger); }
.score-bar { margin-top: 10px; height: 6px; background: var(--line); border-radius: 999px; overflow: hidden; }
.score-bar > span { display: block; height: 100%; border-radius: 999px; background: linear-gradient(90deg, var(--accent), #4f9a79); }

/* detail */
.detail-grid { display: grid; grid-template-columns: 1.05fr 1fr; gap: 22px; align-items: start; margin-top: 6px; }
.detail-img { width: 100%; border-radius: var(--radius); border: 1px solid var(--line); display: block; }
.spec { width: 100%; border-collapse: collapse; }
.spec th, .spec td { text-align: left; padding: 12px 4px; border-bottom: 1px solid var(--line); font-size: 14px; }
.spec tr:last-child th, .spec tr:last-child td { border-bottom: none; }
.spec th { color: var(--muted); width: 40%; font-weight: 600; }
.spec td { font-weight: 500; }
.score-big { font-size: 15px; color: var(--muted); margin: 0 0 14px; }
.score-big strong { font-family: var(--font-display); font-size: 24px; color: var(--accent); margin-left: 6px; }
.desc { font-size: 14px; color: var(--ink-soft); margin: 18px 0 0; }
.analyze-box h2 { margin-top: 0; }
.analysis {
  white-space: pre-wrap; background: var(--surface-2); border: 1px solid var(--line);
  border-radius: var(--radius-sm); padding: 18px; font-family: inherit; font-size: 14px;
  margin-top: 16px; line-height: 1.85;
}
.hidden { display: none; }

/* flow timeline */
.flow-steps { list-style: none; padding: 0; margin: 8px 0 0; position: relative; }
.flow-step { display: flex; gap: 18px; align-items: flex-start; padding: 18px 20px; }
.step-num {
  flex: none; width: 40px; height: 40px; border-radius: 12px;
  background: var(--accent-soft); color: var(--accent); border: 1px solid #cfe1d5;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-display); font-weight: 900; font-size: 17px;
}
.flow-step h3 { margin: 6px 0 3px; font-size: 16px; font-family: var(--font-display); font-weight: 700; }
.flow-step p { margin: 0; color: var(--muted); font-size: 13.5px; }

/* chat drawer */
:root { --chat-width: 380px; }
.page-wrap { transition: margin-right .3s cubic-bezier(.4,0,.2,1); }
body.chat-open .page-wrap { margin-right: var(--chat-width); }
body.chat-open .site-header { padding-right: calc(clamp(20px,5vw,44px) + var(--chat-width)); }

#chat-launcher {
  position: fixed; right: 24px; bottom: 24px; z-index: 30;
  width: 58px; height: 58px; border-radius: 18px; border: none; cursor: pointer;
  background: var(--accent); color: #fff;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 12px 26px -8px rgba(31,91,69,.6);
  transition: right .3s cubic-bezier(.4,0,.2,1), transform .18s, background .18s;
}
#chat-launcher:hover { transform: translateY(-2px) scale(1.03); background: var(--accent-hover); }
body.chat-open #chat-launcher { right: calc(24px + var(--chat-width)); }

.chat-drawer {
  position: fixed; top: 0; right: 0; z-index: 40;
  width: var(--chat-width); height: 100%;
  background: var(--surface); border-left: 1px solid var(--line);
  box-shadow: -18px 0 40px -24px rgba(27,25,21,.45);
  display: flex; flex-direction: column;
  transform: translateX(100%); transition: transform .3s cubic-bezier(.4,0,.2,1);
}
body.chat-open .chat-drawer { transform: translateX(0); }
.chat-drawer-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 18px 20px; border-bottom: 1px solid var(--line);
}
.drawer-title {
  display: inline-flex; align-items: center; gap: 9px;
  font-family: var(--font-display); font-weight: 700; font-size: 15px;
}
.drawer-title .dot {
  width: 8px; height: 8px; border-radius: 50%; background: #3f9a6f;
  box-shadow: 0 0 0 3px var(--accent-soft);
}
.chat-close { background: none; border: none; font-size: 26px; line-height: 1; cursor: pointer; color: var(--muted); transition: color .18s; }
.chat-close:hover { color: var(--ink); }

.chat-window { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 12px; background: var(--surface-2); }
.chat-empty { color: var(--muted); font-size: 13.5px; line-height: 1.8; }
.bubble { max-width: 82%; padding: 11px 15px; border-radius: 16px; font-size: 14px; line-height: 1.7; }
.bubble.user { align-self: flex-end; background: var(--accent); color: #fff; border-bottom-right-radius: 5px; }
.bubble.bot { align-self: flex-start; background: #fff; color: var(--ink); border: 1px solid var(--line); border-bottom-left-radius: 5px; white-space: pre-wrap; }
.chat-form { display: flex; gap: 9px; padding: 14px; border-top: 1px solid var(--line); background: var(--surface); }
.chat-form input { flex: 1; padding: 12px 14px; border: 1px solid var(--line); border-radius: 10px; font-size: 14.5px; font-family: inherit; background: var(--surface-2); }
.chat-form input:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); background: #fff; }

/* responsive */
@media (max-width: 720px) {
  .detail-grid { grid-template-columns: 1fr; }
  .property-card { flex-direction: column; }
  .property-card .thumb { width: 100%; height: 190px; }
  .score-wrap { text-align: left; min-width: 0; }
  .score-top { justify-content: flex-start; }
}
@media (max-width: 640px) {
  :root { --chat-width: 88vw; }
  body.chat-open .page-wrap { margin-right: 0; }
  body.chat-open .site-header { padding-right: clamp(20px,5vw,44px); }
  body.chat-open #chat-launcher { right: 24px; }
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
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=Zen+Kaku+Gothic+New:wght@500;700;900&display=swap" rel="stylesheet">
  <style>{% raw %}__CSS__{% endraw %}</style>
</head>
<body>
  <header class="site-header">
    <a class="brand" href="{{ url_for('index') }}"><span class="brand-mark"></span>宅ラーク</a>
    <nav>
      <a class="nav-link" href="{{ url_for('index') }}">条件入力</a>
      <a class="nav-link" href="{{ url_for('proposals') }}">物件提案</a>
      <button type="button" class="nav-chat-btn" data-chat-toggle>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        AIに質問
      </button>
    </nav>
  </header>

  <div class="page-wrap">
    <main class="container">
      {% block content %}{% endblock %}
    </main>

    <footer class="site-footer">
      不動産マッチングシステム ・ チーム労楽 ・ 内部設計書ベースの試作版
    </footer>
  </div>

  <!-- AIコンシェルジュ：右側スライドイン式チャットドロワー（全ページ共通） -->
  <button type="button" id="chat-launcher" data-chat-toggle aria-label="AIに質問">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
  </button>

  <aside id="chat-drawer" class="chat-drawer" aria-hidden="true">
    <div class="chat-drawer-header">
      <span class="drawer-title"><span class="dot"></span>AIコンシェルジュ</span>
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
<div class="page-hero">
  <span class="eyebrow">Step 01 — 条件入力</span>
  <h1>あなたの住まいの希望を教えてください</h1>
  <p class="lead">条件を入力して検索すると、AIが適合度の高い順に物件を提案します。</p>
</div>

{% if use_mock %}
<p class="badge-mock">サンプルデータで動作中（デモモード）</p>
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

  <button type="submit" class="btn primary block">物件を検索する</button>
</form>
{% endblock %}
"""

_PROPOSALS = """{% extends "base.html" %}
{% block title %}物件提案｜宅ラーク{% endblock %}
{% block content %}
<div class="page-hero">
  <span class="eyebrow">Step 02 — 物件提案</span>
  <h1>あなたへのおすすめ</h1>
</div>

<div class="cond-summary card">
  <strong>検索条件</strong>
  <span>{{ condition.area }} ・ 予算 {{ '{:,}'.format(condition.budget) }}円以下 ・
  {{ condition.layout }} ・ 駅徒歩{{ condition.station_minutes }}分以内 ・
  ペット{{ '可のみ' if condition.pet_allowed else '不問' }}</span>
  <a class="btn ghost small" href="{{ url_for('index') }}">条件を変更</a>
</div>

{% if relaxed %}
<p class="notice">条件に完全合致する物件が見つかりませんでした。条件を緩和した候補を適合度順に表示します。</p>
{% endif %}

<div class="property-list">
  {% for p in properties %}
  <article class="card property-card">
    <div class="thumb"><img src="{{ p.image_url }}" alt="{{ p.name }}"></div>
    <div class="property-body">
      <div class="property-head">
        <div>
          <span class="eyebrow-inline">{{ p.deal_type }} ・ {{ p.building_type }}</span>
          <h2>{{ p.name }}</h2>
        </div>
        <div class="score-wrap">
          <div class="score-top">
            <span class="score-pct">{{ p.score }}<small>%</small></span>
            <span class="score-rank rank-{{ p.rank }}">{{ p.rank }}</span>
          </div>
          <div class="score-bar"><span style="width: {{ p.score }}%"></span></div>
        </div>
      </div>
      <div class="tags">
        <span class="tag">{{ p.area }}</span>
        <span class="tag">{{ p.layout }}</span>
        <span class="tag rent">家賃 {{ '{:,}'.format(p.rent) }}円</span>
        <span class="tag">駅徒歩{{ p.station_minutes }}分</span>
        <span class="tag">ペット{{ '可' if p.pet_allowed else '不可' }}</span>
      </div>
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
<div class="page-hero">
  <span class="eyebrow">Step 03 — 物件詳細</span>
  <h1>{{ prop.name }}</h1>
</div>

<div class="detail-grid">
  <img src="{{ prop.image_url }}" alt="{{ prop.name }}" class="detail-img">
  <div class="card">
    {% if score is not none %}<p class="score-big">あなたの条件との適合度<strong>{{ score }}%</strong></p>{% endif %}
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
  <h2>入居までの手順</h2>
  <p class="lead">{{ prop.deal_type }}の場合の手続きフローを確認できます。</p>
  <a class="btn ghost" href="{{ url_for('move_in_flow', property_id=prop.id) }}">入居フローを見る（{{ prop.deal_type }}）</a>
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
<div class="page-hero">
  <span class="eyebrow">Step 05 — 入居手順</span>
  <h1>入居までの手順</h1>
  <p class="lead">{{ prop.name }} は「{{ prop.deal_type }}」物件です。入居（引き渡し）までの手続きは以下のとおりです。</p>
</div>

<ol class="flow-steps card">
  {% for s in steps %}
  <li class="flow-step">
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
