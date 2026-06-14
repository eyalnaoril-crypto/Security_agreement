---
title: INDEX
type: instructions
owner: shared
tags: [index, vault, overview]
source: docs/
---

# 📚 G1 Security Contract Agent – Obsidian Vault

vault תיעוד אוטומטי של פרויקט [G1 Security Contract Agent](https://github.com/eyalnaoril-crypto/Security_agreement) – סוכן AI לניתוח הסכמי שמירה ואבטחה שמגיעים ממזמיני שירות והשוואתם להסכם הגנרי של G1.

## 🔄 זרימת עבודה

```
קלט: DOCX/PDF/TXT (הסכם לקוח)
    ↓
[[analyze_contract.py]] – מתאם הכול
    ↓
חילוץ טקסט (mammoth / pdftotext)
    ↓
ניתוח AI עם [[system_prompt.md]] + השוואה ל-[[generic_contract.md]]
    ↓
findings.json
    ↓
   ├─→ [[export_excel.py]] → XLSX (3 גיליונות: סיכום, ממצאים, עדיפויות)
   └─→ [[inject_tracked.py]] → DOCX עם tracked changes + comments inline
```

## 📂 קבצים לפי בעלות

### 🟢 Legal (משפטי)
- [[system_prompt.md]] – הנחיות ה-AI לניתוח חוזה
- [[generic_contract.md]] – ההסכם הגנרי של G1 לבסיס ההשוואה

### ⚙️ Engineering (סקריפטים)
- [[analyze_contract.py]] – נקודת הכניסה הראשית
- [[export_excel.py]] – ייצור דו"ח Excel
- [[inject_tracked.py]] – הזרקת tracked changes ל-DOCX
- [[generate_tracked_docx.py]] – גרסה ישנה (לא בשימוש ראשי)

### 🔧 Office Toolkit (תשתית DOCX)
- [[pack.py]] – אריזה חזרה של DOCX מפורק
- [[unpack.py]] – פירוק DOCX לעריכה
- [[validate.py]] – אימות סכמת OOXML
- [[soffice.py]] – הרצת LibreOffice בסביבות מוגבלות
- [[merge_runs.py]] – מיזוג runs צמודים ב-DOCX
- [[simplify_redlines.py]] – פישוט tracked changes

### 🌐 Web UI (ממשק דפדפן)
- [[web/app.py]] – שרת Flask + SSE
- [[web/templates/index.html]] – דף הבית
- [[web/static/style.css]] – עיצוב G1 RTL
- [[web/static/app.js]] – לוגיקת frontend
- הפעלה: `python web/app.py` או `run_web.bat`

### 📦 Shared (תשתית פרויקט)
- [[CLAUDE.md]] – הנחיות הסוכן לפרויקט הזה
- [[requirements.txt]] – תלויות Python
- [[.gitignore]] – חוקי git

## 🗺️ איך לפתוח ב-Obsidian
1. Obsidian → **Open folder as vault**
2. בחר את שורש הפרויקט (`security-contract-agent/`)
3. נווט ל-`docs/INDEX.md`
4. לחץ `Ctrl+G` לתצוגת גרף

## 🔗 קישורים חיצוניים
- [GitHub Repository](https://github.com/eyalnaoril-crypto/Security_agreement)
- מאחורי הפרויקט: **G1 Group** – ספק שירותי שמירה ואבטחה
