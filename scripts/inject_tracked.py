#!/usr/bin/env python3
"""
inject_tracked.py
=================
מזריק tracked changes ו-comments ישירות בתוך פסקאות ההסכם,
בדיוק במקום שבו הם שייכים (לא בסוף הקובץ).

שימוש:
    python3 inject_tracked.py <input.docx> <findings.json> <output.docx>
"""

import sys, json, os, zipfile, shutil, copy, re
from pathlib import Path

try:
    from lxml import etree
    LXML = True
except ImportError:
    import xml.etree.ElementTree as etree
    LXML = False

AUTHOR = "G1 Legal AI"
DATE   = "2025-06-14T00:00:00Z"
W      = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def wtag(n):
    return f"{{{W}}}{n}"


# ─────────────────────────────────────────────
# ZIP helpers
# ─────────────────────────────────────────────
def unpack(docx_path, out_dir):
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)
    with zipfile.ZipFile(docx_path, "r") as z:
        z.extractall(out_dir)


def repack(src_dir, out_path):
    if os.path.exists(out_path):
        os.remove(out_path)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(src_dir):
            for f in files:
                full = os.path.join(root, f)
                arc  = os.path.relpath(full, src_dir).replace("\\", "/")
                z.write(full, arc)


# ─────────────────────────────────────────────
# XML element builders
# ─────────────────────────────────────────────
def make_del_run(text, rpr, change_id):
    el = etree.Element(wtag("del"))
    el.set(wtag("id"), str(change_id))
    el.set(wtag("author"), AUTHOR)
    el.set(wtag("date"), DATE)
    r = etree.SubElement(el, wtag("r"))
    if rpr is not None:
        r.append(copy.deepcopy(rpr))
    dt = etree.SubElement(r, wtag("delText"))
    dt.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    dt.text = text
    return el


def make_ins_run(text, rpr, change_id):
    el = etree.Element(wtag("ins"))
    el.set(wtag("id"), str(change_id))
    el.set(wtag("author"), AUTHOR)
    el.set(wtag("date"), DATE)
    r = etree.SubElement(el, wtag("r"))
    if rpr is not None:
        r.append(copy.deepcopy(rpr))
    t = etree.SubElement(r, wtag("t"))
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    return el


def make_ins_para(text, rpr, change_id):
    """Entire new paragraph inserted as tracked change."""
    p = etree.Element(wtag("p"))
    ppr = etree.SubElement(p, wtag("pPr"))
    jc  = etree.SubElement(ppr, wtag("jc"))
    jc.set(wtag("val"), "right")
    rpr2 = etree.SubElement(ppr, wtag("rPr"))
    ins_mark = etree.SubElement(rpr2, wtag("ins"))
    ins_mark.set(wtag("id"), str(change_id))
    ins_mark.set(wtag("author"), AUTHOR)
    ins_mark.set(wtag("date"), DATE)
    ins_el = etree.SubElement(p, wtag("ins"))
    ins_el.set(wtag("id"), str(change_id + 1))
    ins_el.set(wtag("author"), AUTHOR)
    ins_el.set(wtag("date"), DATE)
    r = etree.SubElement(ins_el, wtag("r"))
    if rpr is not None:
        r.append(copy.deepcopy(rpr))
    t = etree.SubElement(r, wtag("t"))
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    return p


def make_comment_start(cid):
    el = etree.Element(wtag("commentRangeStart"))
    el.set(wtag("id"), str(cid))
    return el


def make_comment_end(cid):
    el = etree.Element(wtag("commentRangeEnd"))
    el.set(wtag("id"), str(cid))
    return el


def make_comment_ref(cid):
    r = etree.Element(wtag("r"))
    rpr = etree.SubElement(r, wtag("rPr"))
    rs = etree.SubElement(rpr, wtag("rStyle"))
    rs.set(wtag("val"), "CommentReference")
    ref = etree.SubElement(r, wtag("commentReference"))
    ref.set(wtag("id"), str(cid))
    return r


# ─────────────────────────────────────────────
# Para helpers
# ─────────────────────────────────────────────
def para_text(p):
    return "".join(t.text or "" for t in p.findall(f".//{{{W}}}t"))


def get_rpr(run):
    rpr = run.find(wtag("rPr"))
    return copy.deepcopy(rpr) if rpr is not None else None


def find_para_containing(paras, search_str):
    for p in paras:
        if search_str in para_text(p):
            return p
    return None


# ─────────────────────────────────────────────
# Core: apply one finding to the document tree
# ─────────────────────────────────────────────
def apply_finding(body, paras, finding, change_id, comment_id):
    """
    Apply a single finding as an inline tracked change.
    Returns (new_change_id, new_comment_id, did_apply).
    """
    search   = finding.get("search_text", "").strip()
    original = finding.get("original_text", "").strip()
    replace  = finding.get("replacement_text", "").strip()
    fix      = finding.get("fix", "").strip()
    ch_type  = finding.get("change_type", "insert")   # replace | delete | insert
    severity = finding.get("severity", "warning")
    title    = finding.get("title", "")

    # ── locate paragraph ──────────────────────────────────────────────
    target_para = None
    if search:
        target_para = find_para_containing(paras, search)
    if target_para is None and original:
        target_para = find_para_containing(paras, original)

    if ch_type == "insert" and target_para is None:
        # New clause – insert near a related heading if possible
        target_para = find_para_containing(paras, finding.get("clause_ref", ""))

    # ── apply change ──────────────────────────────────────────────────
    applied = False

    if ch_type in ("replace", "delete") and target_para is not None and original:
        # Find the run(s) containing original_text
        for run in list(target_para):
            if run.tag != wtag("r"):
                continue
            for t_el in run.findall(wtag("t")):
                if t_el.text and original in t_el.text:
                    rpr = get_rpr(run)
                    full = t_el.text
                    idx  = full.index(original)
                    before_txt = full[:idx]
                    after_txt  = full[idx + len(original):]

                    # Shrink original run to 'before'
                    t_el.text = before_txt if before_txt else None
                    if not before_txt:
                        run.remove(t_el)

                    r_pos = list(target_para).index(run)

                    # Delete node
                    del_node = make_del_run(original, rpr, change_id)

                    # Insert node
                    if ch_type == "replace" and replace:
                        ins_node = make_ins_run(replace, rpr, change_id + 1)
                    elif ch_type == "replace" and fix:
                        ins_node = make_ins_run(fix[:200], rpr, change_id + 1)
                    else:
                        ins_node = None

                    # After text run
                    if after_txt:
                        r_after = etree.Element(wtag("r"))
                        if rpr:
                            r_after.append(copy.deepcopy(rpr))
                        ta = etree.SubElement(r_after, wtag("t"))
                        ta.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
                        ta.text = after_txt
                        target_para.insert(r_pos + 1, r_after)
                        offset = r_pos + 1
                    else:
                        offset = r_pos + 1

                    if ins_node is not None:
                        target_para.insert(offset, ins_node)
                    target_para.insert(offset, del_node)

                    # Comment range
                    final_pos = list(target_para).index(del_node)
                    target_para.insert(final_pos + (2 if ins_node else 1), make_comment_end(comment_id))
                    target_para.insert(final_pos + (2 if ins_node else 1), make_comment_ref(comment_id))
                    target_para.insert(final_pos, make_comment_start(comment_id))

                    change_id += 2
                    applied = True
                    break
            if applied:
                break

    elif ch_type == "insert":
        # Insert a new paragraph after the nearest located paragraph
        anchor_para = target_para
        if anchor_para is None:
            # Fall back to end of body
            anchor_para = paras[-1] if paras else None

        if anchor_para is not None:
            insert_text = fix or replace or f"[G1] {title}: {finding.get('required','')[:300]}"
            new_p = make_ins_para(insert_text, None, change_id)
            body_children = list(body)
            try:
                idx = body_children.index(anchor_para)
            except ValueError:
                idx = len(body_children) - 1
            body.insert(idx + 1, new_p)

            # Re-fetch paras since we inserted
            paras.append(new_p)

            change_id += 2
            applied = True

    return change_id, comment_id + 1, applied


# ─────────────────────────────────────────────
# Build comments.xml
# ─────────────────────────────────────────────
def build_comments_xml(findings, base_comment_id=100):
    sev_prefix = {"critical": "🔴 קריטי", "warning": "🟡 אזהרה", "ok": "🟢 תקין"}

    def esc(t):
        return (t or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    parts = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        f'<w:comments xmlns:w="{W}" '
        'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">'
    ]

    for i, f in enumerate(findings):
        cid    = base_comment_id + i
        prefix = sev_prefix.get(f.get("severity",""), "")
        lines  = [
            f"{prefix} | {f.get('title','')}",
            f"סעיף: {f.get('clause_ref','—')} | סטטוס: {f.get('tag','')}",
            f"נוכחי: {(f.get('current',''))[:200]}",
            f"נדרש: {(f.get('required',''))[:200]}",
        ]
        fix = f.get("fix","")
        if fix:
            lines.append(f"תיקון מוצע: {fix[:250]}")

        paras_xml = "".join(
            f'<w:p><w:pPr><w:jc w:val="right"/>'
            f'<w:rPr><w:lang w:bidi="he-IL"/></w:rPr></w:pPr>'
            f'<w:r><w:rPr><w:lang w:bidi="he-IL"/></w:rPr>'
            f'<w:t xml:space="preserve">{esc(line)}</w:t></w:r></w:p>'
            for line in lines
        )
        parts.append(
            f'<w:comment w:id="{cid}" w:author="{esc(AUTHOR)}" '
            f'w:date="{DATE}" w:initials="G1">{paras_xml}</w:comment>'
        )

    parts.append("</w:comments>")
    return "\n".join(parts)


# ─────────────────────────────────────────────
# Ensure rels + content types contain comments
# ─────────────────────────────────────────────
def ensure_comments_rels(unpack_dir):
    rels_path = os.path.join(unpack_dir, "word", "_rels", "document.xml.rels")
    ct_path   = os.path.join(unpack_dir, "[Content_Types].xml")

    REL_NS  = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments"
    CT_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"

    with open(rels_path, encoding="utf-8") as f:
        rels = f.read()
    if REL_NS not in rels:
        rels = rels.replace(
            "</Relationships>",
            f'<Relationship Id="rIdComments" Type="{REL_NS}" Target="comments.xml"/>\n</Relationships>'
        )
        with open(rels_path, "w", encoding="utf-8") as f:
            f.write(rels)

    with open(ct_path, encoding="utf-8") as f:
        ct = f.read()
    if "comments.xml" not in ct:
        ct = ct.replace(
            "</Types>",
            f'<Override PartName="/word/comments.xml" ContentType="{CT_TYPE}"/>\n</Types>'
        )
        with open(ct_path, "w", encoding="utf-8") as f:
            f.write(ct)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def process(docx_in, findings_json_path, docx_out):
    with open(findings_json_path, encoding="utf-8") as f:
        data = json.load(f)

    findings = data.get("findings", [])
    print(f"  מעבד {len(findings)} ממצאים...")

    # Unpack
    unpack_dir = "/tmp/_g1_tracked_inject"
    unpack(docx_in, unpack_dir)

    doc_path = os.path.join(unpack_dir, "word", "document.xml")
    with open(doc_path, encoding="utf-8") as f:
        raw = f.read()

    if LXML:
        tree = etree.fromstring(raw.encode("utf-8"))
    else:
        tree = etree.fromstring(raw)

    body  = tree.find(f".//{{{W}}}body")
    paras = list(body.findall(f".//{{{W}}}p"))

    change_id  = 300
    comment_id = 100
    applied    = 0

    # Sort: critical first (so they get lower IDs)
    order = {"critical": 0, "warning": 1, "ok": 2}
    sorted_findings = sorted(findings, key=lambda f: order.get(f.get("severity", "ok"), 2))

    for finding in sorted_findings:
        if finding.get("severity") == "ok":
            # OK findings → comment only (no change needed)
            comment_id += 1
            continue

        change_id, comment_id, did_apply = apply_finding(
            body, paras, finding, change_id, comment_id
        )
        if did_apply:
            applied += 1

    print(f"  ✓ {applied} שינויים הוחלו inline")

    # Write document.xml
    if LXML:
        result = etree.tostring(tree, encoding="unicode", xml_declaration=False)
    else:
        result = etree.tostring(tree, encoding="unicode")

    with open(doc_path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
        f.write(result)

    # Write comments.xml
    non_ok = [f for f in findings if f.get("severity") != "ok"]
    comments_xml = build_comments_xml(non_ok, base_comment_id=100)
    with open(os.path.join(unpack_dir, "word", "comments.xml"), "w", encoding="utf-8") as f:
        f.write(comments_xml)

    # Update rels + content types
    ensure_comments_rels(unpack_dir)

    # Repack
    repack(unpack_dir, docx_out)
    print(f"  ✓ DOCX נשמר: {docx_out}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("שימוש: python3 inject_tracked.py <input.docx> <findings.json> <output.docx>")
        sys.exit(1)
    process(sys.argv[1], sys.argv[2], sys.argv[3])
