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
