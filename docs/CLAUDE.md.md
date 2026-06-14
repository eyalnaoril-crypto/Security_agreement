---
title: CLAUDE.md
type: instructions
owner: product
tags: [agent-config, hebrew, workflow]
source: CLAUDE.md
related:
  - "[[system_prompt.md]]"
  - "[[analyze_contract.py]]"
  - "[[generic_contract.md]]"
---

# CLAUDE.md

## מה זה עושה
קובץ הנחיות הסוכן (project-level system prompt) של Claude Code עבור פרויקט G1 Security Contract Agent. נטען אוטומטית לכל סשן בתיקייה הזו ומגדיר לסוכן את התפקיד, הזרימה, מבנה הפלטים, וההוראות הטכניות.

## תפקיד בפרויקט
- מגדיר את **תפקיד הסוכן**: עורך דין מסחרי המייצג את G1 Group
- מתאר את **זרימת העבודה** (קלט DOCX/PDF → חילוץ → ניתוח AI → Excel + Word)
- מתעד את **כל הסקריפטים** ותפקידם
- מציב כללי פלט: עברית RTL, חומרות (🔴/🟡/🟢), שמות קבצים סטנדרטיים

## למי זה שייך
- **Owner**: Product / Eyal Naor
- **קוראים אליו**: Claude Code (אוטומטית בכל סשן בפרויקט)
- **משפיע על**: כל פעולה שהסוכן עושה בפרויקט

## קבצים קשורים
- [[system_prompt.md]] – ה-prompt המפורט שנשלח ל-API (שכבה עמוקה יותר)
- [[analyze_contract.py]] – הסקריפט שמיישם את הזרימה שמתוארת כאן
- [[generic_contract.md]] – החוזה הגנרי שמשמש כבסיס השוואה

## הערות
שני המסמכים `CLAUDE.md` ו-`system_prompt.md` משלימים זה את זה: ה-CLAUDE.md מנחה את **הסוכן בסשן** (איזה סקריפט להריץ, איזה קובץ ליצור), בעוד ש-`system_prompt.md` מנחה את **מודל ה-API** מה לכלול בניתוח עצמו.
