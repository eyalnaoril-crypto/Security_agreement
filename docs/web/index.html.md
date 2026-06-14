---
title: web/templates/index.html
type: data
owner: engineering
tags: [web, html, ui, rtl, hebrew]
source: web/templates/index.html
related:
  - "[[app.py]]"
  - "[[style.css]]"
  - "[[app.js]]"
---

# web/templates/index.html

## מה זה עושה
תבנית Jinja2 שמהווה את דף הבית של הממשק. RTL מלא בעברית, גופן Heebo מ-Google Fonts. מורכב מ-4 כרטיסים מסודרים:
1. **העלאת הסכם** – dropzone + file input
2. **הפעלת הניתוח** – כפתור "הפעל" ראשי
3. **התקדמות הטיפול** – progress bar + timeline + יומן
4. **תוצאות לבדיקה** – שלושה כפתורי הורדה

## תפקיד בפרויקט
ה-shell של ה-UI. כל ההיגיון נמצא ב-[[app.js]], כל העיצוב ב-[[style.css]].

## למי זה שייך
- **Owner**: Engineering / Design
- **מוגש על-ידי**: [[app.py]] במסלול `/`

## קבצים קשורים
- [[app.py]] – render_template
- [[style.css]] – עיצוב
- [[app.js]] – אינטראקטיביות

## הערות
- בנוי semantic HTML5 (`<section>`, `<details>`)
- אין framework (וניל) – זריז ופשוט לתחזוקה
