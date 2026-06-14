#!/usr/bin/env python3
"""
G1 Legal AI - Desktop Application
==================================
אפליקציית שולחן עבודה לסריקת הסכמי שמירה.

כפתורים:
  📂 בחר קובץ          - פתיחת דיאלוג בחירת קובץ
  ▶ הפעל ניתוח        - מריץ את הפייפליין
  📊 פתח תוצאה        - פותח את ה-Excel / Word שיוצרו

הרצה:  pythonw desktop_app.pyw   (או דאבל-קליק)
"""

import os
import re
import sys
import queue
import threading
import subprocess
from pathlib import Path
from datetime import datetime

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

BASE_DIR    = Path(__file__).resolve().parent
SCRIPTS_DIR = BASE_DIR / "scripts"
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# ─── G1 brand palette ─────────────────────────────────────────────
COLORS = {
    "dark":      "#0F4C2A",
    "mid":       "#1D9E75",
    "light":     "#E1F5EE",
    "bg":        "#F7FAF8",
    "white":     "#FFFFFF",
    "ink":       "#0E1B14",
    "ink_soft":  "#4A5A52",
    "line":      "#E1E7E4",
    "danger":    "#A32D2D",
    "danger_bg": "#FCEBEB",
    "ok_bg":     "#DCF5DC",
    "ok_tx":     "#1E6B1E",
    "warn_bg":   "#FAEEDA",
    "warn_tx":   "#854F0B",
}

ALLOWED_EXT = [
    ("הסכמי Word",  "*.docx;*.doc"),
    ("PDF",         "*.pdf"),
    ("טקסט",        "*.txt;*.md"),
    ("כל הקבצים",   "*.*"),
]

STEP_PATTERNS = [
    (re.compile(r"\[1/4\]"),              15, "מחלץ טקסט..."),
    (re.compile(r"חולצו"),                25, "טקסט חולץ"),
    (re.compile(r"\[2/4\]"),              35, "ניתוח AI..."),
    (re.compile(r"ממצאים נשמרו"),         60, "ממצאים נשמרו"),
    (re.compile(r"\[3/4\]"),              70, "מייצר Excel..."),
    (re.compile(r"Excel נשמר"),           85, "Excel נשמר"),
    (re.compile(r"\[4/4\]"),              90, "מזריק שינויים ל-Word..."),
    (re.compile(r"(DOCX|Word) נשמר"),     98, "Word נשמר"),
    (re.compile(r"הניתוח הושלם"),         100, "הושלם בהצלחה ✓"),
]


class G1App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("G1 Legal AI - ניתוח הסכמי שמירה")
        self.geometry("780x620")
        self.minsize(700, 580)
        self.configure(bg=COLORS["bg"])

        # State
        self.selected_file: Path | None = None
        self.outputs: dict[str, Path] = {}
        self.is_running = False
        self.event_q: queue.Queue = queue.Queue()

        self._setup_styles()
        self._build_ui()
        self._poll_events()

    # ─── Styling ──────────────────────────────────────────────────
    def _setup_styles(self):
        self.option_add("*Font", "Heebo 10")
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background=COLORS["bg"])
        style.configure("Card.TFrame", background=COLORS["white"], relief="flat")
        style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["ink"])
        style.configure("Card.TLabel", background=COLORS["white"], foreground=COLORS["ink"])
        style.configure("CardMuted.TLabel",
                        background=COLORS["white"], foreground=COLORS["ink_soft"],
                        font=("Heebo", 9))
        style.configure("H1.TLabel",
                        background=COLORS["bg"], foreground=COLORS["dark"],
                        font=("Heebo", 18, "bold"))
        style.configure("H2.TLabel",
                        background=COLORS["white"], foreground=COLORS["dark"],
                        font=("Heebo", 12, "bold"))
        style.configure("Status.TLabel",
                        background=COLORS["white"], foreground=COLORS["ink_soft"],
                        font=("Heebo", 10))

        # Progress bar
        style.configure("G1.Horizontal.TProgressbar",
                        troughcolor=COLORS["light"],
                        background=COLORS["mid"],
                        bordercolor=COLORS["light"],
                        lightcolor=COLORS["mid"],
                        darkcolor=COLORS["dark"],
                        thickness=14)

    def _btn(self, parent, text, command, kind="primary", state="normal"):
        """Create a styled button (tk.Button gives more color control than ttk)."""
        if kind == "primary":
            bg, fg, abg = COLORS["dark"], COLORS["white"], COLORS["mid"]
        elif kind == "secondary":
            bg, fg, abg = COLORS["mid"], COLORS["white"], COLORS["dark"]
        else:  # ghost
            bg, fg, abg = COLORS["white"], COLORS["dark"], COLORS["light"]

        b = tk.Button(
            parent, text=text, command=command,
            bg=bg, fg=fg, activebackground=abg, activeforeground=COLORS["white"],
            relief="flat", borderwidth=0,
            font=("Heebo", 11, "bold"),
            padx=22, pady=10, cursor="hand2",
            state=state,
        )
        if kind == "ghost":
            b.configure(
                activeforeground=COLORS["dark"],
                highlightbackground=COLORS["mid"],
                highlightthickness=1,
            )
        # Disabled state styling
        b.configure(disabledforeground="#A0AEA7")
        return b

    # ─── UI ───────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=COLORS["bg"])
        header.pack(fill="x", padx=24, pady=(20, 14))

        logo = tk.Label(header, text="G1", bg=COLORS["dark"], fg=COLORS["white"],
                        font=("Heebo", 14, "bold"), width=3, height=1)
        logo.pack(side="right", padx=(12, 0))

        title_box = tk.Frame(header, bg=COLORS["bg"])
        title_box.pack(side="right")
        tk.Label(title_box, text="G1 Legal AI", bg=COLORS["bg"],
                 fg=COLORS["dark"], font=("Heebo", 16, "bold")).pack(anchor="e")
        tk.Label(title_box, text="ניתוח הסכמי שמירה ואבטחה",
                 bg=COLORS["bg"], fg=COLORS["ink_soft"],
                 font=("Heebo", 9)).pack(anchor="e")

        # Card container
        body = tk.Frame(self, bg=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        # ── Card 1: file selection ────
        card1 = self._card(body)
        card1.pack(fill="x", pady=(0, 12))
        self._step_header(card1, "1", "בחירת קובץ הסכם")

        self.file_label = tk.Label(
            card1, text="לא נבחר קובץ",
            bg=COLORS["light"], fg=COLORS["ink_soft"],
            font=("Heebo", 10), anchor="e",
            padx=14, pady=12, relief="flat",
        )
        self.file_label.pack(fill="x", padx=14, pady=(0, 12))

        btns_row1 = tk.Frame(card1, bg=COLORS["white"])
        btns_row1.pack(anchor="e", padx=14, pady=(0, 14))

        self.btn_browse = self._btn(btns_row1, "📂  בחר קובץ", self.on_browse, kind="ghost")
        self.btn_browse.pack(side="right")

        self.btn_clear = self._btn(btns_row1, "✕  נקה", self.on_clear, kind="ghost", state="disabled")
        self.btn_clear.pack(side="right", padx=(0, 8))

        # ── Card 2: run ────
        card2 = self._card(body)
        card2.pack(fill="x", pady=(0, 12))
        self._step_header(card2, "2", "הפעלת ניתוח")

        run_box = tk.Frame(card2, bg=COLORS["white"])
        run_box.pack(fill="x", padx=14, pady=(0, 14))

        self.btn_run = self._btn(run_box, "▶  הפעל ניתוח", self.on_run, state="disabled")
        self.btn_run.pack(side="right")

        ttk.Label(run_box,
                  text="הניתוח יזהה סטיות מההסכם הגנרי של G1 ויפיק דו\"ח Excel ו-Word עם Tracked Changes.",
                  style="CardMuted.TLabel", wraplength=460, justify="right",
                  ).pack(side="right", padx=(0, 16), fill="x", expand=True)

        # ── Card 3: progress ────
        card3 = self._card(body)
        card3.pack(fill="both", expand=True, pady=(0, 12))
        self._step_header(card3, "3", "התקדמות", with_status=True)

        # progress bar
        prog_box = tk.Frame(card3, bg=COLORS["white"])
        prog_box.pack(fill="x", padx=14, pady=(0, 6))
        self.progress = ttk.Progressbar(
            prog_box, style="G1.Horizontal.TProgressbar",
            mode="determinate", length=400, maximum=100, value=0,
        )
        self.progress.pack(fill="x")

        meta_box = tk.Frame(card3, bg=COLORS["white"])
        meta_box.pack(fill="x", padx=14, pady=(4, 10))
        self.step_label = ttk.Label(meta_box, text="מוכן", style="Status.TLabel")
        self.step_label.pack(side="right")
        self.pct_label = ttk.Label(meta_box, text="0%",
                                   style="Status.TLabel",
                                   font=("Heebo", 10, "bold"),
                                   foreground=COLORS["dark"])
        self.pct_label.pack(side="left")

        # log
        log_frame = tk.Frame(card3, bg=COLORS["white"])
        log_frame.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        ttk.Label(log_frame, text="יומן:", style="CardMuted.TLabel").pack(anchor="e")

        log_inner = tk.Frame(log_frame, bg=COLORS["white"])
        log_inner.pack(fill="both", expand=True, pady=(4, 0))

        scrollbar = tk.Scrollbar(log_inner)
        scrollbar.pack(side="left", fill="y")

        self.log_text = tk.Text(
            log_inner, height=8,
            bg="#FAFCFB", fg=COLORS["ink"],
            font=("Consolas", 9), wrap="word",
            relief="flat", borderwidth=1,
            highlightthickness=1, highlightbackground=COLORS["line"],
            yscrollcommand=scrollbar.set, state="disabled",
        )
        self.log_text.pack(side="right", fill="both", expand=True)
        scrollbar.config(command=self.log_text.yview)

        # ── Card 4: results ────
        card4 = self._card(body)
        card4.pack(fill="x")
        self._step_header(card4, "✓", "תוצאות", color_override=COLORS["mid"])

        self.results_box = tk.Frame(card4, bg=COLORS["white"])
        self.results_box.pack(fill="x", padx=14, pady=(0, 14))

        self.btn_open_excel = self._btn(self.results_box, "📊  פתח דו\"ח Excel",
                                        lambda: self.open_output("xlsx"),
                                        kind="primary", state="disabled")
        self.btn_open_excel.pack(side="right", padx=(0, 8))

        self.btn_open_docx = self._btn(self.results_box, "📝  פתח Word",
                                       lambda: self.open_output("docx"),
                                       kind="secondary", state="disabled")
        self.btn_open_docx.pack(side="right", padx=(0, 8))

        self.btn_open_folder = self._btn(self.results_box, "📁  פתח תיקיית פלטים",
                                         self.open_outputs_folder,
                                         kind="ghost", state="disabled")
        self.btn_open_folder.pack(side="right")

        # Footer
        tk.Label(self, text="G1 Group · Legal AI · נתונים נשארים מקומית במחשב",
                 bg=COLORS["bg"], fg=COLORS["ink_soft"],
                 font=("Heebo", 8)).pack(side="bottom", pady=(0, 10))

    def _card(self, parent):
        outer = tk.Frame(parent, bg=COLORS["line"])
        inner = tk.Frame(outer, bg=COLORS["white"])
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        return inner

    def _step_header(self, parent, num, title, with_status=False, color_override=None):
        hdr = tk.Frame(parent, bg=COLORS["white"])
        hdr.pack(fill="x", padx=14, pady=(14, 10))

        bg_color = color_override if color_override else COLORS["dark"]
        badge = tk.Label(hdr, text=str(num),
                         bg=COLORS["light"] if not color_override else color_override,
                         fg=bg_color if not color_override else COLORS["white"],
                         font=("Heebo", 11, "bold"),
                         width=2, height=1)
        badge.pack(side="right", padx=(0, 10))

        tk.Label(hdr, text=title, bg=COLORS["white"], fg=COLORS["dark"],
                 font=("Heebo", 12, "bold")).pack(side="right")

        if with_status:
            self.status_pill = tk.Label(hdr, text="ממתין",
                                        bg=COLORS["light"], fg=COLORS["dark"],
                                        font=("Heebo", 9, "bold"),
                                        padx=10, pady=2)
            self.status_pill.pack(side="left")

    # ─── Event handlers ───────────────────────────────────────────
    def on_browse(self):
        if self.is_running:
            return
        path = filedialog.askopenfilename(
            title="בחר הסכם לניתוח",
            filetypes=ALLOWED_EXT,
            initialdir=str(Path.home() / "Downloads") if (Path.home() / "Downloads").exists() else str(Path.home()),
        )
        if not path:
            return
        p = Path(path)
        if not p.exists():
            messagebox.showerror("שגיאה", "הקובץ לא נמצא")
            return
        self.selected_file = p
        size_kb = p.stat().st_size / 1024
        size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.2f} MB"
        self.file_label.config(
            text=f"  📄  {p.name}    •    {size_str}",
            fg=COLORS["dark"], bg=COLORS["light"],
        )
        self.btn_clear.config(state="normal")
        self.btn_run.config(state="normal")

    def on_clear(self):
        if self.is_running:
            return
        self.selected_file = None
        self.file_label.config(text="לא נבחר קובץ", fg=COLORS["ink_soft"])
        self.btn_clear.config(state="disabled")
        self.btn_run.config(state="disabled")
        self._reset_progress()

    def on_run(self):
        if self.is_running or not self.selected_file:
            return
        self.is_running = True
        self.outputs = {}
        self._set_buttons_during_run(True)
        self._reset_progress()
        self._set_status("מעבד...", "warn")
        self._log(f"מתחיל ניתוח: {self.selected_file.name}")
        t = threading.Thread(target=self._run_subprocess, daemon=True)
        t.start()

    def _run_subprocess(self):
        contract = self.selected_file
        date_str = datetime.now().strftime("%Y%m%d")
        stem = contract.stem[:30]

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUNBUFFERED"] = "1"

        cmd = [sys.executable, "-u", str(SCRIPTS_DIR / "analyze_contract.py"), str(contract)]

        try:
            proc = subprocess.Popen(
                cmd,
                cwd=str(BASE_DIR),
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace",
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
        except Exception as e:
            self.event_q.put(("error", f"כשל בהפעלת התהליך: {e}"))
            return

        for line in iter(proc.stdout.readline, ""):
            line = line.rstrip()
            if not line:
                continue
            matched = False
            for pat, prog, step in STEP_PATTERNS:
                if pat.search(line):
                    self.event_q.put(("progress", prog, step, line))
                    matched = True
                    break
            if not matched:
                self.event_q.put(("log", line))

        rc = proc.wait()

        if rc != 0:
            self.event_q.put(("error", f"התהליך הסתיים עם קוד שגיאה {rc}"))
            return

        # Resolve outputs
        candidates = {
            "xlsx": list(OUTPUTS_DIR.glob(f"{stem}_ניתוח_{date_str}.xlsx")),
            "docx": list(OUTPUTS_DIR.glob(f"{stem}_עקוב_שינויים_{date_str}.docx")),
        }
        found = {}
        for kind, paths in candidates.items():
            if paths:
                paths.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                found[kind] = paths[0]
        self.event_q.put(("done", found))

    def _poll_events(self):
        """Drain the event queue from the worker thread back to the UI thread."""
        try:
            while True:
                evt = self.event_q.get_nowait()
                kind = evt[0]
                if kind == "progress":
                    _, pct, step, line = evt
                    self.progress["value"] = pct
                    self.pct_label.config(text=f"{pct}%")
                    self.step_label.config(text=step)
                    self._log(line)
                elif kind == "log":
                    self._log(evt[1])
                elif kind == "done":
                    self.outputs = evt[1]
                    self.progress["value"] = 100
                    self.pct_label.config(text="100%")
                    self.step_label.config(text="הושלם בהצלחה ✓")
                    self._set_status("הושלם", "ok")
                    self._log("הניתוח הסתיים. ניתן לפתוח את הקבצים.")
                    self.is_running = False
                    self._set_buttons_during_run(False)
                    self._enable_result_buttons()
                elif kind == "error":
                    self._set_status("שגיאה", "err")
                    self._log(f"שגיאה: {evt[1]}")
                    self.is_running = False
                    self._set_buttons_during_run(False)
                    messagebox.showerror("שגיאה בניתוח", evt[1])
        except queue.Empty:
            pass
        self.after(80, self._poll_events)

    # ─── UI helpers ───────────────────────────────────────────────
    def _reset_progress(self):
        self.progress["value"] = 0
        self.pct_label.config(text="0%")
        self.step_label.config(text="מוכן")
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")
        self.btn_open_excel.config(state="disabled")
        self.btn_open_docx.config(state="disabled")
        self.btn_open_folder.config(state="disabled")
        self._set_status("ממתין", "neutral")

    def _set_status(self, text, kind):
        palette = {
            "neutral": (COLORS["light"], COLORS["dark"]),
            "warn":    (COLORS["warn_bg"], COLORS["warn_tx"]),
            "ok":      (COLORS["ok_bg"], COLORS["ok_tx"]),
            "err":     (COLORS["danger_bg"], COLORS["danger"]),
        }
        bg, fg = palette.get(kind, palette["neutral"])
        self.status_pill.config(text=text, bg=bg, fg=fg)

    def _set_buttons_during_run(self, running: bool):
        state = "disabled" if running else "normal"
        self.btn_browse.config(state=state)
        self.btn_clear.config(state="disabled" if running else ("normal" if self.selected_file else "disabled"))
        self.btn_run.config(state="disabled" if running else ("normal" if self.selected_file else "disabled"))

    def _enable_result_buttons(self):
        if "xlsx" in self.outputs:
            self.btn_open_excel.config(state="normal")
        if "docx" in self.outputs:
            self.btn_open_docx.config(state="normal")
        if self.outputs:
            self.btn_open_folder.config(state="normal")

    def _log(self, line: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"[{ts}] {line}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    # ─── Open result files ────────────────────────────────────────
    def open_output(self, kind: str):
        path = self.outputs.get(kind)
        if not path or not path.exists():
            messagebox.showwarning("קובץ לא נמצא", "הקובץ לא קיים יותר.")
            return
        self._open_path(path)

    def open_outputs_folder(self):
        self._open_path(OUTPUTS_DIR)

    @staticmethod
    def _open_path(p: Path):
        try:
            if os.name == "nt":
                os.startfile(str(p))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(p)], check=False)
            else:
                subprocess.run(["xdg-open", str(p)], check=False)
        except Exception as e:
            messagebox.showerror("שגיאה", f"לא ניתן לפתוח: {e}")


def main():
    app = G1App()
    app.mainloop()


if __name__ == "__main__":
    main()
