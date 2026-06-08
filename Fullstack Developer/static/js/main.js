/* main.js — Dark mode toggle + Live search */

// ── Dark mode ──────────────────────────────────────────────────
const html = document.documentElement;
const themeBtn = document.getElementById("themeBtn");
const saved = localStorage.getItem("theme") || "light";
html.setAttribute("data-theme", saved);
updateIcon(saved);

function toggleTheme() {
  const current = html.getAttribute("data-theme");
  const next = current === "dark" ? "light" : "dark";
  html.setAttribute("data-theme", next);
  localStorage.setItem("theme", next);
  updateIcon(next);
}

function updateIcon(theme) {
  if (themeBtn) themeBtn.textContent = theme === "dark" ? "☀️" : "🌙";
}

// ── Live search (client-side filter) ──────────────────────────
const liveSearch = document.getElementById("liveSearch");
const grid = document.getElementById("newsGrid");

if (liveSearch && grid) {
  liveSearch.addEventListener("input", () => {
    const q = liveSearch.value.toLowerCase().trim();
    const cards = grid.querySelectorAll(".card");
    let visible = 0;
    cards.forEach(card => {
      const text = card.textContent.toLowerCase();
      const show = !q || text.includes(q);
      card.style.display = show ? "" : "none";
      if (show) visible++;
    });
  });
}
