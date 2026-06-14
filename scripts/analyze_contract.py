#!/usr/bin/env python3
"""
סוכן ניתוח הסכמי שמירה ואבטחה – G1 Security
=============================================
שימוש:
    python3 analyze_contract.py <path_to_contract>

דוגמה:
    python3 analyze_contract.py ~/Downloads/הסכם_לקוח.docx

פלטים (ב-outputs/):
    [שם]_ניתוח_[תאריך].xlsx
    [שם]_עקוב_שינויים_[תאריך].docx   (רק אם הוגש DOCX)
"""

import sys, os, json, subprocess, tempfile, re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent  # project root (script lives in scripts/)
DATA_DIR  = BASE_DIR / "data"
OUT_DIR   = BASE_DIR / "outputs"
SCRIPTS   = BASE_DIR / "scripts"
OUT_DIR.mkdir(exist_ok=True)

# ─────────────────────────────────────────────
# 1. חילוץ טקסט מהקובץ
# ─────────────────────────────────────────────
def extract_text(file_path: Path) -> str:
    ext = file_path.suffix.lower()
    print(f"[1/4] מחלץ טקסט מ-{file_path.name}...")

    if ext in (".docx", ".doc"):
        try:
            import mammoth
            with open(file_path, "rb") as f:
                result = mammoth.extract_raw_text(f)
            return result.value
        except ImportError:
            pass
        # fallback: extract-text CLI
        result = subprocess.run(
            ["extract-text", str(file_path)],
            capture_output=True, text=True
        )
        return result.stdout

    elif ext == ".pdf":
        result = subprocess.run(
            ["pdftotext", str(file_path), "-"],
            capture_output=True, text=True
        )
        return result.stdout

    elif ext in (".txt", ".md"):
        return file_path.read_text(encoding="utf-8", errors="replace")

    else:
        raise ValueError(f"סוג קובץ לא נתמך: {ext}. נתמך: .docx .pdf .txt")


# ─────────────────────────────────────────────
# 2. ניתוח AI
# ─────────────────────────────────────────────
def analyze_with_ai(contract_text: str) -> dict:
    print("[2/4] מנתח עם AI...")

    # Load system prompt
    system_prompt = (DATA_DIR / "system_prompt.md").read_text(encoding="utf-8")

    # Truncate to 8000 chars for context limit
    user_content = f"להלן ההסכם לסריקה:\n\n{contract_text[:8000]}"

    try:
        import anthropic
        client = anthropic.Anthropic()
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}]
        )
        raw = message.content[0].text
    except ImportError:
        # fallback: use requests
        import urllib.request
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise EnvironmentError("ANTHROPIC_API_KEY לא מוגדר")

        payload = json.dumps({
            "model": "claude-sonnet-4-6",
            "max_tokens": 4000,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_content}]
        }).encode()

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            }
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
        raw = data["content"][0]["text"]

    # Parse JSON
    clean = raw.strip()
    # Strip markdown fences if present
    clean = re.sub(r"^```json\s*", "", clean)
    clean = re.sub(r"\s*```$", "", clean)
    clean = clean.strip()

    try:
        return json.loads(clean)
    except json.JSONDecodeError as e:
        print(f"[!] שגיאה בפענוח JSON: {e}")
        print(f"    תגובה גולמית: {raw[:300]}")
        raise


# ─────────────────────────────────────────────
# 3. ייצוא Excel
# ─────────────────────────────────────────────
def export_excel(findings_data: dict, output_path: Path, contract_name: str):
    print("[3/4] מייצא Excel...")

    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "export_excel.py"),
         json.dumps(findings_data),
         str(output_path),
         contract_name],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if result.returncode != 0:
        print(f"[!] שגיאת Excel: {result.stderr}")
    else:
        print(f"    ✓ Excel נשמר: {output_path}")


# ─────────────────────────────────────────────
# 4. Word עם tracked changes
# ─────────────────────────────────────────────
def export_word_tracked(contract_path: Path, findings_data: dict, output_path: Path):
    print("[4/4] מייצר Word עם עקוב אחר שינויים...")

    # Write findings to temp JSON
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                     delete=False, encoding="utf-8") as tmp:
        json.dump(findings_data, tmp, ensure_ascii=False)
        tmp_path = tmp.name

    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "inject_tracked.py"),
         str(contract_path), tmp_path, str(output_path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    os.unlink(tmp_path)

    if result.returncode != 0:
        print(f"[!] שגיאת Word: {result.stderr}")
    else:
        print(f"    ✓ Word נשמר: {output_path}")


# ─────────────────────────────────────────────
# ריכוז ממצאים לסיכום
# ─────────────────────────────────────────────
def print_summary(data: dict):
    findings = data.get("findings", [])
    crit  = [f for f in findings if f.get("severity") == "critical"]
    warn  = [f for f in findings if f.get("severity") == "warning"]
    ok    = [f for f in findings if f.get("severity") == "ok"]

    risk_label = {"low": "נמוך 🟢", "medium": "בינוני 🟡", "high": "גבוה 🔴"}
    print("\n" + "═"*60)
    print("📋 סיכום ניתוח הסכם – G1 Security")
    print("═"*60)
    print(f"  {data.get('summary','')}")
    print(f"  סיכון כולל: {risk_label.get(data.get('overall_risk',''), '')}")
    print(f"\n  🔴 ממצאים קריטיים : {len(crit)}")
    for f in crit:
        print(f"     • {f.get('title','')} ({f.get('clause_ref','')})")
    print(f"\n  🟡 אזהרות          : {len(warn)}")
    for f in warn:
        print(f"     • {f.get('title','')} ({f.get('clause_ref','')})")
    print(f"\n  🟢 תקין            : {len(ok)}")

    insurance = data.get("insurance_note", "")
    if insurance and insurance != "לא":
        print(f"\n  🔒 ביטוחים: {insurance[:100]}")

    missing = data.get("missing_appendices", "")
    if missing and missing != "אין":
        print(f"\n  📎 נספחים חסרים: {missing[:100]}")
    print("═"*60)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        print("שימוש: python3 analyze_contract.py <path_to_contract>")
        print("דוגמה: python3 analyze_contract.py ~/הסכם_לקוח.docx")
        sys.exit(1)

    contract_path = Path(sys.argv[1]).expanduser().resolve()
    if not contract_path.exists():
        print(f"[!] קובץ לא נמצא: {contract_path}")
        sys.exit(1)

    # Derive output name
    date_str      = datetime.now().strftime("%Y%m%d")
    contract_stem = contract_path.stem[:30]
    out_xlsx      = OUT_DIR / f"{contract_stem}_ניתוח_{date_str}.xlsx"
    out_docx      = OUT_DIR / f"{contract_stem}_עקוב_שינויים_{date_str}.docx"
    findings_json = OUT_DIR / f"{contract_stem}_findings_{date_str}.json"

    # Step 1: extract text
    text = extract_text(contract_path)
    if not text.strip():
        print("[!] לא הצלחתי לחלץ טקסט מהקובץ")
        sys.exit(1)
    print(f"    ✓ חולצו {len(text):,} תווים")

    # Step 2: AI analysis
    data = analyze_with_ai(text)

    # Save findings JSON
    findings_json.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"    ✓ ממצאים נשמרו: {findings_json}")

    # Print summary
    print_summary(data)

    # Step 3: Excel
    export_excel(data, out_xlsx, contract_stem)

    # Step 4: Word with tracked changes (DOCX only)
    if contract_path.suffix.lower() in (".docx", ".doc"):
        export_word_tracked(contract_path, data, out_docx)
    else:
        print("[4/4] Word עם שינויים – זמין רק לקבצי DOCX (דולג)")

    print(f"\n✅ הניתוח הושלם. קבצים ב: {OUT_DIR}")


if __name__ == "__main__":
    main()
