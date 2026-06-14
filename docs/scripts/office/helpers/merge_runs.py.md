---
title: merge_runs.py
type: module
owner: engineering
tags: [docx, xml-cleanup, runs, helper]
source: scripts/office/helpers/merge_runs.py
related:
  - "[[unpack.py]]"
  - "[[simplify_redlines.py]]"
  - "[[inject_tracked.py]]"
---

# merge_runs.py

## מה זה עושה
ממזג אלמנטי `<w:r>` (runs) צמודים עם **תכונות עיצוב זהות** (`<w:rPr>`) ב-DOCX. עובד גם על runs בפסקאות וגם בתוך tracked changes (`<w:ins>`, `<w:del>`). בנוסף:
- מסיר תכונות `rsid` (metadata של revision שלא משפיע על תצוגה)
- מסיר אלמנטי `proofErr` (סימוני שגיאות איות/דקדוק שחוסמים מיזוג)

## תפקיד בפרויקט
מודול עזר ל-[[unpack.py]] – מנקה DOCX מ"רעש" XML שנובע מ-Word כשמשתמש מקליד תווים בודדים. שימושי לפני שעוברים על ה-XML ידנית.

## למי זה שייך
- **Owner**: Engineering (תשתית)
- **מקור**: ארגז כלים סטנדרטי של Anthropic Skills

## קבצים קשורים
- [[unpack.py]] – הצרכן הישיר (flag `--merge-runs`)
- [[simplify_redlines.py]] – פעולה משלימה ברמת ה-tracked changes
- [[inject_tracked.py]] – ה-DOCX שהוא מייצר יכול להפיק תועלת מהמיזוג

## הערות
מודול עזר טהור – אין לו `__main__`. נקרא רק כספרייה.
