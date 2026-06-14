---
title: system_prompt.md
type: prompt
owner: legal
tags: [ai-prompt, hebrew, legal-analysis]
source: data/system_prompt.md
related:
  - "[[analyze_contract.py]]"
  - "[[generic_contract.md]]"
  - "[[CLAUDE.md]]"
---

# system_prompt.md

## מה זה עושה
ה-system prompt שנשלח למודל Claude (sonnet-4-6) לניתוח הסכמי שמירה. מגדיר את התפקיד המשפטי, את נקודות העיגון של ההסכם הגנרי, ואת **מבנה ה-JSON המדויק** שהמודל חייב להחזיר.

## תפקיד בפרויקט
- מקודד את **נקודות המפתח של ההסכם הגנרי** (סעיפים 4, 5, 7, 8.4, 9, 11, 12, 14)
- מציב **דגלים אדומים אסורים**: שיפוי מיידי ללא פסק דין, שוטף+60, ביטול חד-צדדי <60 יום
- מורה למודל: **JSON בלבד, בעברית בלבד, ללא markdown**
- מגדיר את שדות ה-findings: `id`, `severity`, `title`, `tag`, `clause_ref`, `current`, `required`, `fix`, `search_text`, `original_text`, `replacement_text`, `change_type`

## למי זה שייך
- **Owner**: Legal (G1 in-house counsel)
- **נטען על-ידי**: [[analyze_contract.py]] בפונקציה `analyze_with_ai()`
- **שינויים בו** משנים את אופי הניתוח של כל הסכם – טעון אישור משפטי

## קבצים קשורים
- [[analyze_contract.py]] – טוען וקורא את הקובץ הזה
- [[generic_contract.md]] – פירוט מלא של ההסכם הגנרי (גרסה ארוכה)
- [[inject_tracked.py]] – צרכן של ה-JSON שמתבסס על הפורמט המוגדר כאן
- [[export_excel.py]] – גם כן צורך את אותו JSON

## הערות
חיתוך ל-8,000 תווים מתבצע ב-[[analyze_contract.py]] לפני שליחה ל-API.
