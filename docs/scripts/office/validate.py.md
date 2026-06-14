---
title: validate.py
type: script
owner: engineering
tags: [office, validation, xsd, ooxml]
source: scripts/office/validate.py
related:
  - "[[pack.py]]"
  - "[[unpack.py]]"
  - "[[inject_tracked.py]]"
---

# validate.py

## מה זה עושה
מאמת קבצי XML של מסמכי Office מול XSD schemas ובדיקות tracked changes. אופציית `--auto-repair` מתקנת:
- `paraId` / `durableId` שחורגים מגבולות OOXML
- `xml:space="preserve"` חסר ב-`w:t` עם רווחים

```bash
python validate.py document.docx --auto-repair
python validate.py unpacked/ --author "G1 Legal AI"
```

## תפקיד בפרויקט
תשתית debugging. **לא חלק מהזרימה הראשית**. שימושי כאשר Word פותח DOCX שייצרנו ב-[[inject_tracked.py]] ומציג שגיאה / מבקש לתקן.

## למי זה שייך
- **Owner**: Engineering (תשתית)
- **מקור**: ארגז כלים סטנדרטי של Anthropic Skills

## קבצים קשורים
- [[pack.py]] – משתמש ב-validate בשלב האריזה
- [[unpack.py]] – משלים
- [[inject_tracked.py]] – אם פלט DOCX שלו נכשל באימות, יש להריץ סקריפט זה לדיבוג
