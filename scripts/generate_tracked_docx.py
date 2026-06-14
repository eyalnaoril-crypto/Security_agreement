#!/usr/bin/env python3
"""
מקבל JSON של ממצאים מניתוח הסכם ומייצר DOCX עם:
- עקוב אחר שינויים (tracked changes) על ההסכם המקורי
- הערות (comments) לכל ממצא
- גיליון Excel של ממצאים
"""
import sys, json, os, zipfile, shutil, re, copy
from pathlib import Path
from datetime import datetime

AUTHOR = "G1 Legal AI"
DATE = "2025-06-14T00:00:00Z"

def esc(text):
    """Escape XML special chars"""
    if not text:
        return ""
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;"))

def load_findings(json_path):
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)

def unpack_docx(docx_path, out_dir):
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)
    with zipfile.ZipFile(docx_path, "r") as z:
        z.extractall(out_dir)

def pack_docx(src_dir, out_path, original_docx):
    if os.path.exists(out_path):
        os.remove(out_path)
    with zipfile.ZipFile(original_docx, "r") as orig:
        orig_names = set(orig.namelist())
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                full = os.path.join(root, file)
                arcname = os.path.relpath(full, src_dir).replace("\\", "/")
                z.write(full, arcname)

def read_xml(path):
    with open(path, encoding="utf-8") as f:
        return f.read()

def write_xml(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def next_id(xml_content):
    """Find max w:id in doc and return next available"""
    ids = re.findall(r'w:id="(\d+)"', xml_content)
    return max((int(x) for x in ids), default=0) + 1

def build_comments_xml(findings, start_id=100):
    """Build word/comments.xml content"""
    sev_labels = {"critical": "קריטי", "warning": "אזהרה", "ok": "תקין"}
    tag_prefix = {"critical": "🔴", "warning": "🟡", "ok": "🟢"}

    parts = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
             '<w:comments xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" '
             'xmlns:cx="http://schemas.microsoft.com/office/drawing/2014/chartex" '
             'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
             'xmlns:aink="http://schemas.microsoft.com/office/drawing/2016/ink" '
             'xmlns:am3d="http://schemas.microsoft.com/office/drawing/2017/model3d" '
             'xmlns:o="urn:schemas-microsoft-com:office:office" '
             'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
             'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" '
             'xmlns:v="urn:schemas-microsoft-com:vml" '
             'xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" '
             'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
             'xmlns:w10="urn:schemas-microsoft-com:office:word" '
             'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
             'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" '
             'xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml" '
             'xmlns:w16cex="http://schemas.microsoft.com/office/word/2018/wordml/cex" '
             'xmlns:w16cid="http://schemas.microsoft.com/office/word/2016/wordml/cid" '
             'xmlns:w16="http://schemas.microsoft.com/office/word/2018/wordml" '
             'xmlns:w16se="http://schemas.microsoft.com/office/word/2015/wordml/symex" '
             'xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" '
             'xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" '
             'xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" '
             'xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" '
             'mc:Ignorable="w14 w15 w16se w16cid w16 w16cex w16cex cx aink am3d wp14">']

    for i, f in enumerate(findings):
        cid = start_id + i
        sev = sev_labels.get(f.get("severity",""), f.get("severity",""))
        prefix = tag_prefix.get(f.get("severity",""), "")
        title = esc(f.get("title",""))
        current = esc(f.get("current",""))
        required = esc(f.get("required",""))
        fix = esc(f.get("fix",""))
        clause = esc(f.get("clause_ref",""))
        tag = esc(f.get("tag",""))

        lines = [
            f"{prefix} [{sev}] {title}",
            f"סטטוס: {tag}" + (f" | סעיף: {clause}" if clause else ""),
            f"נוכחי: {current[:200]}{'...' if len(current)>200 else ''}",
            f"נדרש: {required[:200]}{'...' if len(required)>200 else ''}",
        ]
        if fix:
            lines.append(f"נוסח מוצע: {fix[:250]}{'...' if len(fix)>250 else ''}")

        paras = ""
        for line in lines:
            paras += f'''<w:p>
  <w:pPr><w:jc w:val="right"/><w:rPr><w:lang w:bidi="he-IL"/></w:rPr></w:pPr>
  <w:r><w:rPr><w:lang w:bidi="he-IL"/></w:rPr><w:t xml:space="preserve">{line}</w:t></w:r>
</w:p>'''

        parts.append(f'''<w:comment w:id="{cid}" w:author="{esc(AUTHOR)}" w:date="{DATE}" w:initials="G1">
{paras}
</w:comment>''')

    parts.append('</w:comments>')
    return "\n".join(parts)

def build_comments_extended_xml(findings, start_id=100):
    """Build word/commentsExtended.xml for modern Word"""
    parts = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
             '<w15:commentsEx xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" '
             'xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml" '
             'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
             'mc:Ignorable="w15">']
    for i, f in enumerate(findings):
        cid = start_id + i
        parts.append(f'<w15:commentEx w15:paraId="{(cid*7+1):08X}" w15:done="0"/>')
    parts.append('</w15:commentsEx>')
    return "\n".join(parts)

def inject_comments_into_document(doc_xml, findings, start_id=100):
    """
    Inject comment markers + tracked-change insertions into document body.
    Strategy: append a new section at the end of the document with all findings
    as tracked insertions (new paragraphs) with comment markers.
    """
    sev_labels = {"critical": "קריטי ⚠", "warning": "אזהרה", "ok": "תקין ✓"}

    # Find </w:body> to inject before it
    insert_point = doc_xml.rfind("</w:body>")
    if insert_point == -1:
        return doc_xml  # can't inject

    cur_id = start_id * 10  # tracked change IDs
    inserted_blocks = []

    # Add a separator paragraph
    inserted_blocks.append(f'''<w:p>
  <w:pPr><w:jc w:val="right"/><w:rPr><w:ins w:id="{cur_id}" w:author="{esc(AUTHOR)}" w:date="{DATE}"/><w:lang w:bidi="he-IL"/><w:b/></w:rPr></w:pPr>
  <w:ins w:id="{cur_id+1}" w:author="{esc(AUTHOR)}" w:date="{DATE}">
    <w:r><w:rPr><w:b/><w:lang w:bidi="he-IL"/></w:rPr><w:t>&#x2500;&#x2500;&#x2500; ממצאי ניתוח G1 Legal AI &#x2500;&#x2500;&#x2500;</w:t></w:r>
  </w:ins>
</w:p>''')
    cur_id += 2

    for i, f in enumerate(findings):
        cid = start_id + i
        sev = sev_labels.get(f.get("severity",""), "")
        title = esc(f.get("title",""))
        fix = esc(f.get("fix",""))
        tag = esc(f.get("tag",""))
        clause = esc(f.get("clause_ref",""))

        # Build finding summary line
        summary = f"[{sev}] {title}"
        if clause:
            summary += f" ({clause})"
        if fix:
            summary += f" | תיקון: {fix[:120]}"

        # Comment range + tracked insertion paragraph
        inserted_blocks.append(f'''<w:p>
  <w:pPr><w:jc w:val="right"/><w:rPr><w:ins w:id="{cur_id}" w:author="{esc(AUTHOR)}" w:date="{DATE}"/><w:lang w:bidi="he-IL"/></w:rPr></w:pPr>
  <w:commentRangeStart w:id="{cid}"/>
  <w:ins w:id="{cur_id+1}" w:author="{esc(AUTHOR)}" w:date="{DATE}">
    <w:r><w:rPr><w:lang w:bidi="he-IL"/></w:rPr><w:t xml:space="preserve">{esc(summary)}</w:t></w:r>
  </w:ins>
  <w:commentRangeEnd w:id="{cid}"/>
  <w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="{cid}"/></w:r>
</w:p>''')
        cur_id += 2

    injection = "\n".join(inserted_blocks)
    return doc_xml[:insert_point] + "\n" + injection + "\n" + doc_xml[insert_point:]

def ensure_comments_relationship(rels_xml, unpack_dir):
    """Add comment relationships to document.xml.rels if missing"""
    rel_comment = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments'
    rel_comment_ext = 'http://schemas.microsoft.com/office/2011/relationships/commentsExtended'

    if rel_comment not in rels_xml:
        rels_xml = rels_xml.replace(
            '</Relationships>',
            f'<Relationship Id="rIdComments" Type="{rel_comment}" Target="comments.xml"/>\n</Relationships>'
        )
    if rel_comment_ext not in rels_xml:
        rels_xml = rels_xml.replace(
            '</Relationships>',
            f'<Relationship Id="rIdCommentsEx" Type="{rel_comment_ext}" Target="commentsExtended.xml"/>\n</Relationships>'
        )
    return rels_xml

def ensure_content_types(ct_xml):
    """Add comments content types if missing"""
    if 'comments.xml' not in ct_xml:
        ct_xml = ct_xml.replace(
            '</Types>',
            '<Override PartName="/word/comments.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"/>\n</Types>'
        )
    if 'commentsExtended.xml' not in ct_xml:
        ct_xml = ct_xml.replace(
            '</Types>',
            '<Override PartName="/word/commentsExtended.xml" ContentType="application/vnd.ms-office.activeX+xml"/>\n</Types>'
        )
    return ct_xml

def process(docx_in, findings_json, docx_out):
    data = load_findings(findings_json)
    findings = data.get("findings", [])
    summary = data.get("summary", "")

    print(f"Processing {len(findings)} findings...")

    # Unpack
    unpack_dir = "/tmp/docx_unpack"
    unpack_docx(docx_in, unpack_dir)

    # Read document XML
    doc_path = os.path.join(unpack_dir, "word", "document.xml")
    rels_path = os.path.join(unpack_dir, "word", "_rels", "document.xml.rels")
    ct_path = os.path.join(unpack_dir, "[Content_Types].xml")

    doc_xml = read_xml(doc_path)
    rels_xml = read_xml(rels_path)
    ct_xml = read_xml(ct_path)

    # Build and write comments.xml
    comments_xml = build_comments_xml(findings, start_id=100)
    write_xml(os.path.join(unpack_dir, "word", "comments.xml"), comments_xml)

    # Build and write commentsExtended.xml
    comments_ext_xml = build_comments_extended_xml(findings, start_id=100)
    write_xml(os.path.join(unpack_dir, "word", "commentsExtended.xml"), comments_ext_xml)

    # Inject comment markers + tracked insertions into document body
    doc_xml = inject_comments_into_document(doc_xml, findings, start_id=100)
    write_xml(doc_path, doc_xml)

    # Update relationships
    rels_xml = ensure_comments_relationship(rels_xml, unpack_dir)
    write_xml(rels_path, rels_xml)

    # Update content types
    ct_xml = ensure_content_types(ct_xml)
    write_xml(ct_path, ct_xml)

    # Repack
    pack_docx(unpack_dir, docx_out, docx_in)
    print(f"Done: {docx_out}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python generate_tracked_docx.py <input.docx> <findings.json> <output.docx>")
        sys.exit(1)
    process(sys.argv[1], sys.argv[2], sys.argv[3])
