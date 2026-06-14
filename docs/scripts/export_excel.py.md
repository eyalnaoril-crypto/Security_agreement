---
title: export_excel.py
type: script
owner: engineering
tags: [excel, reporting, openpyxl, hebrew, rtl]
source: scripts/export_excel.py
related:
  - "[[analyze_contract.py]]"
  - "[[system_prompt.md]]"
  - "[[requirements.txt]]"
---

# export_excel.py

## מה זה עושה
מקבל JSON של ממצאים (פלט מה-AI) ומייצר קובץ Excel בעברית RTL עם **3 גיליונות**:
1. **סיכום** – תקציר, סיכון כולל, מספרי ממצאים, הערת ביטוחים, נספחים חסרים
2. **ממצאים מפורטים** – טבלה של כל ה-findings, ממוינת לפי חומרה
3. **סדר עדיפויות לתיקון** – רק ממצאים קריטיים, מסודרים לפעולה

## תפקיד בפרויקט
שלב 3 בזרימה. נקרא על-ידי [[analyze_contract.py]] כ-subprocess:
```bash
python3 export_excel.py '<json_string>' output.xlsx "שם לקוח"
```
מקבל JSON גם כמחרוזת inline וגם כנתיב לקובץ.

## עיצוב
- **RTL** מופעל ב-`ws.sheet_view.rightToLeft = True` לכל גיליון
- צבעים: G1 ירוק כהה לכותרות, אדום/ענבר/ירוק לפי חומרה
- גופן Arial, גודלים 10-14
- גובהי שורות ורוחבי עמודות מותאמים לעברית

## למי זה שייך
- **Owner**: Engineering
- **משתמש**: [[analyze_contract.py]]
- **נצרך על-ידי**: עו"ד/הנהלה לסקירה ב-Excel

## קבצים קשורים
- [[analyze_contract.py]] – המפעיל
- [[system_prompt.md]] – מגדיר את שמות השדות שהקובץ הזה צורך (`severity`, `title`, `clause_ref`, ...)
- [[requirements.txt]] – openpyxl

## הערות
ניתן להריץ גם standalone אם יש JSON שמור:
```bash
python3 export_excel.py outputs/findings.json out.xlsx "G1"
```
