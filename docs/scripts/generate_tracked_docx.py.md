---
title: generate_tracked_docx.py
type: script
owner: engineering
tags: [docx, deprecated, tracked-changes, legacy]
source: scripts/generate_tracked_docx.py
related:
  - "[[inject_tracked.py]]"
  - "[[analyze_contract.py]]"
---

# generate_tracked_docx.py

## מה זה עושה
**גרסה ישנה** של מנגנון יצירת DOCX עם tracked changes. ירש לטובת [[inject_tracked.py]] שמזריק שינויים inline במקום להוסיף אותם בסוף.

## תפקיד בפרויקט
- לא חלק מהזרימה הראשית כיום
- נשמר כ-fallback / רפרנס היסטורי
- מסומן ב-[[CLAUDE.md]] כ"גרסה ישנה – לא בשימוש ראשי"

## למי זה שייך
- **Owner**: Engineering (legacy)
- **סטטוס**: deprecated – אל תקרא לזה מקוד חדש

## קבצים קשורים
- [[inject_tracked.py]] – החליף אותו
- [[analyze_contract.py]] – לא קורא לו (קורא ל-inject_tracked)

## הערות
מומלץ למחוק את הקובץ ברגע שיש ביטחון מלא ש-[[inject_tracked.py]] מכסה את כל המקרים. כרגע נשמר ליתר ביטחון.
