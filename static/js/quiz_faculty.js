document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("quizAttemptModal");
  const modalBody = document.getElementById("quizAttemptModalBody");
  const closeBtn = document.getElementById("quizAttemptModalClose");
  const triggerButtons = Array.from(document.querySelectorAll(".quiz-view-attempt-btn"));

  if (!modal || !modalBody || !closeBtn || !triggerButtons.length) return;

  function openModal(templateId) {
    const template = document.getElementById(templateId);
    if (!template) return;

    modalBody.innerHTML = template.innerHTML;
    modal.style.display = "flex";
    modal.setAttribute("aria-hidden", "false");
    document.body.classList.add("drawer-open");
  }

  function closeModal() {
    modal.style.display = "none";
    modal.setAttribute("aria-hidden", "true");
    document.body.classList.remove("drawer-open");
  }

  triggerButtons.forEach(button => {
    button.addEventListener("click", () => {
      const templateId = button.dataset.attemptTemplateId;
      openModal(templateId);
    });
  });

  closeBtn.addEventListener("click", closeModal);

  modal.addEventListener("click", event => {
    if (event.target === modal) {
      closeModal();
    }
  });

  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && modal.style.display === "flex") {
      closeModal();
    }
  });
});
