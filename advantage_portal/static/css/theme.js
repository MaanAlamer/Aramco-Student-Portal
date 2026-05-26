(function () {
  const KEY = "aa_theme"; // "dark" | "light"
  const root = document.documentElement;

  function setTheme(theme) {
    if (theme === "light") root.setAttribute("data-theme", "light");
    else root.removeAttribute("data-theme");
    localStorage.setItem(KEY, theme);
    updateButtons();
  }

  function updateButtons() {
    const isLight = root.getAttribute("data-theme") === "light";
    document.querySelectorAll("[data-theme-toggle]").forEach((btn) => {
      btn.innerHTML = isLight
        ? '🌙 <span>الوضع الداكن</span>'
        : '☀️ <span>الوضع النهاري</span>';
    });
  }

  const saved = localStorage.getItem(KEY);
  setTheme(saved === "light" ? "light" : "dark");

  document.addEventListener("click", function (e) {
    const btn = e.target.closest("[data-theme-toggle]");
    if (!btn) return;
    const isLight = root.getAttribute("data-theme") === "light";
    setTheme(isLight ? "dark" : "light");
  });

  window.AATheme = { setTheme };
})();
