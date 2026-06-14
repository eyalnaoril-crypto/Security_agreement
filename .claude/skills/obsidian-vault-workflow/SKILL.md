---
name: obsidian-vault-workflow
description: Walk a project directory and produce an Obsidian-compatible documentation vault under docs/ — one Markdown file per source file with YAML frontmatter (title, type, owner, tags, related), Hebrew RTL body explaining what the file does and who owns it, and [[wikilinks]] to related files. Builds a folder structure mirroring the source tree and emits docs/INDEX.md as the vault entry point. Use whenever the user asks to document a codebase, create an Obsidian vault, build project docs, map a repo, or generate per-file MD with frontmatter and backlinks. Pure Markdown output — no Obsidian plugin required.
---

# Obsidian Vault Workflow

## מטרה
לקבל תיקיית פרויקט, לסרוק כל קובץ, ולהפיק vault תיעוד תואם-Obsidian תחת `docs/` עם:
- קובץ MD אחד לכל קובץ מקור
- YAML frontmatter (`title`, `type`, `owner`, `tags`, `related`)
- גוף בעברית RTL שמסביר מה הקובץ עושה, למי הוא שייך, ואיך הוא מתחבר לאחרים
- `[[wikilinks]]` לקבצים קשורים – Obsidian יפתור אותם אוטומטית
- `docs/INDEX.md` שמשמש כדף שער של ה-vault

## מתי להפעיל
- המשתמש מבקש "תייצר תיעוד", "צור vault", "מפה את הקוד", "תרשום MD לכל קובץ"
- בתחילת סשן בפרויקט שיש בו זיכרון feedback שמפעיל את הסקיל אוטומטית
- כשמשתמש מציין Obsidian, MD vault, או wikilinks

## תהליך

### 1. סריקה
- הפעל `Glob` עם `**/*` תחת שורש הפרויקט
- דלג על: `.git/`, `node_modules/`, `outputs/`, `__pycache__/`, `.venv/`, `dist/`, `build/`
- אסוף רשימת קבצים + תיקיות

### 2. סיווג כל קובץ (`type`)
| סיומת/תפקיד | `type` |
|---|---|
| `.py` שמורץ ישירות | `script` |
| `.py` עזר/מודול | `module` |
| `.md` של מפרט/prompt | `prompt` |
| `.md` של תוכן (חוזה גנרי, פלייבוק) | `data` |
| `.json`/`.yaml` תצורה | `config` |
| `requirements.txt`, `package.json` | `dependencies` |
| `CLAUDE.md`, `README.md` | `instructions` |
| `.gitignore`, `Dockerfile` | `infra` |
| `.docx`/`.pdf`/`.xlsx` | `document` |

### 3. זיהוי בעלות (`owner`)
בחר לפי תוכן הקובץ ושמו:
- `legal` – חוזים, prompts משפטיים, תבניות
- `engineering` – סקריפטים, מודולים, build
- `product` – CLAUDE.md, מפרטי מוצר
- `ops` – CI, Docker, deployment
- `shared` – README, INDEX, מסמכי-על

### 4. גלה קשרים (`related`)
לכל קובץ, אתר:
- **imports**: בקבצי `.py` חפש `import X` / `from X import` ומפה לקבצים אחרים בפרויקט
- **רפרנסים בטקסט**: גרפ אחרי שמות קבצים אחרים בתוך התוכן (לדוגמה `system_prompt.md` מוזכר ב-`analyze_contract.py`)
- **subprocess calls**: חפש `subprocess.run([... script.py ...])`
- **נתיבים נצרכים**: `Path(__file__).parent / "data" / "X"` → תלוי ב-X

### 5. כתיבת קובץ MD לכל קובץ מקור
מבנה `docs/<relative_path>.md` (משכפל את עץ המקור):

```markdown
---
title: שם_הקובץ
type: script | module | prompt | data | config | ...
owner: legal | engineering | product | ops | shared
tags: [tag1, tag2]
source: scripts/foo.py
related:
  - "[[bar.py]]"
  - "[[system_prompt.md]]"
---

# שם הקובץ

## מה זה עושה
פסקה קצרה בעברית.

## תפקיד בפרויקט
איפה הוא יושב בזרימה (קלט → מה הוא עושה → פלט).

## למי זה שייך
מי הבעלים, מי משתמש, מתי קוראים לו.

## קבצים קשורים
- [[related_file_1]] – הסבר קצר על הקשר
- [[related_file_2]] – הסבר קצר על הקשר

## הערות
כל דבר שלא ברור מקריאת הקוד.
```

### 6. INDEX.md
כתוב `docs/INDEX.md` שמכיל:
- כותרת + תקציר הפרויקט
- מפת זרימה (קלט → AI → Excel + Word)
- רשימת קבצים מאורגנת לפי `owner` ו-`type`, כל פריט עם `[[wikilink]]`
- קישור ל-CLAUDE.md / README

## כללי כתיבה
- **עברית RTL** בגוף הטקסט (frontmatter באנגלית)
- שם הקובץ ב-wikilink הוא basename בלבד (`[[analyze_contract.py]]`, לא הנתיב המלא) – Obsidian יפתור גלובלי
- שמות קבצי MD משקפים את המקור: `analyze_contract.py` → `analyze_contract.py.md`
- אל תיצור MD לקבצי בינארי גדולים (>1MB) או לקבצים שב-`.gitignore`
- שמור על תיאורים קצרים (3-6 שורות לסעיף), לא חזרות על הקוד

## פלט סופי
מבנה `docs/`:
```
docs/
├── INDEX.md
├── CLAUDE.md.md
├── data/
│   ├── system_prompt.md.md
│   └── generic_contract.md.md
└── scripts/
    ├── analyze_contract.py.md
    └── ...
```

הודע למשתמש: "ה-vault מוכן ב-`docs/`. פתח את `docs/INDEX.md` ב-Obsidian (File → Open Vault → בחר את התיקיה השורש של הפרויקט) כדי לראות את הגרף."
