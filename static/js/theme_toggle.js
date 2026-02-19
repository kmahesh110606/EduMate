(function () {
  const storageKey = "edumate_theme";
  const moonSvg = '<svg width="24" height="24" fill="none" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M20.026 17.001c-2.762 4.784-8.879 6.423-13.663 3.661A9.965 9.965 0 0 1 3.13 17.68a.75.75 0 0 1 .365-1.132c3.767-1.348 5.785-2.91 6.956-5.146 1.232-2.353 1.551-4.93.689-8.463a.75.75 0 0 1 .769-.927 9.961 9.961 0 0 1 4.457 1.327c4.784 2.762 6.423 8.879 3.66 13.662Z" fill="#fff"/></svg>';
  const sunSvg = '<svg width="24" height="24" fill="none" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M11.996 18.532a1 1 0 0 1 .993.883l.007.117v1.456a1 1 0 0 1-1.993.116l-.007-.116v-1.456a1 1 0 0 1 1-1Zm6.037-1.932 1.03 1.03a1 1 0 0 1-1.415 1.413l-1.03-1.029a1 1 0 0 1 1.415-1.414Zm-10.66 0a1 1 0 0 1 0 1.414l-1.029 1.03a1 1 0 0 1-1.414-1.415l1.03-1.03a1 1 0 0 1 1.413 0ZM12.01 6.472a5.525 5.525 0 1 1 0 11.05 5.525 5.525 0 0 1 0-11.05Zm8.968 4.546a1 1 0 0 1 .117 1.993l-.117.007h-1.456a1 1 0 0 1-.116-1.993l.116-.007h1.456ZM4.479 10.99a1 1 0 0 1 .116 1.993l-.116.007H3.023a1 1 0 0 1-.117-1.993l.117-.007h1.456Zm1.77-6.116.095.083 1.03 1.03a1 1 0 0 1-1.32 1.497L5.958 7.4 4.93 6.371a1 1 0 0 1 1.32-1.497Zm12.813.083a1 1 0 0 1 .083 1.32l-.083.094-1.03 1.03a1 1 0 0 1-1.497-1.32l.084-.095 1.029-1.03a1 1 0 0 1 1.414 0ZM12 2.013a1 1 0 0 1 .993.883l.007.117v1.455a1 1 0 0 1-1.993.117L11 4.468V3.013a1 1 0 0 1 1-1Z" fill="#fff"/></svg>';

  function applyTheme(theme) {
    const value = theme === "dark" ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", value);

    const toggleBtn = document.getElementById("themeToggleBtn");
    if (toggleBtn) {
      toggleBtn.innerHTML = value === "dark" ? sunSvg : moonSvg;
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
