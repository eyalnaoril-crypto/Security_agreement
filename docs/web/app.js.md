---
title: web/static/app.js
type: script
owner: engineering
tags: [web, javascript, sse, frontend]
source: web/static/app.js
related:
  - "[[app.py]]"
  - "[[index.html]]"
  - "[[style.css]]"
---

# web/static/app.js

## מה זה עושה
ההיגיון של הצד-לקוח. JavaScript וניל (ללא framework). מטפל ב:
- **גרירת קובץ** ל-dropzone + לחיצה לפתיחת file picker
- **העלאה** ל-`/upload` עם FormData ומקבל `job_id`
- **לחיצה על "הפעל"** → POST ל-`/run/<job_id>`
- **EventSource** → מאזין ל-`/events/<job_id>` ומעדכן UI בזמן אמת
- **Timeline** → מסמן שלבים active/done לפי אחוז ההתקדמות
- **תוצאות** → מציג כפתורי הורדה ל-XLSX / DOCX / JSON

## תפקיד בפרויקט
מחבר את ה-UI הסטטי ([[index.html]]) עם ה-API של [[app.py]]. כל פעולה אינטראקטיבית עוברת כאן.

## למי זה שייך
- **Owner**: Engineering
- **טוען על-ידי**: [[index.html]]

## קבצים קשורים
- [[app.py]] – ה-endpoints שהקובץ קורא אליהם
- [[index.html]] – ה-DOM שעליו הקובץ פועל
- [[style.css]] – ה-classes ש-app.js מוסיף/מסיר

## הערות
- אין dependencies חיצוניים – שום npm
- שגיאות SSE נבלעות בשקט (השרת סוגר כשמסיים)
- מציג שלבים לפי תחומי אחוזים: extract 5-30%, ai 30-65%, excel 65-88%, word 88-99%
