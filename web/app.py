#!/usr/bin/env python3
"""
G1 Security Contract Agent – Web UI
====================================
Flask server:
  POST /upload          – קבלת קובץ הסכם
  POST /run/<job_id>    – הפעלת הניתוח
  GET  /events/<job_id> – Server-Sent Events לסטטוס חי
  GET  /download/<job_id>/<kind> – הורדת XLSX / DOCX / JSON
  GET  /                – דף הבית

שימוש:
  python web/app.py
  → http://127.0.0.1:5000
"""

import os
import re
import sys
import json
import uuid
import queue
import threading
import subprocess
from pathlib import Path
from datetime import datetime

# Force UTF-8 on stdout/stderr so Hebrew + Unicode arrows print on Windows cp1255 consoles
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

from flask import Flask, request, jsonify, send_file, Response, render_template, abort

BASE_DIR   = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
OUTPUTS_DIR = BASE_DIR / "outputs"
UPLOAD_DIR  = BASE_DIR / "outputs" / "_uploads"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXT = {".docx", ".doc", ".pdf", ".txt", ".md"}

app = Flask(
    __name__,
    template_folder=str(Path(__file__).parent / "templates"),
    static_folder=str(Path(__file__).parent / "static"),
)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB

# ─── In-memory job store ──────────────────────────────────────────
JOBS: dict[str, dict] = {}
JOB_LOCK = threading.Lock()


def new_job(uploaded_path: Path, original_name: str) -> str:
    job_id = uuid.uuid4().hex[:12]
    with JOB_LOCK:
        JOBS[job_id] = {
            "id": job_id,
            "status": "ready",          # ready | running | done | error
            "progress": 0,              # 0..100
            "step": "מוכן להרצה",
            "log": [],
            "uploaded_path": str(uploaded_path),
            "original_name": original_name,
            "queue": queue.Queue(),
            "outputs": {},              # kind -> path
            "error": None,
            "started_at": None,
            "finished_at": None,
        }
    return job_id


def push_event(job_id: str, event: dict):
    """Push a status event to the job's SSE queue."""
    with JOB_LOCK:
        job = JOBS.get(job_id)
        if not job:
            return
        if "step" in event:
            job["step"] = event["step"]
        if "progress" in event:
            job["progress"] = event["progress"]
        if "status" in event:
            job["status"] = event["status"]
        if "log" in event:
            job["log"].append(event["log"])
        if "outputs" in event:
            job["outputs"].update(event["outputs"])
        if "error" in event:
            job["error"] = event["error"]
        job["queue"].put(event)


# ─── Progress parser for analyze_contract.py stdout ──────────────
STEP_PATTERNS = [
    (re.compile(r"\[1/4\]"), 15, "מחלץ טקסט מהקובץ..."),
    (re.compile(r"✓ חולצו"), 25, "טקסט חולץ בהצלחה"),
    (re.compile(r"\[2/4\]"), 35, "שולח ל-AI לניתוח משפטי..."),
    (re.compile(r"ממצאים נשמרו"), 60, "ניתוח הושלם, מעבד ממצאים"),
    (re.compile(r"\[3/4\]"), 70, "מייצר דו\"ח Excel..."),
    (re.compile(r"✓ Excel נשמר"), 85, "Excel נשמר"),
    (re.compile(r"\[4/4\]"), 90, "מזריק tracked changes ל-Word..."),
    (re.compile(r"✓ DOCX נשמר|✓ Word נשמר"), 98, "Word נשמר"),
]


def run_analysis(job_id: str):
    """Run analyze_contract.py as subprocess, parse stdout for progress."""
    with JOB_LOCK:
        job = JOBS[job_id]
        job["status"] = "running"
        job["started_at"] = datetime.now().isoformat()
        contract_path = Path(job["uploaded_path"])

    push_event(job_id, {"status": "running", "progress": 5, "step": "מתחיל...",
                        "log": f"קובץ: {contract_path.name}"})

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"

    cmd = [sys.executable, "-u", str(SCRIPTS_DIR / "analyze_contract.py"), str(contract_path)]

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(BASE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
    except Exception as e:
        push_event(job_id, {"status": "error", "error": f"כשל בהפעלה: {e}",
                            "step": "שגיאה", "progress": 0})
        return

    for line in iter(proc.stdout.readline, ""):
        line = line.rstrip()
        if not line:
            continue
        # Match against step patterns
        for pat, prog, step in STEP_PATTERNS:
            if pat.search(line):
                push_event(job_id, {"progress": prog, "step": step, "log": line})
                break
        else:
            push_event(job_id, {"log": line})

    rc = proc.wait()

    if rc != 0:
        push_event(job_id, {"status": "error", "error": f"הסקריפט הסתיים עם קוד {rc}",
                            "step": "שגיאה", "progress": 0})
        return

    # Locate output files (most recent matching pattern)
    contract_stem = contract_path.stem[:30]
    date_str = datetime.now().strftime("%Y%m%d")
    candidates = {
        "xlsx": list(OUTPUTS_DIR.glob(f"{contract_stem}_ניתוח_{date_str}.xlsx")),
        "docx": list(OUTPUTS_DIR.glob(f"{contract_stem}_עקוב_שינויים_{date_str}.docx")),
        "json": list(OUTPUTS_DIR.glob(f"{contract_stem}_findings_{date_str}.json")),
    }
    outputs = {}
    for kind, paths in candidates.items():
        if paths:
            # newest
            paths.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            outputs[kind] = str(paths[0])

    with JOB_LOCK:
        JOBS[job_id]["finished_at"] = datetime.now().isoformat()

    push_event(job_id, {
        "status": "done",
        "progress": 100,
        "step": "הושלם בהצלחה ✓",
        "outputs": outputs,
        "log": "הניתוח הסתיים. ניתן להוריד את הקבצים."
    })


# ─── Routes ──────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "לא נשלח קובץ"}), 400
    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "שם קובץ ריק"}), 400

    ext = Path(f.filename).suffix.lower()
    if ext not in ALLOWED_EXT:
        return jsonify({"error": f"סוג קובץ לא נתמך: {ext}. נתמך: {', '.join(sorted(ALLOWED_EXT))}"}), 400

    # Save with unique prefix to avoid collisions
    safe_name = re.sub(r"[^\w\.\-]", "_", f.filename)
    unique = uuid.uuid4().hex[:8]
    dest = UPLOAD_DIR / f"{unique}_{safe_name}"
    f.save(str(dest))

    job_id = new_job(dest, f.filename)
    return jsonify({"job_id": job_id, "filename": f.filename, "size": dest.stat().st_size})


@app.route("/run/<job_id>", methods=["POST"])
def run(job_id):
    with JOB_LOCK:
        job = JOBS.get(job_id)
    if not job:
        return jsonify({"error": "job not found"}), 404
    if job["status"] == "running":
        return jsonify({"error": "כבר רץ"}), 409

    t = threading.Thread(target=run_analysis, args=(job_id,), daemon=True)
    t.start()
    return jsonify({"ok": True})


@app.route("/events/<job_id>")
def events(job_id):
    with JOB_LOCK:
        job = JOBS.get(job_id)
    if not job:
        abort(404)
    q: queue.Queue = job["queue"]

    def stream():
        # Send current state immediately
        with JOB_LOCK:
            snapshot = {
                "status": job["status"],
                "progress": job["progress"],
                "step": job["step"],
                "outputs": list(job["outputs"].keys()),
            }
        yield f"data: {json.dumps(snapshot, ensure_ascii=False)}\n\n"

        while True:
            try:
                evt = q.get(timeout=30)
            except queue.Empty:
                yield ": keepalive\n\n"
                continue
            payload = {
                "step": evt.get("step"),
                "progress": evt.get("progress"),
                "status": evt.get("status"),
                "log": evt.get("log"),
                "outputs": list(evt.get("outputs", {}).keys()) if evt.get("outputs") else None,
                "error": evt.get("error"),
            }
            payload = {k: v for k, v in payload.items() if v is not None}
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
            if evt.get("status") in ("done", "error"):
                break

    return Response(stream(), mimetype="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
    })


@app.route("/download/<job_id>/<kind>")
def download(job_id, kind):
    with JOB_LOCK:
        job = JOBS.get(job_id)
    if not job:
        abort(404)
    path = job["outputs"].get(kind)
    if not path or not Path(path).exists():
        abort(404)
    return send_file(path, as_attachment=True, download_name=Path(path).name)


@app.route("/status/<job_id>")
def status(job_id):
    with JOB_LOCK:
        job = JOBS.get(job_id)
    if not job:
        return jsonify({"error": "not found"}), 404
    return jsonify({
        "id": job["id"],
        "status": job["status"],
        "progress": job["progress"],
        "step": job["step"],
        "outputs": list(job["outputs"].keys()),
        "error": job["error"],
        "log_tail": job["log"][-20:],
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n  G1 Security Contract Agent - Web UI")
    print(f"  -> http://127.0.0.1:{port}\n")
    app.run(host="127.0.0.1", port=port, debug=False, threaded=True)
