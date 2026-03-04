document.addEventListener("DOMContentLoaded", () => {
  const drawer = document.getElementById("quizAttemptDrawer");
  const overlay = document.getElementById("quizAttemptDrawerOverlay");
  const drawerBody = document.getElementById("quizAttemptDrawerBody");
  const closeBtn = document.getElementById("quizAttemptDrawerClose");
  const triggerButtons = Array.from(document.querySelectorAll(".quiz-view-attempt-btn"));

  if (!drawer || !overlay || !drawerBody || !closeBtn || !triggerButtons.length) return;

  function openDrawer(templateId) {
    const template = document.getElementById(templateId);
    if (!template) return;

    drawerBody.innerHTML = template.innerHTML;
    drawer.classList.add("open");
    overlay.classList.add("open");
    drawer.setAttribute("aria-hidden", "false");
    overlay.setAttribute("aria-hidden", "false");
    document.body.classList.add("drawer-open");
  }

  function closeDrawer() {
    drawer.classList.remove("open");
    overlay.classList.remove("open");
    drawer.setAttribute("aria-hidden", "true");
    overlay.setAttribute("aria-hidden", "true");
    document.body.classList.remove("drawer-open");
  }

  triggerButtons.forEach(button => {
    button.addEventListener("click", () => {
      const templateId = button.dataset.attemptTemplateId;
      openDrawer(templateId);
    });
  });

  closeBtn.addEventListener("click", closeDrawer);
  overlay.addEventListener("click", closeDrawer);

  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && drawer.classList.contains("open")) {
      closeDrawer();
    }
  });
});
