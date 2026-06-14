---
title: soffice.py
type: module
owner: engineering
tags: [libreoffice, sandbox, subprocess, infrastructure]
source: scripts/office/soffice.py
related:
  - "[[pack.py]]"
  - "[[validate.py]]"
---

# soffice.py

## מה זה עושה
מודול עזר להרצת **LibreOffice (soffice)** בסביבות שבהן AF_UNIX sockets חסומים (לדוגמה: VMs sandboxed). מזהה את ההגבלה בזמן ריצה ומחיל LD_PRELOAD shim אם צריך.

```python
from office.soffice import run_soffice, get_soffice_env

# אופציה 1 – הרצת soffice ישירות
run_soffice(["--headless", "--convert-to", "pdf", "input.docx"])

# אופציה 2 – קבלת env dict ל-subprocess שלך
env = get_soffice_env()
subprocess.run(["soffice", ...], env=env)
```

## תפקיד בפרויקט
תשתית להמרת DOCX ל-PDF או פתיחה ב-headless mode. **לא בשימוש בזרימה הראשית** של הסוכן (Windows + Word), אבל חיוני אם נדרש להריץ ב-Linux container.

## למי זה שייך
- **Owner**: Engineering (תשתית)
- **מקור**: ארגז כלים סטנדרטי של Anthropic Skills

## קבצים קשורים
- [[pack.py]] – יכול להשתמש בהמרה ל-PDF לאימות חזותי
- [[validate.py]] – משלים – אחד טכני (XML), אחד חזותי (LibreOffice render)

## הערות
רלוונטי בעיקר ל-CI/CD או שרת Linux. בסביבת Windows המקומית של G1, soffice אופציונלי.
