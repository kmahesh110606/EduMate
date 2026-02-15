(function () {
  const answerInputs = document.querySelectorAll("input[name='correct_answer']");
  if (!answerInputs.length) return;

  answerInputs.forEach((input) => {
    input.addEventListener("input", () => {
      input.value = (input.value || "").toUpperCase().replace(/[^ABCD]/g, "");
    });
  });
})();
