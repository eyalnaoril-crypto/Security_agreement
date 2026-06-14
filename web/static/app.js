(() => {
  const $ = (sel) => document.querySelector(sel);

  const dz = $("#dropzone");
  const fileInput = $("#fileInput");
  const browseBtn = $("#browseBtn");
  const fileInfo = $("#fileInfo");
  const fileName = $("#fileName");
  const fileSize = $("#fileSize");
  const removeBtn = $("#removeFile");
  const runBtn = $("#runBtn");
  const progressCard = $("#progress-card");
  const progressFill = $("#progressFill");
  const progressStep = $("#progressStep");
  const progressPct = $("#progressPct");
  const statusPill = $("#statusPill");
  const logOutput = $("#logOutput");
  const timeline = $("#timeline");
  const resultsCard = $("#results-card");
  const resultsGrid = $("#resultsGrid");
  const errorCard = $("#error-card");
  const errorMsg = $("#errorMsg");

  let currentJobId = null;
  let eventSource = null;

  /* ───── File handling ───── */
  function fmtSize(bytes) {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / 1024 / 1024).toFixed(2) + " MB";
  }

  function showFile(name, size) {
    fileName.textContent = name;
    fileSize.textContent = fmtSize(size);
    fileInfo.classList.remove("hidden");
    dz.classList.add("hidden");
  }

  function resetFile() {
    fileInput.value = "";
    fileInfo.classList.add("hidden");
    dz.classList.remove("hidden");
    runBtn.disabled = true;
    currentJobId = null;
  }

  async function uploadFile(file) {
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await fetch("/upload", { method: "POST", body: form });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "כשל בהעלאה");
      currentJobId = data.job_id;
      showFile(data.filename, data.size);
      runBtn.disabled = false;
    } catch (err) {
      alert("שגיאת העלאה: " + err.message);
    }
  }

  browseBtn.addEventListener("click", () => fileInput.click());
  dz.addEventListener("click", (e) => {
    if (e.target !== browseBtn) fileInput.click();
  });

  fileInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (file) uploadFile(file);
  });

  ["dragenter", "dragover"].forEach((evt) =>
    dz.addEventListener(evt, (e) => {
      e.preventDefault();
      dz.classList.add("drag");
    })
  );
  ["dragleave", "drop"].forEach((evt) =>
    dz.addEventListener(evt, (e) => {
      e.preventDefault();
      dz.classList.remove("drag");
    })
  );
  dz.addEventListener("drop", (e) => {
    const file = e.dataTransfer.files[0];
    if (file) uploadFile(file);
  });

  removeBtn.addEventListener("click", () => {
    if (eventSource) { eventSource.close(); eventSource = null; }
    resetFile();
    progressCard.classList.add("hidden");
    resultsCard.classList.add("hidden");
    errorCard.classList.add("hidden");
  });

  /* ───── Run ───── */
  runBtn.addEventListener("click", async () => {
    if (!currentJobId) return;
    runBtn.disabled = true;
    progressCard.classList.remove("hidden");
    resultsCard.classList.add("hidden");
    errorCard.classList.add("hidden");
    resetTimeline();

    try {
      const res = await fetch(`/run/${currentJobId}`, { method: "POST" });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "כשל בהפעלה");
      openEventStream(currentJobId);
    } catch (err) {
      showError(err.message);
      runBtn.disabled = false;
    }
  });

  /* ───── SSE ───── */
  function openEventStream(jobId) {
    if (eventSource) eventSource.close();
    eventSource = new EventSource(`/events/${jobId}`);
    eventSource.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data);
        applyUpdate(data);
      } catch {}
    };
    eventSource.onerror = () => {
      // ignore; server may have closed normally on done/error
    };
  }

  function applyUpdate(data) {
    if (typeof data.progress === "number") {
      progressFill.style.width = data.progress + "%";
      progressPct.textContent = data.progress + "%";
      updateTimeline(data.progress);
    }
    if (data.step) progressStep.textContent = data.step;
    if (data.log) appendLog(data.log);

    if (data.status === "running") {
      statusPill.textContent = "מעבד...";
      statusPill.className = "status-pill running";
    } else if (data.status === "done") {
      statusPill.textContent = "הושלם ✓";
      statusPill.className = "status-pill done";
      finishAllTimeline();
      showResults();
      if (eventSource) { eventSource.close(); eventSource = null; }
    } else if (data.status === "error") {
      statusPill.textContent = "שגיאה";
      statusPill.className = "status-pill error";
      showError(data.error || "שגיאה לא ידועה");
      if (eventSource) { eventSource.close(); eventSource = null; }
    }
  }

  function appendLog(line) {
    const t = new Date().toLocaleTimeString("he-IL");
    logOutput.textContent += `[${t}] ${line}\n`;
    logOutput.scrollTop = logOutput.scrollHeight;
  }

  /* ───── Timeline ───── */
  const STAGES = [
    { key: "extract", min: 5, max: 30 },
    { key: "ai",      min: 30, max: 65 },
    { key: "excel",   min: 65, max: 88 },
    { key: "word",    min: 88, max: 99 },
  ];

  function resetTimeline() {
    timeline.querySelectorAll(".tl-item").forEach((el) => {
      el.classList.remove("active", "done");
    });
    progressFill.style.width = "0%";
    progressPct.textContent = "0%";
    progressStep.textContent = "מתחיל...";
    logOutput.textContent = "";
  }

  function updateTimeline(pct) {
    STAGES.forEach((s, i) => {
      const el = timeline.querySelector(`[data-stage="${s.key}"]`);
      if (!el) return;
      if (pct >= s.max) {
        el.classList.remove("active");
        el.classList.add("done");
      } else if (pct >= s.min) {
        el.classList.add("active");
        el.classList.remove("done");
      } else {
        el.classList.remove("active", "done");
      }
    });
  }

  function finishAllTimeline() {
    timeline.querySelectorAll(".tl-item").forEach((el) => {
      el.classList.remove("active");
      el.classList.add("done");
    });
  }

  /* ───── Results ───── */
  function showResults() {
    if (!currentJobId) return;
    const items = [
      { kind: "xlsx", icon: "📊", title: "דו\"ח Excel", desc: "סיכום ממצאים ב-3 גיליונות" },
      { kind: "docx", icon: "📝", title: "Word עם שינויים", desc: "הסכם עם Tracked Changes inline" },
      { kind: "json", icon: "🔧", title: "ממצאים גולמיים", desc: "JSON של תוצאת ה-AI" },
    ];
    resultsGrid.innerHTML = items
      .map(
        (it) => `
        <div class="result-card">
          <span class="ico">${it.icon}</span>
          <h4>${it.title}</h4>
          <p>${it.desc}</p>
          <a href="/download/${currentJobId}/${it.kind}">הורד</a>
        </div>`
      )
      .join("");
    resultsCard.classList.remove("hidden");
    resultsCard.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function showError(msg) {
    errorMsg.textContent = msg;
    errorCard.classList.remove("hidden");
    errorCard.scrollIntoView({ behavior: "smooth", block: "start" });
  }
})();
