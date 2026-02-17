document.addEventListener("DOMContentLoaded", () => {

  const quizForm = document.getElementById("quizForm");
  if (!quizForm) return;

  const quizId = quizForm.dataset.quizId || "";
  const answersKey = `quiz_answers_${quizId}`;
  const timerKey = `quiz_timer_${quizId}`;

  const startScreen = document.getElementById("startScreen");
  const startQuizBtn = document.getElementById("startQuizBtn");
  const quizAttemptUI = document.getElementById("quizAttemptUI");
  const saveStatus = document.getElementById("saveStatus");
  const progressText = document.getElementById("progressText");
  const submitBtn = document.getElementById("submitBtn");

  /* ===================== QUESTION NAV ===================== */
  let blocks = Array.from(document.querySelectorAll(".question-block"));
  let current = 0;

  function shuffleArray(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
  }

  // Shuffle question display order (keep input names tied to original indexes)
  const card = quizForm.querySelector(".card");
  if (card && blocks.length > 1) {
    shuffleArray(blocks);
    blocks.forEach(b => card.appendChild(b));
  }

  // Shuffle options order per question (keep values A/B/C/D intact)
  document.querySelectorAll(".options").forEach(optionsEl => {
    const rows = Array.from(optionsEl.querySelectorAll(".option-row"));
    shuffleArray(rows);
    rows.forEach(r => optionsEl.appendChild(r));
  });

  function show(index) {
    if (!blocks.length) return;
    if (index < 0) index = 0;
    if (index > blocks.length - 1) index = blocks.length - 1;
    current = index;

    blocks.forEach(b => b.style.display = "none");
    blocks[index].style.display = "block";

    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");
    if (prevBtn) prevBtn.style.display = index === 0 ? "none" : "inline-block";
    if (nextBtn) nextBtn.style.display = index === blocks.length - 1 ? "none" : "inline-block";
    if (submitBtn) submitBtn.style.display = index === blocks.length - 1 ? "inline-block" : "none";

    if (progressText) {
      progressText.textContent = `Question ${index + 1} of ${blocks.length}`;
    }
  }

  function loadSavedAnswers() {
    let saved = null;
    try {
      saved = JSON.parse(localStorage.getItem(answersKey) || "null");
    } catch {
      saved = null;
    }
    if (!saved || typeof saved !== "object") return;

    Object.keys(saved).forEach(qIndex => {
      const val = saved[qIndex];
      if (!val) return;
      const radio = document.querySelector(`input[type=radio][name="answer_${qIndex}"][value="${val}"]`);
      if (radio) radio.checked = true;
    });

    if (saveStatus) saveStatus.textContent = "Restored saved answers.";
  }

  function saveAnswer(qIndex, value) {
    let saved = {};
    try {
      saved = JSON.parse(localStorage.getItem(answersKey) || "{}") || {};
    } catch {
      saved = {};
    }
    saved[qIndex] = value;
    localStorage.setItem(answersKey, JSON.stringify(saved));
    if (saveStatus) saveStatus.textContent = "Saved.";
  }

  /* ===================== AUTOSAVE (LOCAL) ===================== */
  document.querySelectorAll("input[type=radio]").forEach(radio => {
    radio.addEventListener("change", () => {
      const parts = radio.name.split("_");
      const qIndex = parts.length > 1 ? parts[1] : "";
      saveAnswer(qIndex, radio.value);
    });
  });

  /* ===================== TIMER (PERSISTENT) ===================== */
  const timerEl = document.getElementById("timer");
  let timerInterval = null;
  function startTimer() {
    if (!timerEl) return;

    const totalSeconds = parseInt(timerEl.dataset.duration || "0", 10) * 60;
    let remaining = localStorage.getItem(timerKey);
    remaining = remaining ? parseInt(remaining, 10) : totalSeconds;

    const tick = () => {
      const m = Math.floor(Math.max(remaining, 0) / 60);
      const s = Math.max(remaining, 0) % 60;
      timerEl.textContent = `Time Left: ${m}:${s.toString().padStart(2, "0")}`;

      remaining--;
      localStorage.setItem(timerKey, remaining);

      if (remaining < 0) {
        localStorage.removeItem(timerKey);
        localStorage.removeItem(answersKey);
        forceSubmit("time_up");
      }
    };

    tick();
    timerInterval = setInterval(tick, 1000);
  }

  /* ===================== JAIL MODE ===================== */
  let strikes = 0;
  const MAX_STRIKES = 2;
  let securityArmed = false;

  const jail = document.createElement("div");
  jail.style.cssText = `
    position:fixed;
    inset:0;
    background:rgba(0,0,0,0.85);
    color:#fff;
    display:none;
    align-items:center;
    justify-content:center;
    z-index:99999;
  `;
  jail.innerHTML = `
    <div>
      <h2>Exam Security Warning</h2>
      <p id="strikeText"></p>
    </div>
  `;
  document.body.appendChild(jail);

  const securityToast = document.createElement("div");
  securityToast.style.cssText = `
    position:fixed;
    top:18px;
    right:18px;
    background:rgba(14,15,17,0.9);
    color:#fff;
    padding:10px 14px;
    border-radius:12px;
    font-weight:700;
    font-size:0.92rem;
    z-index:100000;
    opacity:0;
    transform:translateY(-8px);
    transition:opacity .2s ease, transform .2s ease;
    pointer-events:none;
    max-width:min(92vw, 360px);
  `;
  document.body.appendChild(securityToast);

  let submitting = false;
  let allowUnload = false;
  let lastViolationAt = 0;
  let ignoreViolationsUntil = 0;
  let securityToastTimer = null;

  function showSecurityToast(message, isError) {
    securityToast.textContent = message;
    securityToast.style.background = isError ? "rgba(127, 10, 28, 0.92)" : "rgba(14, 15, 17, 0.9)";
    securityToast.style.opacity = "1";
    securityToast.style.transform = "translateY(0)";
    if (securityToastTimer) clearTimeout(securityToastTimer);
    securityToastTimer = setTimeout(() => {
      securityToast.style.opacity = "0";
      securityToast.style.transform = "translateY(-8px)";
    }, isError ? 2400 : 1800);
  }

  function forceSubmit(reason) {
    if (!securityArmed || submitting) return;
    submitting = true;
    allowUnload = true;
    securityArmed = false;
    try {
      const reasonEl = document.getElementById("autoSubmitReason");
      if (reasonEl) reasonEl.value = reason || "auto_submit";
    } catch {}
    if (timerInterval) clearInterval(timerInterval);
    localStorage.removeItem(timerKey);
    localStorage.removeItem(answersKey);
    quizForm.submit();
  }

  function registerViolation(reason) {
    if (!securityArmed || submitting) return;

    const now = Date.now();
    if (now < ignoreViolationsUntil) return;
    // Debounce repeated events (blur can fire multiple times)
    if (now - lastViolationAt < 800) return;
    lastViolationAt = now;

    strikes++;
    const strikeText = document.getElementById("strikeText");
    if (strikeText) {
      const prettyReason = reason ? ` (${reason})` : "";
      strikeText.innerText = `Violations: ${strikes} / ${MAX_STRIKES}${prettyReason}`;
    }
    showSecurityToast(`Security warning ${strikes}/${MAX_STRIKES}${reason ? `: ${reason}` : ""}`, false);

    jail.style.display = "flex";
    ignoreViolationsUntil = now + 2300;
    setTimeout(() => {
      jail.style.display = "none";
      // Try to pull them back into fullscreen after warning
      if (!document.fullscreenElement) enterFS();
    }, 2000);

    if (strikes >= MAX_STRIKES) {
      showSecurityToast("Malpractice limit reached. Auto-submitting quiz.", true);
      forceSubmit(reason || "malpractice");
    }
  }

  /* ===================== FORCE FULLSCREEN ===================== */
  function enterFS() {
    if (document.documentElement.requestFullscreen) {
      document.documentElement.requestFullscreen();
    }
  }

  document.addEventListener("fullscreenchange", () => {
    if (!securityArmed) return;
    if (!document.fullscreenElement) {
      registerViolation("fullscreen_exit");
    }
  });

  /* ===================== TAB / SWITCH DETECTION ===================== */
  let hiddenSince = null;
  document.addEventListener("visibilitychange", () => {
    if (!securityArmed) return;
    if (document.hidden) {
      hiddenSince = Date.now();
      return;
    }
    if (hiddenSince) {
      const hiddenMs = Date.now() - hiddenSince;
      hiddenSince = null;
      // Any tab switch counts as a violation; longer = still one violation.
      registerViolation(hiddenMs > 1500 ? "tab_switch_long" : "tab_switch");
    }
  });

  window.addEventListener("blur", () => {
    if (!securityArmed) return;
    registerViolation("window_blur");
  });

  /* ===================== BLOCK KEYS ===================== */
  document.addEventListener("keydown", e => {
    if (!securityArmed) return;
    const blocked =
      e.key === "PrintScreen" ||
      e.key === "F12" ||
      (e.ctrlKey && ["c","v","x","s","u","p"].includes(e.key.toLowerCase())) ||
      (e.altKey && e.key === "Tab") ||
      (e.metaKey && e.key === "Tab");

    if (blocked) {
      e.preventDefault();
      registerViolation("blocked_key");
    }
  });

  /* ===================== BLOCK RIGHT CLICK ===================== */
  document.addEventListener("contextmenu", e => {
    if (!securityArmed) return;
    e.preventDefault();
    registerViolation("right_click");
  });

  /* ===================== AUTO SUBMIT ON LEAVE ===================== */
  window.addEventListener("beforeunload", e => {
    if (!securityArmed || submitting || allowUnload) return;
    e.preventDefault();
    e.returnValue = "";
  });

  /* ===================== FOCUS POLLING (CATCH-ALL) ===================== */
  let focusLostActive = false;
  setInterval(() => {
    if (!securityArmed || submitting) return;

    const hasFocus = document.hasFocus ? document.hasFocus() : true;
    if (!hasFocus && !focusLostActive) {
      focusLostActive = true;
      registerViolation("focus_lost");
      return;
    }
    if (hasFocus && focusLostActive) {
      focusLostActive = false;
    }
  }, 500);

  /* ===================== START FLOW ===================== */
  function beginAttemptUI() {
    if (startScreen) startScreen.style.display = "none";
    if (quizAttemptUI) quizAttemptUI.style.display = "block";

    // Arm security + enter fullscreen
    securityArmed = true;
    enterFS();

    // Restore saved answers and start nav/timer
    loadSavedAnswers();
    show(0);
    startTimer();
  }

  if (startQuizBtn) {
    startQuizBtn.addEventListener("click", () => {
      beginAttemptUI();
    });
  } else {
    // Fallback: if start screen is missing, show UI immediately
    beginAttemptUI();
  }

  const nextBtn = document.getElementById("nextBtn");
  const prevBtn = document.getElementById("prevBtn");
  if (nextBtn) {
    nextBtn.onclick = () => {
      const currentBlock = blocks[current];
      const qIndex = currentBlock ? currentBlock.dataset.qindex : "";
      const checked = qIndex !== "" ? document.querySelector(`input[type=radio][name="answer_${qIndex}"]:checked`) : null;
      if (!checked) {
        if (saveStatus) saveStatus.textContent = "Select an option to continue.";
        return;
      }
      if (current < blocks.length - 1) show(current + 1);
    };
  }
  if (prevBtn) {
    prevBtn.onclick = () => {
      if (current > 0) {
        show(current - 1);
      }
    };
  }

  if (submitBtn) {
    submitBtn.addEventListener("click", () => {
      submitting = true;
      allowUnload = true;
      securityArmed = false;
    });
  }

  quizForm.addEventListener("submit", () => {
    submitting = true;
    allowUnload = true;
    securityArmed = false;
    // Attempt is being submitted; clear local persistence
    localStorage.removeItem(timerKey);
    localStorage.removeItem(answersKey);
    if (timerInterval) clearInterval(timerInterval);
  });

});
