---
title: pack.py
type: script
owner: engineering
tags: [office, docx, pptx, xlsx, packaging, ooxml]
source: scripts/office/pack.py
related:
  - "[[unpack.py]]"
  - "[[validate.py]]"
  - "[[soffice.py]]"
  - "[[inject_tracked.py]]"
---

# pack.py

## מה זה עושה
ארוז תיקייה מפורקת חזרה לקובץ Office סגור (DOCX / PPTX / XLSX). מבצע אימות עם תיקון אוטומטי, מקצר עיצוב XML, ומייצר את הקובץ הסופי.

```bash
python pack.py unpacked/ output.docx --original input.docx
python pack.py unpacked/ output.pptx --validate false
```

## תפקיד בפרויקט
חלק מארגז כלים גנרי לעבודה עם פורמטי Office. **לא נקרא ישירות** מהזרימה הראשית של הסוכן ([[inject_tracked.py]] משתמש ב-zipfile של פייתון), אבל זמין כתשתית לתסריטים מתקדמים יותר.

## למי זה שייך
- **Owner**: Engineering (תשתית)
- **מקור**: ארגז כלים סטנדרטי של Anthropic Skills (`docx` skill)

## קבצים קשורים
- [[unpack.py]] – פעולה הפוכה
- [[validate.py]] – נקרא אוטומטית כחלק מהאריזה
- [[soffice.py]] – הרצת LibreOffice
- [[inject_tracked.py]] – משלים: עושה אותה פעולה ידנית
