---
title: analyze_contract.py
type: script
owner: engineering
tags: [entry-point, orchestrator, ai, hebrew]
source: scripts/analyze_contract.py
related:
  - "[[system_prompt.md]]"
  - "[[export_excel.py]]"
  - "[[inject_tracked.py]]"
  - "[[CLAUDE.md]]"
  - "[[requirements.txt]]"
---

# analyze_contract.py

## מה זה עושה
**נקודת הכניסה הראשית של הסוכן.** מקבל נתיב להסכם (DOCX/PDF/TXT), ומריץ את כל הזרימה: חילוץ טקסט → ניתוח AI → ייצוא Excel → הזרקת tracked changes ל-Word.

```bash
python3 analyze_contract.py /path/to/הסכם_לקוח.docx
```

## תפקיד בפרויקט
המתאם (orchestrator). ארבעת השלבים:
1. **`extract_text()`** – mammoth ל-DOCX, pdftotext ל-PDF, קריאה רגילה ל-TXT/MD
2. **`analyze_with_ai()`** – שולח את הטקסט (עד 8,000 תווים) ל-Anthropic API עם [[system_prompt.md]]; מנקה markdown fences ומפענח JSON
3. **`export_excel()`** – מפעיל את [[export_excel.py]] כ-subprocess עם findings JSON
4. **`export_word_tracked()`** – מפעיל את [[inject_tracked.py]] (רק אם הקלט DOCX)

פלטים נשמרים ב-`outputs/` בשמות:
- `[שם]_ניתוח_[תאריך].xlsx`
- `[שם]_עקוב_שינויים_[תאריך].docx`
- `[שם]_findings_[תאריך].json`

## למי זה שייך
- **Owner**: Engineering
- **משתמש**: כל מי שמריץ ניתוח חוזה (משפטי, חוזים, הנהלה)
- **תלוי ב**: `ANTHROPIC_API_KEY` במשתני הסביבה

## קבצים קשורים
- [[system_prompt.md]] – ה-prompt שנטען לזכרון
- [[export_excel.py]] – נקרא דרך subprocess
- [[inject_tracked.py]] – נקרא דרך subprocess
- [[CLAUDE.md]] – מתעד את הזרימה הזו
- [[requirements.txt]] – mammoth, anthropic

## הערות
- חיתוך הטקסט ל-8,000 תווים – אם ההסכם ארוך משמעותית, החלקים האחרונים לא ינותחו
- שני fallbacks ל-API: SDK רשמי `anthropic`, ואם לא מותקן – `urllib.request` ישיר
