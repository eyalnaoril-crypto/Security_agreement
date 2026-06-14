---
title: requirements.txt
type: dependencies
owner: engineering
tags: [python, dependencies]
source: requirements.txt
related:
  - "[[analyze_contract.py]]"
  - "[[inject_tracked.py]]"
  - "[[export_excel.py]]"
---

# requirements.txt

## מה זה עושה
רשימת חבילות Python שהפרויקט תלוי בהן.

## תפקיד בפרויקט
מותקן באמצעות:
```bash
pip install -r requirements.txt --break-system-packages
```

חבילות מרכזיות:
- **lxml** – פירוס XML של DOCX ([[inject_tracked.py]])
- **openpyxl** – יצירת קבצי Excel ([[export_excel.py]])
- **mammoth** – חילוץ טקסט מ-DOCX ([[analyze_contract.py]])
- **python-docx** – עזר נוסף ל-DOCX
- **anthropic** (אופציונלי) – SDK רשמי, fallback ל-urllib

## למי זה שייך
- **Owner**: Engineering
- **משתמשים**: כל מי שמתקין את הפרויקט

## קבצים קשורים
- [[analyze_contract.py]] – משתמש ב-mammoth ו-anthropic
- [[inject_tracked.py]] – משתמש ב-lxml
- [[export_excel.py]] – משתמש ב-openpyxl
