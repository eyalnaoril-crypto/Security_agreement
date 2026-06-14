---
title: web/app.py
type: script
owner: engineering
tags: [web, flask, sse, server, ui]
source: web/app.py
related:
  - "[[analyze_contract.py]]"
  - "[[index.html]]"
  - "[[app.js]]"
  - "[[style.css]]"
  - "[[requirements.txt]]"
---

# web/app.py

## מה זה עושה
שרת Flask שמספק ממשק Web לסוכן. מקבל קובץ הסכם דרך הדפדפן, מריץ את [[analyze_contract.py]] ברקע כ-subprocess, ומשדר התקדמות חיה דרך **Server-Sent Events (SSE)** אל הדפדפן. כשהריצה מסתיימת — מציע הורדה של XLSX / DOCX / JSON.

## מסלולים (Routes)
| Method | Path | תפקיד |
|---|---|---|
| GET | `/` | דף הבית ([[index.html]]) |
| POST | `/upload` | קבלת קובץ, יצירת `job_id` |
| POST | `/run/<job_id>` | הפעלת subprocess של הניתוח |
| GET | `/events/<job_id>` | זרם SSE עם התקדמות |
| GET | `/download/<job_id>/<kind>` | הורדת קובץ פלט (xlsx/docx/json) |
| GET | `/status/<job_id>` | מצב נוכחי כ-JSON |

## תפקיד בפרויקט
שכבת הצגה (presentation layer). לא מבצע ניתוח בעצמו – רק מתאם בין UI לבין [[analyze_contract.py]]. מנתח את ה-stdout של הסקריפט עם regex (`STEP_PATTERNS`) כדי להמיר שורות כמו `[2/4]` לאחוזי התקדמות (35%).

## למי זה שייך
- **Owner**: Engineering
- **משתמש**: עו"ד / חוזים / הנהלה – דרך הדפדפן ב-`http://127.0.0.1:5000`
- **תלוי ב**: [[requirements.txt]] (flask), [[analyze_contract.py]]

## קבצים קשורים
- [[analyze_contract.py]] – מופעל כ-subprocess
- [[index.html]] – הדף שמוגש מ-`/`
- [[app.js]] – הצד הלקוח (fetch + EventSource)
- [[style.css]] – עיצוב
- [[requirements.txt]] – Flask נדרש

## הערות
- מאחסן jobs בזיכרון (לא DB) – ייעלמו ב-restart
- מחייב `ANTHROPIC_API_KEY` במשתני סביבה
- בינתיים `host=127.0.0.1` בלבד – לא חשוף לרשת. לפריסה: שנה ל-`0.0.0.0` והוסף auth
