(function () {
  function closeAll(except) {
    document.querySelectorAll(".custom-select.open").forEach((root) => {
      if (root !== except) root.classList.remove("open");
    });
  }

  function buildCustomSelect(select) {
    if (!select || select.dataset.customized === "1") return;
    if (select.multiple || Number(select.size || 1) > 1) return;

    select.dataset.customized = "1";

    const wrapper = document.createElement("div");
    wrapper.className = "custom-select";
    select.classList.forEach((className) => wrapper.classList.add(className));

    select.parentNode.insertBefore(wrapper, select);
    wrapper.appendChild(select);
    select.classList.add("custom-select-native");

    const trigger = document.createElement("button");
    trigger.type = "button";
    trigger.className = "custom-select-trigger";

    const label = document.createElement("span");
    label.className = "custom-select-label";

    const icon = document.createElement("i");
    icon.className = "ms-Icon ms-Icon--ChevronDown fluent-icon custom-select-icon";
    icon.setAttribute("aria-hidden", "true");

    trigger.appendChild(label);
    trigger.appendChild(icon);

    const menu = document.createElement("div");
    menu.className = "custom-select-menu";

    const options = Array.from(select.options || []);

    function renderOptions() {
      menu.innerHTML = "";
      options.forEach((opt) => {
        const item = document.createElement("button");
        item.type = "button";
        item.className = "custom-select-option";
        item.textContent = opt.text;
        item.dataset.value = opt.value;
        if (opt.disabled) item.disabled = true;
        if (opt.selected) item.classList.add("active");

        item.addEventListener("click", () => {
          if (item.disabled) return;
          select.value = opt.value;
          select.dispatchEvent(new Event("change", { bubbles: true }));
          wrapper.classList.remove("open");
        });

        menu.appendChild(item);
      });
    }

    function syncFromSelect() {
      const selected = select.options[select.selectedIndex];
      label.textContent = selected ? selected.text : "Select";

      menu.querySelectorAll(".custom-select-option").forEach((item) => {
        item.classList.toggle("active", item.dataset.value === select.value);
      });

      trigger.disabled = select.disabled;
      wrapper.classList.toggle("disabled", !!select.disabled);
    }

    trigger.addEventListener("click", () => {
      if (trigger.disabled) return;
      const opening = !wrapper.classList.contains("open");
      closeAll(wrapper);
      wrapper.classList.toggle("open", opening);
    });

    select.addEventListener("change", syncFromSelect);

    wrapper.appendChild(trigger);
    wrapper.appendChild(menu);

    renderOptions();
    syncFromSelect();
  }

  document.addEventListener("click", (event) => {
    if (!event.target.closest(".custom-select")) {
      closeAll(null);
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeAll(null);
  });

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("select").forEach(buildCustomSelect);
  });
})();
