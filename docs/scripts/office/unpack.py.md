---
title: unpack.py
type: script
owner: engineering
tags: [office, docx, pptx, xlsx, unpacking, ooxml]
source: scripts/office/unpack.py
related:
  - "[[pack.py]]"
  - "[[merge_runs.py]]"
  - "[[simplify_redlines.py]]"
  - "[[inject_tracked.py]]"
---

# unpack.py

## מה זה עושה
פירוק קובץ Office (DOCX / PPTX / XLSX) לתיקייה כדי לאפשר עריכה ידנית. מחלץ את ה-ZIP, מבצע pretty-print ל-XMLs, ואופציונלית:
- ממזג runs צמודים עם עיצוב זהה ([[merge_runs.py]])
- מפשט tracked changes צמודים מאותו author ([[simplify_redlines.py]])

```bash
python unpack.py document.docx unpacked/
python unpack.py document.docx unpacked/ --merge-runs false
```

## תפקיד בפרויקט
תשתית לעבודה ידנית עם DOCX. **לא נקרא ישירות** מהזרימה הראשית. שימושי לדיבוג של [[inject_tracked.py]] – אם הזרקה לא עובדת, פותחים את ה-DOCX עם הסקריפט הזה ובוחנים את ה-XML.

## למי זה שייך
- **Owner**: Engineering (תשתית)
- **מקור**: ארגז כלים סטנדרטי של Anthropic Skills

## קבצים קשורים
- [[pack.py]] – פעולה הפוכה
- [[merge_runs.py]] – אופציה למיזוג runs
- [[simplify_redlines.py]] – אופציה לפישוט tracked changes
- [[inject_tracked.py]] – משלים, מבצע unpack ידני באמצעות `zipfile`
