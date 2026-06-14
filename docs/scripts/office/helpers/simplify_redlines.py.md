---
title: simplify_redlines.py
type: module
owner: engineering
tags: [docx, tracked-changes, redlines, helper]
source: scripts/office/helpers/simplify_redlines.py
related:
  - "[[unpack.py]]"
  - "[[merge_runs.py]]"
  - "[[inject_tracked.py]]"
---

# simplify_redlines.py

## מה זה עושה
מפשט tracked changes על-ידי מיזוג אלמנטי `<w:ins>` או `<w:del>` צמודים. כללים:
- ממזג רק `w:ins` עם `w:ins` ו-`w:del` עם `w:del` (אותו סוג אלמנט)
- ממזג רק אם **אותו author** (מתעלם מהבדלי timestamp)
- ממזג רק אם **באמת צמודים** (רק whitespace ביניהם)

## תפקיד בפרויקט
מודול עזר ל-[[unpack.py]]. שימושי כשמסמך מכיל הרבה redlines קטנים שאפשר לאחד לרצף אחד – משפר קריאות.

## למי זה שייך
- **Owner**: Engineering (תשתית)
- **מקור**: ארגז כלים סטנדרטי של Anthropic Skills

## קבצים קשורים
- [[unpack.py]] – הצרכן הישיר (flag רלוונטי)
- [[merge_runs.py]] – פעולה משלימה ברמת ה-runs (לא tracked changes)
- [[inject_tracked.py]] – פלט שלו עם הרבה ממצאים רצופים יכול להפיק תועלת

## הערות
מודול עזר טהור. כיום [[inject_tracked.py]] לא מפעיל אותו אחרי הזרקה, אבל אפשר להוסיף את זה אם הפלט נראה "רועש".
