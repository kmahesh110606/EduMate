(function () {
  function $(id) {
    return document.getElementById(id);
  }

  const input = $("navbarSearchInput");
  const dropdown = $("navbarSearchDropdown");
  if (!input || !dropdown) return;

  let abortController = null;
  let debounceTimer = null;

  function hide() {
    dropdown.classList.remove("show");
    dropdown.innerHTML = "";
  }

  function show() {
    dropdown.classList.add("show");
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function render(results) {
    if (!Array.isArray(results) || results.length === 0) {
      hide();
      return;
    }

    dropdown.innerHTML = results
      .map((r) => {
        const title = escapeHtml(r.title || "");
        const subtitle = escapeHtml(r.subtitle || "");
        const url = escapeHtml(r.url || "#");
        return `
          <a class="nav-search-item" href="${url}">
            <div class="nav-search-title">${title}</div>
            ${subtitle ? `<div class="nav-search-subtitle">${subtitle}</div>` : ""}
          </a>
        `;
      })
      .join("");

    show();
  }

  function showLoading() {
    dropdown.innerHTML = `<div class="nav-search-loading"><div class="nav-spinner" aria-label="Loading"></div></div>`;
    show();
  }

  async function doSearch(q) {
    if (abortController) abortController.abort();
    abortController = new AbortController();

    showLoading();

    try {
      const res = await fetch(`/search?q=${encodeURIComponent(q)}`,
        { signal: abortController.signal, headers: { "Accept": "application/json" } }
      );
      if (!res.ok) {
        hide();
        return;
      }
      const data = await res.json();
      render(data.results || []);
    } catch (e) {
      // AbortError is expected during fast typing
      hide();
    }
  }

  input.addEventListener("input", () => {
    const q = (input.value || "").trim();

    clearTimeout(debounceTimer);

    if (q.length < 2) {
      hide();
      return;
    }

    debounceTimer = setTimeout(() => doSearch(q), 180);
  });

  document.addEventListener("click", (e) => {
    const target = e.target;
    if (!target) return;

    if (target === input || dropdown.contains(target)) return;
    hide();
  });

  input.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      hide();
      input.blur();
    }
  });
})();
