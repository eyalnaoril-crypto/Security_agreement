---
title: web/static/style.css
type: data
owner: engineering
tags: [web, css, design, rtl, theme]
source: web/static/style.css
related:
  - "[[index.html]]"
  - "[[app.js]]"
---

# web/static/style.css

## מה זה עושה
גיליון סגנונות לממשק. מגדיר את שפת העיצוב של G1: ירוק כהה (`#0F4C2A`) + ירוק חי (`#1D9E75`), רקע gradient עדין, כרטיסים עם shadow רך, פינות מעוגלות.

## רכיבים עיקריים
- **Topbar** – לוגו G1 + כותרת + pills מטא-מידע
- **Hero** – כותרת ראשית והסבר
- **Cards** – המבנה הבסיסי לכל סקציה (העלאה, הפעלה, התקדמות, תוצאות)
- **Dropzone** – אזור גרירת קובץ עם הובר
- **Progress bar** – פס התקדמות עם shimmer animation
- **Timeline** – 4 שלבים עם נקודות שמתמלאות
- **Result cards** – grid של כפתורי הורדה

## תפקיד בפרויקט
המראה והתחושה. הצבעים סנכרנו עם פלטת [[export_excel.py]] כדי שהממשק וקובץ ה-Excel ייראו "כאילו מאותה משפחה".

## למי זה שייך
- **Owner**: Engineering / Design
- **טוען על-ידי**: [[index.html]]

## קבצים קשורים
- [[index.html]] – המסמך שמשתמש בסגנונות
- [[app.js]] – מוסיף/מסיר classes (`active`, `done`, `running`, `error`)

## הערות
- responsive: עד 640px → timeline ל-2 עמודות
- משתמש ב-CSS variables (`--g1-dark`, `--g1-light`, ...) למיתוג מהיר
