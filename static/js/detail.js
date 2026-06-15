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
