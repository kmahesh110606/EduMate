(function () {
  const storageKey = "edumate_theme";

  function applyTheme(theme) {
    const value = theme === "dark" ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", value);

    const toggleBtn = document.getElementById("themeToggleBtn");
    if (toggleBtn) {
      const iconEl = toggleBtn.querySelector(".theme-toggle-icon");
      if (iconEl) {
        iconEl.className = value === "dark"
          ? "ms-Icon ms-Icon--Sunny fluent-icon theme-toggle-icon"
          : "ms-Icon ms-Icon--ClearNight fluent-icon theme-toggle-icon";
      }
      toggleBtn.setAttribute("aria-label", value === "dark" ? "Switch to light theme" : "Switch to dark theme");
      toggleBtn.setAttribute("title", value === "dark" ? "Switch to light theme" : "Switch to dark theme");
    }
  }

  function getInitialTheme() {
    const saved = localStorage.getItem(storageKey);
    if (saved === "dark" || saved === "light") return saved;
    return "light";
  }

  function toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
    const next = current === "dark" ? "light" : "dark";
    localStorage.setItem(storageKey, next);
    applyTheme(next);
  }

  document.addEventListener("DOMContentLoaded", function () {
    applyTheme(getInitialTheme());

    const toggleBtn = document.getElementById("themeToggleBtn");
    if (toggleBtn) {
      toggleBtn.addEventListener("click", toggleTheme);
    }
  });
})();
