---
title: inject_tracked.py
type: script
owner: engineering
tags: [docx, tracked-changes, lxml, ooxml, hebrew]
source: scripts/inject_tracked.py
related:
  - "[[analyze_contract.py]]"
  - "[[generate_tracked_docx.py]]"
  - "[[pack.py]]"
  - "[[unpack.py]]"
  - "[[validate.py]]"
  - "[[system_prompt.md]]"
---

# inject_tracked.py

## מה זה עושה
מקבל את ה-DOCX המקורי של הלקוח + JSON של ממצאים, ומזריק tracked changes ו-comments **בדיוק במקום הנכון בתוך הפסקאות** (לא בסוף הקובץ). הפלט: DOCX חדש שנפתח ב-Word עם "track changes" פעיל ועם הערות לכל ממצא.

```bash
python3 inject_tracked.py input.docx findings.json output.docx
```

## תפקיד בפרויקט
שלב 4 בזרימה (רק עבור קלט DOCX). השלב הכי מורכב טכנית. הפעולה:
1. **`unpack()`** – פרק את ה-DOCX ל-`/tmp/_g1_tracked_inject/`
2. עבור כל finding (`change_type` = replace / delete / insert):
   - אתר את הפסקה המכילה את `search_text` או `original_text`
   - בנה אלמנטי `<w:del>` ו-`<w:ins>` עם author="G1 Legal AI"
   - הזרק comment range (`commentRangeStart` / `commentRangeEnd` / `commentReference`)
3. **`build_comments_xml()`** – מייצר `comments.xml` עם תוכן מובנה לכל ממצא
4. **`ensure_comments_rels()`** – מעדכן את `document.xml.rels` ו-`[Content_Types].xml`
5. **`repack()`** – ארוז חזרה ל-DOCX

## למי זה שייך
- **Owner**: Engineering
- **משתמש**: [[analyze_contract.py]] (subprocess)
- **נצרך על-ידי**: עו"ד שפותח את ה-DOCX ב-Word ורואה את הסימונים inline

## קבצים קשורים
- [[analyze_contract.py]] – המפעיל
- [[generate_tracked_docx.py]] – גרסה ישנה שאת תפקידה ירש קובץ זה
- [[pack.py]] / [[unpack.py]] / [[validate.py]] – ארגז כלים נפרד לעבודה עם DOCX (לא בשימוש ישיר כאן, אבל מקביל מבחינה רעיונית)
- [[system_prompt.md]] – מגדיר את השדות (`search_text`, `original_text`, `replacement_text`, `change_type`) שהקובץ הזה צורך

## הערות
- חיפוש הטקסט המקורי הוא literal substring – אם ה-AI טועה בציטוט, ההזרקה תיכשל בשקט (`did_apply = False`)
- ה-namespace `http://schemas.openxmlformats.org/wordprocessingml/2006/main` משמש לכל אלמנט
- ממצאי `ok` מקבלים comment בלבד, לא שינוי בפועל
- ה-IDs: change_id מתחיל ב-300, comment_id ב-100 (להימנע מהתנגשות עם IDs קיימים בקובץ)
