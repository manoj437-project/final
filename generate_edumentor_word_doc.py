# -*- coding: utf-8 -*-
"""
EduMentor AI - Academic Project Report Generator (.docx)
Replicates the exact format, font styles, font sizes, line spacing, margins, page dividers,
and academic layout of the Thiagarajar College (Autonomous) B.Sc Computer Science project report.
"""

import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def build_report():
    doc = Document()

    # ---------------------------------------------------------
    # Document Default Styles & Font Configuration
    # Ensure Times New Roman everywhere
    # ---------------------------------------------------------
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Times New Roman'
    style_normal.font.size = Pt(12)
    style_normal.font.color.rgb = RGBColor(0, 0, 0)
    style_normal.paragraph_format.line_spacing = 1.3
    style_normal.paragraph_format.space_after = Pt(6)

    # Set document default XML fonts to Times New Roman
    rPr = style_normal.element.get_or_add_rPr()
    rFonts = parse_xml(
        f'<w:rFonts {nsdecls("w")} w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>'
    )
    rPr.append(rFonts)

    def set_margins(section, top=1.0, bottom=1.0, left=1.2, right=1.0):
        section.top_margin = Inches(top)
        section.bottom_margin = Inches(bottom)
        section.left_margin = Inches(left)
        section.right_margin = Inches(right)
        section.page_width = Inches(8.27)   # A4
        section.page_height = Inches(11.69) # A4

    def add_p(text="", align=WD_ALIGN_PARAGRAPH.JUSTIFY, bold=False, italic=False, size=12, space_before=0, space_after=6, line_spacing=1.3):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = line_spacing
        if text:
            run = p.add_run(text)
            run.bold = bold
            run.italic = italic
            run.font.name = 'Times New Roman'
            run.font.size = Pt(size)
            run.font.color.rgb = RGBColor(0, 0, 0)
        return p

    def add_heading_1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run.font.color.rgb = RGBColor(0, 0, 0)
        return p

    def add_heading_2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(0, 0, 0)
        return p

    def add_heading_3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(0, 0, 0)
        return p

    def add_bullet(text, space_after=4):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.left_indent = Inches(0.4)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.2
        run = p.add_run(f"•  {text}")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(0, 0, 0)
        return p

    def add_code_line(text, indent_level=0):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        indent = Inches(0.2 + (indent_level * 0.25))
        p.paragraph_format.left_indent = indent
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(0, 0, 0)
        return p

    def add_divider_page(title):
        for _ in range(8):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(title)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(18)
        run.font.color.rgb = RGBColor(0, 0, 0)
        doc.add_page_break()

    def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = OxmlElement('w:tcMar')
        for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
            node = OxmlElement(f'w:{m}')
            node.set(qn('w:w'), str(val))
            node.set(qn('w:type'), 'dxa')
            tcMar.append(node)
        tcPr.append(tcMar)

    def set_table_borders(table):
        tblPr = table._tbl.tblPr
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'<w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            f'<w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            f'<w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            f'<w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            f'</w:tblBorders>'
        )
        tblPr.append(borders)

    # ---------------------------------------------------------
    # SECTION 1: FRONT MATTER (Pages 1 to 6)
    # Unnumbered pages in footer
    # ---------------------------------------------------------
    sec1 = doc.sections[0]
    set_margins(sec1)
    sec1.footer.is_linked_to_previous = False

    # ---------------------------------------------------------
    # PAGE 1: TITLE PAGE (COVER)
    # ---------------------------------------------------------
    add_p("EDUMENTOR AI", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=20, space_before=20, space_after=12)
    add_p("Submitted in partial fulfilment of the requirements for the award of\nthe Degree of", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=12, space_before=10, space_after=10, line_spacing=1.3)
    add_p("Bachelor of Science in Computer Science", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, italic=True, size=13, space_before=0, space_after=20)

    add_p("Submitted By", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=12, space_before=0, space_after=4)
    add_p("Manoj Pandi P (24UCS07)", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=12, space_before=0, space_after=2)
    add_p("Sasi Kumar G (24UCS13)", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=12, space_before=0, space_after=16)

    add_p("Under the Guidance of", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=12, space_before=0, space_after=4)
    add_p("Dr. M.R.SUMATHI MCA.,M.Phil.,Ph.D.,", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=12, space_before=0, space_after=14)

    # College Logo
    if os.path.exists("college_logo.png"):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(4)
        p_logo.paragraph_format.space_after = Pt(12)
        run_logo = p_logo.add_run()
        run_logo.add_picture("college_logo.png", width=Inches(1.35))

    add_p("DEPARTMENT OF COMPUTER SCIENCE", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=12, space_before=0, space_after=4)
    add_p("THIAGARAJAR COLLEGE (AUTONOMOUS)", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=13, space_before=0, space_after=2)
    add_p("(Affiliated to Madurai Kamaraj University)", align=WD_ALIGN_PARAGRAPH.CENTER, bold=False, size=11, space_before=0, space_after=2)
    add_p("Re-accredited with ‘A++’ Grade by NAAC", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=11, space_before=0, space_after=2)
    add_p("Ranked 20th in NIRF 2025", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=11, space_before=0, space_after=2)
    add_p("Madurai – 625009", align=WD_ALIGN_PARAGRAPH.CENTER, bold=False, size=11, space_before=0, space_after=10)
    add_p("October/November– 2026", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=11, space_before=0, space_after=0)

    doc.add_page_break()

    # ---------------------------------------------------------
    # PAGE 2: BONAFIDE CERTIFICATE
    # ---------------------------------------------------------
    add_p("THIAGARAJAR COLLEGE (AUTONOMOUS)", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=13, space_before=16, space_after=2)
    add_p("(Affiliated to Madurai Kamaraj University)", align=WD_ALIGN_PARAGRAPH.CENTER, bold=False, size=11, space_before=0, space_after=2)
    add_p("Re-Accredited with ‘A++’ Grade by NAAC", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=11, space_before=0, space_after=2)
    add_p("Ranked 20th in NIRF 2025", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=11, space_before=0, space_after=12)

    add_p("DEPARTMENT OF COMPUTER SCIENCE", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=12, space_before=0, space_after=24)

    add_p(
        'This is to certify that “EDUMENTOR AI” is a bonafide project work done by '
        'Manoj Pandi P (24UCS07) and Sasi Kumar G (24UCS13) of B.Sc Computer Science '
        'during the fifth semester. Submitted for the final viva-voce held on _____________________',
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, line_spacing=1.5, space_after=90
    )

    sig_table = doc.add_table(rows=2, cols=2)
    sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    sig_table.columns[0].width = Inches(3.2)
    sig_table.columns[1].width = Inches(3.2)

    cell_guide = sig_table.cell(0, 0)
    p_gtitle = cell_guide.paragraphs[0]
    p_gtitle.text = "Project Guide"
    p_gtitle.runs[0].bold = True
    p_gtitle.runs[0].font.name = 'Times New Roman'
    p_gname = cell_guide.add_paragraph("(Dr. M.R.SUMATHI)")
    p_gname.runs[0].font.name = 'Times New Roman'

    cell_hod = sig_table.cell(0, 1)
    p_htitle = cell_hod.paragraphs[0]
    p_htitle.text = "Head of the Department"
    p_htitle.runs[0].bold = True
    p_htitle.runs[0].font.name = 'Times New Roman'
    p_htitle.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_hname = cell_hod.add_paragraph("(Mrs.SM.VALLI)")
    p_hname.runs[0].font.name = 'Times New Roman'
    p_hname.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    cell_ext = sig_table.cell(1, 0)
    cell_ext.paragraphs[0].paragraph_format.space_before = Pt(65)
    cell_ext.paragraphs[0].text = "External Examiner"
    cell_ext.paragraphs[0].runs[0].bold = True
    cell_ext.paragraphs[0].runs[0].font.name = 'Times New Roman'

    doc.add_page_break()

    # ---------------------------------------------------------
    # PAGE 3: DECLARATION (Candidate 1)
    # ---------------------------------------------------------
    add_p("Manoj Pandi P (24UCS07)", align=WD_ALIGN_PARAGRAPH.LEFT, bold=True, size=12, space_before=10, space_after=1)
    add_p("B.Sc Computer Science", align=WD_ALIGN_PARAGRAPH.LEFT, size=12, space_before=0, space_after=1)
    add_p("Department of Computer Science", align=WD_ALIGN_PARAGRAPH.LEFT, size=12, space_before=0, space_after=1)
    add_p("Thiagarajar College (Autonomous)", align=WD_ALIGN_PARAGRAPH.LEFT, size=12, space_before=0, space_after=1)
    add_p("Madurai - 625009", align=WD_ALIGN_PARAGRAPH.LEFT, size=12, space_before=0, space_after=40)

    p_dtitle1 = add_p("DECLARATION", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=13, space_before=0, space_after=30)
    p_dtitle1.runs[0].underline = True

    add_p(
        'Hereby, I declare that the project work entitled “EDUMENTOR AI”, submitted to '
        'Thiagarajar College, Madurai, has been carried out by me as a part of the curriculum. To the best of '
        'my knowledge, this is my original work and has not been copied from any other source. This '
        'project work has not been submitted to any other University/Institute for the award of any degree.',
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, line_spacing=1.5, space_after=80
    )

    decl1_table = doc.add_table(rows=1, cols=2)
    decl1_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    decl1_table.columns[0].width = Inches(3.2)
    decl1_table.columns[1].width = Inches(3.2)

    c0 = decl1_table.cell(0, 0)
    p_p = c0.paragraphs[0]
    p_p.text = "Place:"
    p_p.runs[0].bold = True
    p_p.runs[0].font.name = 'Times New Roman'
    p_d = c0.add_paragraph("Date:")
    p_d.runs[0].bold = True
    p_d.runs[0].font.name = 'Times New Roman'

    c1 = decl1_table.cell(0, 1)
    p_s = c1.paragraphs[0]
    p_s.text = "Signature"
    p_s.runs[0].bold = True
    p_s.runs[0].font.name = 'Times New Roman'
    p_s.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_name = c1.add_paragraph("(Manoj Pandi P)")
    p_name.runs[0].font.name = 'Times New Roman'
    p_name.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_reg = c1.add_paragraph("(24UCS07)")
    p_reg.runs[0].font.name = 'Times New Roman'
    p_reg.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    doc.add_page_break()

    # ---------------------------------------------------------
    # PAGE 4: DECLARATION (Candidate 2)
    # ---------------------------------------------------------
    add_p("Sasi Kumar G (24UCS13)", align=WD_ALIGN_PARAGRAPH.LEFT, bold=True, size=12, space_before=10, space_after=1)
    add_p("B.Sc Computer Science", align=WD_ALIGN_PARAGRAPH.LEFT, size=12, space_before=0, space_after=1)
    add_p("Department of Computer Science", align=WD_ALIGN_PARAGRAPH.LEFT, size=12, space_before=0, space_after=1)
    add_p("Thiagarajar College (Autonomous)", align=WD_ALIGN_PARAGRAPH.LEFT, size=12, space_before=0, space_after=1)
    add_p("Madurai - 625009", align=WD_ALIGN_PARAGRAPH.LEFT, size=12, space_before=0, space_after=40)

    p_dtitle2 = add_p("DECLARATION", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=13, space_before=0, space_after=30)
    p_dtitle2.runs[0].underline = True

    add_p(
        'Hereby, I declare that the project work entitled “EDUMENTOR AI”, submitted to '
        'Thiagarajar College, Madurai, has been carried out by me as a part of the curriculum. To the best of '
        'my knowledge, this is my original work and has not been copied from any other source. This '
        'project work has not been submitted to any other University/Institute for the award of any degree.',
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, line_spacing=1.5, space_after=80
    )

    decl2_table = doc.add_table(rows=1, cols=2)
    decl2_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    decl2_table.columns[0].width = Inches(3.2)
    decl2_table.columns[1].width = Inches(3.2)

    c0_2 = decl2_table.cell(0, 0)
    p_p2 = c0_2.paragraphs[0]
    p_p2.text = "Place:"
    p_p2.runs[0].bold = True
    p_p2.runs[0].font.name = 'Times New Roman'
    p_d2 = c0_2.add_paragraph("Date:")
    p_d2.runs[0].bold = True
    p_d2.runs[0].font.name = 'Times New Roman'

    c1_2 = decl2_table.cell(0, 1)
    p_s2 = c1_2.paragraphs[0]
    p_s2.text = "Signature"
    p_s2.runs[0].bold = True
    p_s2.runs[0].font.name = 'Times New Roman'
    p_s2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_name2 = c1_2.add_paragraph("(Sasi Kumar G)")
    p_name2.runs[0].font.name = 'Times New Roman'
    p_name2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_reg2 = c1_2.add_paragraph("(24UCS13)")
    p_reg2.runs[0].font.name = 'Times New Roman'
    p_reg2.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    doc.add_page_break()

    # ---------------------------------------------------------
    # PAGE 5: ACKNOWLEDGEMENT
    # ---------------------------------------------------------
    p_ack = add_p("ACKNOWLEDGEMENT", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=13, space_before=15, space_after=24)
    p_ack.runs[0].underline = True

    add_p(
        "We extend our sincere thanks to the Almighty for blessing us with the physical strength, mental "
        "ability, and determination that enabled us to complete this project effectively.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, line_spacing=1.5, space_after=14
    )
    add_p(
        "We are grateful to our respected Principal, Dr. D. PANDIARAJA, M.Sc., M.Phil., P.G.D.C.A., "
        "B.Ed., Ph.D., Thiagarajar College, Madurai, for granting us the opportunity to carry out this "
        "project work under the esteemed guidance of our department.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, line_spacing=1.5, space_after=14
    )
    add_p(
        "We wish to express our profound gratitude to the Head of the Department of Computer Science, "
        "Mrs. SM. VALLI, B.E., M.C.A., M.Phil. We sincerely thank her for her valuable guidance, "
        "constant encouragement, and support throughout the progress of this work.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, line_spacing=1.5, space_after=14
    )
    add_p(
        "We are especially indebted to our Project Guide, Dr. M. R. SUMATHI, M.C.A., M.Phil., Ph.D., "
        "for her patient guidance, constructive suggestions, and for having faith in our ability. Her keen "
        "interest and valuable feedback at every stage greatly contributed to the successful completion of "
        "this project.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, line_spacing=1.5, space_after=14
    )
    add_p(
        "We also extend our heartfelt thanks to all the faculty members of the Department of Computer "
        "Science for their constant support, academic guidance, and encouragement during the course of our "
        "project.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, line_spacing=1.5, space_after=14
    )
    add_p(
        "Finally, we express our deep sense of gratitude to our family members and friends for their "
        "unwavering encouragement, moral support, and understanding, which have been a pillar of "
        "strength throughout our work.",
        align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, line_spacing=1.5, space_after=14
    )

    doc.add_page_break()

    # ---------------------------------------------------------
    # PAGE 6: CONTENTS (TABLE OF CONTENTS)
    # ---------------------------------------------------------
    p_toc = add_p("CONTENTS", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=13, space_before=15, space_after=18)
    p_toc.runs[0].underline = True

    toc_rows = [
        ("Sl. No.", "Title", "Pg. No."),
        ("1", "INTRODUCTION\n1.1 Abstract\n1.2 Project Description", "\n2\n3"),
        ("2", "SYSTEM ANALYSIS\n2.1 Existing System\n2.2 Proposed System", "\n10\n12"),
        ("3", "SYSTEM CONFIGURATION\n3.1 Hardware Specification\n3.2 Software Specification\n3.3 About The Language", "\n16\n16\n16"),
        ("4", "SYSTEM DESIGN\n4.1 Data Flow Description\n4.2 Module Description", ""),
        ("5", "SYSTEM IMPLEMENTATION\n5.1 Frontend Implementation\n5.2 Backend Implementation\n5.3 Sample Coding", "\n22\n24\n26"),
        ("6", "SYSTEM TESTING\n6.1 System Testing\n6.2 Types of Testing", ""),
        ("7", "SCREENSHOTS", ""),
        ("8", "CONCLUSION", ""),
        ("9", "FUTURE ENHANCEMENTS", ""),
        ("", "BIBLIOGRAPHY", ""),
    ]

    toc_table = doc.add_table(rows=len(toc_rows), cols=3)
    toc_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(toc_table)

    col_widths = [Inches(1.0), Inches(4.5), Inches(1.0)]
    for i, row in enumerate(toc_table.rows):
        sl, title, pg = toc_rows[i]
        for col_idx, text in enumerate([sl, title, pg]):
            cell = row.cells[col_idx]
            cell.width = col_widths[col_idx]
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            cell.text = text
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.2
            p.paragraph_format.space_after = Pt(2)
            if col_idx == 0 or col_idx == 2:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            
            for run in p.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(11)
                if i == 0 or (col_idx == 1 and any(k in text for k in ["INTRODUCTION", "SYSTEM ANALYSIS", "SYSTEM CONFIGURATION", "SYSTEM DESIGN", "SYSTEM IMPLEMENTATION", "SYSTEM TESTING", "SCREENSHOTS", "CONCLUSION", "FUTURE", "BIBLIOGRAPHY"])):
                    run.bold = True

    # ---------------------------------------------------------
    # SECTION 2: BODY OF REPORT (Starts at Page 1)
    # Centered page number in footer starting at 1
    # ---------------------------------------------------------
    doc.add_page_break()
    sec2 = doc.add_section()
    set_margins(sec2)
    sec2.footer.is_linked_to_previous = False
    
    # Page number XML in footer
    p_foot = sec2.footer.paragraphs[0]
    p_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_f = p_foot.add_run()
    run_f.font.name = 'Times New Roman'
    run_f.font.size = Pt(11)

    fld1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls('w'))
    instr = parse_xml(r'<w:instrText %s xml:space="preserve"> PAGE </w:instrText>' % nsdecls('w'))
    fld2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls('w'))
    fld3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls('w'))
    run_f._r.append(fld1)
    run_f._r.append(instr)
    run_f._r.append(fld2)
    run_f._r.append(fld3)

    pgNum = parse_xml(r'<w:pgNumType %s w:start="1"/>' % nsdecls('w'))
    sec2._sectPr.append(pgNum)

    # ---------------------------------------------------------
    # DIVIDER 1: INTRODUCTION (Page 1)
    # ---------------------------------------------------------
    add_divider_page("INTRODUCTION")

    # ---------------------------------------------------------
    # CHAPTER 1: INTRODUCTION (Page 2)
    # ---------------------------------------------------------
    add_heading_1("1. INTRODUCTION")
    add_heading_2("1.1 ABSTRACT")
    add_p(
        "EduMentor AI is a modern web-based intelligent student learning and mentoring system engineered to revolutionize "
        "classroom assessment, real-time academic monitoring, and personalized student guidance within higher education institutions. "
        "In collegiate academic environments, faculty members and mentors encounter substantial friction when evaluating student "
        "comprehension across diverse course subjects on a daily basis. Conventional manual examinations and static paper assignments "
        "suffer from severe grading delays, subjective inconsistencies, and a lack of granular analytics. Consequently, struggling students "
        "fail to receive timely intervention, while high-performing learners lack adaptive challenges to accelerate their growth."
    )
    add_p(
        "The proposed system establishes a unified, responsive platform integrating a React-based interactive frontend, a high-performance "
        "FastAPI (Python) backend, and a robust PostgreSQL relational database. It incorporates generative artificial intelligence via "
        "Google Gemini models to automate daily topic assessment across Multiple Choice Questions (MCQ), True/False evaluations, Fill-in-the-Blank "
        "exercises, and conceptual Short Answer prompts. Secure role-based access control (RBAC) with JSON Web Tokens (JWT) and BCrypt "
        "cryptographic password hashing protects student and mentor features. Students can take scheduled quizzes, receive immediate explanatory "
        "feedback, consult a 24/7 contextual AI Tutor chatbot, and monitor their learning trajectories. Simultaneously, mentors gain real-time "
        "cohort dashboards, automated at-risk student flagging, curriculum timetable management, and automated diagnostic report dispatches."
    )

    doc.add_page_break()

    # ---------------------------------------------------------
    # 1.2 PROJECT DESCRIPTION (Pages 3 to 8)
    # ---------------------------------------------------------
    add_heading_2("1.2 PROJECT DESCRIPTION")
    add_p(
        "The project aims to develop an innovative web-based academic mentoring platform, EduMentor AI, that enables college students "
        "to continuously assess their syllabus comprehension and provides faculty mentors with real-time academic visibility. It is designed "
        "to provide a trusted, structured, and organized platform where daily syllabus topics are automatically converted into rigorous assessments, "
        "evaluated instantaneously, and synthesized into actionable cohort metrics. The system reduces dependency on informal communication "
        "channels such as WhatsApp groups and static spreadsheets, providing a centralized environment for institutional academic tracking."
    )
    add_p(
        "The system integrates React with Vite and Tailwind CSS for the frontend, Python FastAPI with Uvicorn for backend API development, "
        "PostgreSQL and SQLAlchemy for relational database management, and Google Gemini AI for pedagogical question synthesis and interactive "
        "chat tutoring. Student and mentor verification through college credentials, JWT tokens, and BCrypt security ensures that all restricted "
        "endpoints remain protected. The system delivers comprehensive curriculum timetable synchronization, multi-format automated quiz generation, "
        "instantaneous evaluation pipelines, weak-student diagnostic alerting, automated email reporting, and 24/7 chatbot assistance. By combining "
        "these features, the project provides a simple, secure, and efficient ecosystem for maximizing student academic success."
    )

    add_heading_3("Implementation Steps:")

    # Module 1
    add_p("1. Student and Mentor Authentication and Verification", bold=True)
    add_p(
        "Authentication is the process of identifying and verifying users before granting them access to protected features of the application. "
        "It ensures that only authorized students and faculty mentors can interact with cohort dashboards, assessment engines, and academic records."
    )
    add_p("Required Technologies", bold=True)
    add_bullet("React")
    add_bullet("FastAPI")
    add_bullet("OAuth2 Bearer")
    add_bullet("JWT (python-jose)")
    add_bullet("BCrypt")
    add_bullet("Email / OTP Service")
    add_p("Implementation in EduMentor AI", bold=True)
    add_p(
        "The authentication module provides secure student registration with college register number validation, mentor onboarding, login, "
        "and password recovery. Passwords are encrypted using BCrypt before database storage. Upon successful login, signed JWT tokens are "
        "generated and persisted in client session storage to authenticate subsequent REST API requests across protected student and mentor routes."
    )

    # Module 2
    add_p("2. Curriculum and Daily Topic Management Module", bold=True)
    add_p(
        "Curriculum management is the process of creating, organizing, scheduling, and updating the academic topics taught across different "
        "classes and semesters. It enables faculty mentors to align daily quizzes directly with classroom lectures."
    )
    add_p("Required Technologies", bold=True)
    add_bullet("React")
    add_bullet("FastAPI")
    add_bullet("SQLAlchemy 2.0")
    add_bullet("PostgreSQL")
    add_bullet("REST API")
    add_p("Implementation in EduMentor AI", bold=True)
    add_p(
        "The curriculum module enables mentors to select active topics for First, Second, and Third Year cohorts directly from a weekly timetable. "
        "Mentors can specify custom question quotas, set quiz submission deadlines with automated countdown timers, and archive assigned topics "
        "in the PostgreSQL database for historical syllabus coverage auditing."
    )

    # Module 3
    add_p("3. AI-Powered Question Generation & Quiz Engine Module", bold=True)
    add_p(
        "The AI quiz engine automates the pedagogical synthesis of test items based on the active lecture topic. It relieves educators from the "
        "burdensome task of drafting fresh questions daily while preventing question repetition."
    )
    add_p("Required Technologies", bold=True)
    add_bullet("Python")
    add_bullet("Google Gemini 1.5 Flash API")
    add_bullet("Pydantic Schema Validation")
    add_bullet("FastAPI")
    add_bullet("JSON")
    add_p("Implementation in EduMentor AI", bold=True)
    add_p(
        "When a daily topic is scheduled, the backend orchestrates a structured prompt to the Google Gemini AI model requesting a multi-format "
        "assessment covering Multiple Choice, True/False, Fill in the Blanks, and Short Conceptual questions. Strict Pydantic JSON validation "
        "guarantees that every generated question includes plausible distractors, correct answers, and thorough explanation rationales."
    )

    # Module 4
    add_p("4. Interactive Student Assessment & Instant Scoring Module", bold=True)
    add_p(
        "This module provides a focused, distraction-free environment for students to complete daily quizzes and receive immediate cognitive "
        "reinforcement through automated grading."
    )
    add_p("Required Technologies", bold=True)
    add_bullet("React")
    add_bullet("Tailwind CSS")
    add_bullet("Fetch / Axios")
    add_bullet("FastAPI")
    add_bullet("SQLAlchemy")
    add_p("Implementation in EduMentor AI", bold=True)
    add_p(
        "Students review question prompts, select choices or input answers, and track elapsed time via an intuitive user interface. Upon final "
        "submission, the backend calculates the percentage score, updates student performance records in the database, and renders an itemized "
        "review screen highlighting correct answers and explanatory insights."
    )

    # Module 5
    add_p("5. Mentor Analytics & Cohort Monitoring Module", bold=True)
    add_p(
        "The mentor analytics module aggregates student assessment data across entire academic cohorts, transforming raw scores into visual "
        "comprehension metrics that empower data-driven teaching decisions."
    )
    add_p("Required Technologies", bold=True)
    add_bullet("React")
    add_bullet("Tailwind CSS")
    add_bullet("FastAPI")
    add_bullet("SQLAlchemy")
    add_bullet("REST API")
    add_p("Implementation in EduMentor AI", bold=True)
    add_p(
        "The mentor dashboard computes class average scores, participation rates, submission timeliness, and score distributions across grade "
        "brackets. Mentors can toggle seamlessly between Year 1, 2, and 3 cohorts to monitor academic trajectories and pinpoint topics requiring "
        "classroom re-teaching."
    )

    # Module 6
    add_p("6. Automated Weak-Student Flagging & Diagnostic Alert Module", bold=True)
    add_p(
        "An early-warning diagnostic system continuously tracks learner performance against institutional mastery benchmarks, ensuring that "
        "struggling students receive proactive guidance before terminal examinations."
    )
    add_p("Required Technologies", bold=True)
    add_bullet("FastAPI")
    add_bullet("SQLAlchemy")
    add_bullet("Resend / SMTP Gateway")
    add_bullet("APScheduler")
    add_p("Implementation in EduMentor AI", bold=True)
    add_p(
        "Whenever a student scores below 50% or submits an unmastered concept flag, the engine records an At-Risk diagnostic entry. If cohort-wide "
        "weakness exceeds critical thresholds or students log persistent disengagement, automated email alerts and remediation reports are "
        "dispatched directly to faculty advisors."
    )

    # Module 7
    add_p("7. 24/7 AI Socratic Study Assistant & Tutor Chatbot Module", bold=True)
    add_p(
        "The AI study assistant provides round-the-clock interactive tutoring, enabling students to clarify complex theoretical concepts "
        "and resolve doubts outside standard college hours."
    )
    add_p("Required Technologies", bold=True)
    add_bullet("React")
    add_bullet("FastAPI")
    add_bullet("Google Gemini AI API")
    add_bullet("Prompt Engineering Guardrails")
    add_p("Implementation in EduMentor AI", bold=True)
    add_p(
        "Students access a dedicated conversational interface to ask questions regarding lecture topics. The AI Tutor employs Socratic hints "
        "and conceptual breakdowns strictly bounded by the assigned course syllabus, helping students master difficult topics without revealing "
        "unearned answers."
    )

    # Module 8
    add_p("8. Timetable Scheduling & Administrative Management Module", bold=True)
    add_p(
        "The administrative scheduling module provides centralized control over academic calendars, department batches, faculty assignments, "
        "and multi-year class timetables."
    )
    add_p("Required Technologies", bold=True)
    add_bullet("React")
    add_bullet("FastAPI")
    add_bullet("SQLAlchemy")
    add_bullet("PostgreSQL")
    add_p("Implementation in EduMentor AI", bold=True)
    add_p(
        "Mentors and departmental administrators configure weekly recurring timetables mapping specific subjects and periods across working days. "
        "The system auto-synchronizes daily quizzes with scheduled lecture hours, maintaining complete administrative oversight across all degree cohorts."
    )

    # ---------------------------------------------------------
    # DIVIDER 2: SYSTEM ANALYSIS (Page 9)
    # ---------------------------------------------------------
    add_divider_page("SYSTEM ANALYSIS")

    # ---------------------------------------------------------
    # CHAPTER 2: SYSTEM ANALYSIS (Pages 10 to 14)
    # ---------------------------------------------------------
    add_heading_1("2. SYSTEM ANALYSIS")
    add_heading_2("2.1 EXISTING SYSTEM")
    add_p(
        "Currently, academic mentoring and continuous student assessment in higher education institutions rely predominantly on conventional "
        "pen-and-paper examinations, periodic internal tests, physical assignments, and informal messaging groups such as WhatsApp or Telegram. "
        "Faculty members manually formulate question papers, administer tests during physical class hours, collect physical answer scripts, and "
        "spend extensive hours grading individual responses by hand. Assessment scores are tabulated into disparate spreadsheets or manual grade "
        "registers. These conventional approaches fail to provide a centralized, verified, and automated environment for tracking continuous "
        "student learning outcomes."
    )

    add_heading_3("DISADVANTAGES")

    add_p("1. No Centralized Academic Assessment Platform", bold=True)
    add_p(
        "Existing methods do not provide a dedicated platform where daily syllabus topics, student assessments, automated grading, and academic "
        "records are unified in a single institutional ecosystem."
    )
    add_p(
        "Real-World Example: A professor teaching Database Systems must manually print question sheets, distribute them across 60 students, "
        "and manually record scores in separate offline spreadsheets, leading to fragmented academic tracking.",
        italic=True
    )

    add_p("2. Delayed Student Evaluation and Feedback", bold=True)
    add_p(
        "Manual evaluation requires several days or weeks, completely decoupling assessment results from the active learning moment. By the time "
        "students receive feedback, the syllabus has progressed to advanced topics, leaving foundational knowledge gaps unaddressed."
    )
    add_p(
        "Real-World Example: Students who made conceptual mistakes in SQL Join operations only receive their graded papers two weeks later, "
        "after the instructor has already begun teaching complex Normalization theory.",
        italic=True
    )

    add_p("3. Inability to Pinpoint Struggling Learners in Real Time", bold=True)
    add_p(
        "In large academic cohorts, faculty mentors cannot continuously track individual comprehension curves. Students experiencing subtle "
        "difficulties go unnoticed until midterm examinations, when remedial interventions are often too late."
    )
    add_p(
        "Real-World Example: In a class of 65 students, seven students score below 35% on Python OOP concepts, but their struggle remains invisible "
        "to the mentor because grades are compiled only at the end of the term.",
        italic=True
    )

    add_p("4. Heavy Burden of Manual Question Paper Formulation", bold=True)
    add_p(
        "Drafting fresh, balanced, and syllabus-aligned questions across multiple course subjects every day imposes an exhaustive administrative "
        "workload on educators, leading to repetitive questions and testing fatigue."
    )
    add_p(
        "Real-World Example: A faculty mentor handling three distinct subjects spends up to two hours daily formulating daily review questions "
        "rather than dedicating time to interactive mentoring and research.",
        italic=True
    )

    add_p("5. Absence of 24/7 Academic Doubt Resolution", bold=True)
    add_p(
        "When students encounter academic hurdles while studying independently outside college hours, faculty guidance is unavailable, leaving "
        "students discouraged and unable to complete their learning tasks."
    )
    add_p(
        "Real-World Example: A student practicing C++ data structures at night struggles with pointer allocation errors but has no available "
        "mentor until the next college working day, halting their study progress.",
        italic=True
    )

    add_p("6. Untracked Disengagement and Unreported Conceptual Gaps", bold=True)
    add_p(
        "Traditional lecture environments provide no anonymous or low-friction feedback channel for students to express that a lecture was "
        "confusing or poorly understood, depriving educators of actionable student sentiment."
    )
    add_p(
        "Real-World Example: Several students fail to follow a complex lecture on Operating System thread synchronization but hesitate to ask "
        "questions in a crowded lecture hall, resulting in widespread assessment failure.",
        italic=True
    )

    add_p("7. Disconnected Timetables and Syllabus Coordination Friction", bold=True)
    add_p(
        "Coordinating daily lecture topics across rotating departmental timetables and multi-year cohorts requires manual synchronization, often "
        "leading to mismatches between what was taught and what is tested."
    )
    add_p(
        "Real-World Example: Due to a faculty schedule shift, a substitute teacher covers File Organization, but students are tested on Indexing, "
        "generating unfair scores and student frustration.",
        italic=True
    )

    add_p("8. Scattered Communication and Missed Academic Deadlines", bold=True)
    add_p(
        "Assignment announcements, syllabus revisions, and quiz notices are dispersed across informal social media groups, where essential "
        "information frequently gets lost among casual chat messages."
    )
    add_p(
        "Real-World Example: A student misses an important weekend revision deadline because the notification was buried under dozens of casual "
        "messages in an informal class WhatsApp group.",
        italic=True
    )

    doc.add_page_break()

    # ---------------------------------------------------------
    # 2.2 PROPOSED SYSTEM
    # ---------------------------------------------------------
    add_heading_2("2.2 PROPOSED SYSTEM")
    add_p(
        "The proposed system aims to develop a web-based student learning and mentoring system, EduMentor AI, that provides a centralized "
        "platform for verified college students and mentors to manage daily syllabus assessments, instant automated evaluation, AI tutoring, "
        "cohort analytics, and automated remedial reporting. Unlike manual and informal methods, the system integrates timetable management, "
        "multi-format AI question generation, automated grading, at-risk flagging, and background email dispatch into a single platform."
    )
    add_p("It provides:")

    add_p("1. Role-Based Secure Student and Mentor Portals", bold=True)
    add_p(
        "Role-based authentication ensures that students access distraction-free quiz taking and AI tutoring, while mentors access cohort "
        "analytics and curriculum configuration. Secure authentication using FastAPI, JWT, and BCrypt protects institutional data and student privacy."
    )

    add_p("2. Centralized Daily Assessment & Timetable Synchronization", bold=True)
    add_p(
        "Mentors can assign active topics directly from a structured weekly timetable. The platform maintains exact alignment between daily lectures "
        "and assessment questions, with configurable submission countdown timers."
    )

    add_p("3. Multi-Format AI Question Generation & Instant Evaluation", bold=True)
    add_p(
        "Powered by Google Gemini Generative AI, the system automatically synthesizes Multiple Choice, True/False, Fill in the Blanks, and "
        "Short Answer questions with zero teacher boilerplate. Quizzes are graded instantaneously upon submission with complete explanations."
    )

    add_p("4. Real-Time Mentor Analytics & Performance Monitoring", bold=True)
    add_p(
        "Assessment submissions immediately feed dynamic visualizations on the mentor dashboard, displaying cohort averages, pass rates, score "
        "distributions, and topic mastery trends across all academic years."
    )

    add_p("5. Automated Early-Warning & Weak-Student Email Alerts", bold=True)
    add_p(
        "Students scoring below 50% or submitting difficulty reports are automatically flagged in real time. The built-in email gateway dispatches "
        "diagnostic summaries to mentors, enabling prompt academic counseling."
    )

    add_p("6. 24/7 Context-Aware AI Chat Tutor for Conceptual Doubt Solving", bold=True)
    add_p(
        "Students have on-demand access to a conversational AI assistant strictly aligned with the current lecture topic, providing Socratic "
        "hints and concept breakdowns whenever needed."
    )

    add_p("7. Centralized Academic History & Progress Tracking", bold=True)
    add_p(
        "Complete historical records of every quiz attempt, topic coverage, and diagnostic intervention are preserved in PostgreSQL, establishing "
        "a reliable audit trail for institutional accreditation."
    )

    add_heading_3("ADVANTAGES")
    add_p(
        "EduMentor AI provides a centralized and organized mentoring ecosystem specifically designed for collegiate education. It reduces "
        "administrative grading overhead and makes it simple for mentors to monitor and elevate student comprehension across all subjects."
    )
    add_p(
        "By combining AI question synthesis, instant evaluation, progress monitoring, early-warning alerts, and 24/7 tutoring, the system "
        "provides a structured environment for continuous academic excellence."
    )
    add_p(
        "The system also promotes inclusive learning, helping students identify and correct weaknesses early while fostering responsible academic growth."
    )

    add_bullet("Provides a centralized academic learning and mentoring platform.")
    add_bullet("Eliminates manual question paper creation and grading overhead.")
    add_bullet("Supports multi-format assessments (MCQ, True/False, Fill in Blanks, Short Answers).")
    add_bullet("Delivers instantaneous, explanatory feedback to students upon quiz submission.")
    add_bullet("Provides real-time cohort analytics and pass/fail distributions for faculty mentors.")
    add_bullet("Automatically identifies at-risk learners and dispatches diagnostic email alerts.")
    add_bullet("Offers 24/7 syllabus-bound conversational AI tutoring for on-demand doubt resolution.")
    add_bullet("Synchronizes daily assessments with structured departmental timetables.")
    add_bullet("Maintains secure, role-based access control using JWT and BCrypt cryptography.")
    add_bullet("Reduces dependency on informal communication platforms and manual spreadsheets.")

    # ---------------------------------------------------------
    # DIVIDER 3: SYSTEM CONFIGURATION (Page 15)
    # ---------------------------------------------------------
    add_divider_page("SYSTEM CONFIGURATION")

    # ---------------------------------------------------------
    # CHAPTER 3: SYSTEM CONFIGURATION (Pages 16 to 20)
    # ---------------------------------------------------------
    add_heading_1("3. SYSTEM CONFIGURATION")
    add_heading_2("3.1 HARDWARE SPECIFICATIONS")

    hw_specs = [
        ("Processor", "Intel(R) Core(TM) i5 Processor"),
        ("Processor Speed", "1.30 GHz or above"),
        ("RAM", "8 GB"),
        ("Hard Drive", "512 GB"),
        ("Display", "HD Display"),
        ("Network", "Wi-Fi / Internet Connection")
    ]
    for k, v in hw_specs:
        add_p(f"{k.ljust(22)} : {v}", align=WD_ALIGN_PARAGRAPH.LEFT, size=12, space_before=1, space_after=3)

    add_heading_2("3.2 SOFTWARE SPECIFICATIONS")
    sw_specs = [
        ("Operating System", "Windows 10 / Windows 11"),
        ("Front-end Technology", "React, HTML, CSS, JavaScript"),
        ("Back-end Technology", "Python, FastAPI, Uvicorn"),
        ("Database", "PostgreSQL / SQLite"),
        ("Database Connectivity", "SQLAlchemy ORM / psycopg2"),
        ("API Communication", "REST API / Axios"),
        ("Authentication", "JWT / BCrypt / OTP"),
        ("AI Service", "Google Gemini AI API"),
        ("Email Service", "Resend / SMTP Gateway"),
        ("Development Environment", "Visual Studio Code / Antigravity IDE"),
        ("Database Tool", "pgAdmin / SQLite Studio / DBeaver"),
        ("API Testing Tool", "Postman / FastAPI Swagger UI"),
        ("Build Tool", "Vite / npm"),
        ("Runtime Environment", "Node.js / Python 3.11+")
    ]
    for k, v in sw_specs:
        add_p(f"{k.ljust(25)} : {v}", align=WD_ALIGN_PARAGRAPH.LEFT, size=12, space_before=1, space_after=3)

    add_heading_2("3.3 ABOUT THE LANGUAGE")
    add_p("Python", bold=True)
    add_p(
        "Python is a high-level, interpreted, and object-oriented programming language widely used for developing web applications, artificial "
        "intelligence systems, and backend microservices. In EduMentor AI, Python is mainly used for developing the backend using the FastAPI "
        "framework. It handles application logic, database operations, user authentication, automated question generation via Gemini AI, "
        "assessment scoring, and communication between the frontend and database."
    )

    add_p("Why Python?", bold=True)
    add_bullet("Object-Oriented Programming – Supports classes, inheritance, encapsulation, and modular abstraction for clean application development.")
    add_bullet("Premier AI Ecosystem – Python provides first-class client libraries and native interfaces for cutting-edge generative AI models.")
    add_bullet("High Framework Support – FastAPI and SQLAlchemy provide modern asynchronous primitives for developing ultra-fast, robust web services.")
    add_bullet("Database Integration – Python integrates seamlessly with PostgreSQL and SQLite databases via the SQLAlchemy Object Relational Mapper.")
    add_bullet("Security Support – Python-Jose and BCrypt can be integrated with Python applications for secure cryptographic authentication and authorization.")

    add_p("Advantages of Python", bold=True)
    add_p("Object-Oriented:", bold=True)
    add_p("Supports modular and reusable programming through object-oriented concepts and clean architectural separation.")
    add_p("Secure:", bold=True)
    add_p("Provides cryptographic hashing libraries and supports industry-standard JWT token verification mechanisms.")
    add_p("Platform Independent:", bold=True)
    add_p("Python applications run smoothly across different operating systems including Windows, Linux, and macOS without codebase modification.")
    add_p("Robust:", bold=True)
    add_p("Provides comprehensive exception handling, strong typing through Pydantic, and automated memory management.")
    add_p("Extensive Framework Support:", bold=True)
    add_p("Modern frameworks such as FastAPI, Uvicorn, and Pydantic simplify web API development and generate interactive documentation.")
    add_p("Database Connectivity:", bold=True)
    add_p("Provides reliable, high-performance connectivity with enterprise relational databases such as PostgreSQL.")

    doc.add_page_break()

    # FRONT-END TECHNOLOGIES
    add_heading_2("FRONT-END TECHNOLOGIES")
    add_p(
        "Front-end technologies in EduMentor AI are used to create the user interface through which students and mentors interact with the "
        "system. They provide daily quiz taking, real-time analytics dashboards, AI tutoring chat, curriculum timetable management, and "
        "profile management features."
    )
    add_p("Required Technologies:", bold=True)
    add_bullet("React")
    add_bullet("HTML")
    add_bullet("CSS")
    add_bullet("JavaScript")
    add_bullet("Axios")

    add_p("React:", bold=True)
    add_p(
        "React is a JavaScript library used to develop the user interface of EduMentor AI. It provides reusable components for pages such as the "
        "student quiz dashboard, mentor analytics dashboard, AI chat interface, timetable editor, and alert settings."
    )
    add_p("HTML:", bold=True)
    add_p(
        "HTML is used to define the semantic structure of web pages. It provides elements such as forms, buttons, cards, progress bars, tables, "
        "and interactive layout containers required by the application."
    )
    add_p("CSS:", bold=True)
    add_p(
        "CSS is used to design and style the application interface. It controls typography, spacing, responsive grids, colors, dark and light modes, "
        "animations, and glassmorphic cards."
    )
    add_p("JavaScript:", bold=True)
    add_p(
        "JavaScript provides dynamic behaviour and reactive state management in the frontend. It handles user inputs, quiz timer intervals, "
        "form validation, state transitions, and asynchronous communication with backend APIs."
    )
    add_p("Axios:", bold=True)
    add_p(
        "Axios is used to communicate between the React frontend and FastAPI backend through HTTP requests. It is used for operations such as "
        "login, registration, topic loading, quiz submissions, chatbot messages, and mentor report dispatches."
    )

    doc.add_page_break()

    # BACK-END TECHNOLOGIES
    add_heading_2("BACK-END TECHNOLOGIES")
    add_p(
        "Back-end technologies in EduMentor AI handle business logic, authentication, database operations, AI prompt engineering, assessment "
        "scoring, automated diagnostic mailers, and communication with the frontend."
    )
    add_p("Required Technologies / Environment:", bold=True)
    add_bullet("Python")
    add_bullet("FastAPI")
    add_bullet("SQLAlchemy")
    add_bullet("PostgreSQL")
    add_bullet("REST API")
    add_bullet("JWT")
    add_bullet("Google Gemini Generative AI")

    add_p("FastAPI:", bold=True)
    add_p(
        "FastAPI is used to develop the backend of EduMentor AI. It provides asynchronous REST APIs required for authentication, student "
        "management, daily topic assignment, AI quiz synthesis, scoring pipelines, and mentor reporting."
    )
    add_p("JWT:", bold=True)
    add_p(
        "JSON Web Token (JWT) is used for secure authentication. After successful login, a cryptographically signed token is generated and used "
        "to authenticate requests to protected backend APIs."
    )
    add_p("SQLAlchemy:", bold=True)
    add_p(
        "SQLAlchemy is the Object Relational Mapper (ORM) used to perform database operations between the Python application and PostgreSQL "
        "database. It simplifies storing, retrieving, and querying relational data."
    )
    add_p("PostgreSQL:", bold=True)
    add_p(
        "PostgreSQL is the relational database management system used to store student records, mentor profiles, daily topics, weekly timetables, "
        "quiz scores, question attempts, and chat interaction logs."
    )
    add_p("Google Gemini Generative AI:", bold=True)
    add_p(
        "Google Gemini AI powers automated question generation and the 24/7 conversational AI Tutor. It processes curriculum topics to synthesize "
        "balanced quizzes and delivers context-aware learning explanations."
    )
    add_p("REST API:", bold=True)
    add_p(
        "REST APIs provide standardized communication between the React frontend and FastAPI backend, allowing data exchange via JSON payloads."
    )
    add_p("Development Environment:", bold=True)
    add_p(
        "Visual Studio Code and Antigravity IDE are used for full-stack code development, pgAdmin/DBeaver is used for database management, "
        "and Postman/Swagger UI is used for testing REST APIs."
    )

    # ---------------------------------------------------------
    # DIVIDER 4: SYSTEM IMPLEMENTATION (Page 21)
    # ---------------------------------------------------------
    add_divider_page("SYSTEM IMPLEMENTATION")

    # ---------------------------------------------------------
    # CHAPTER 5: SYSTEM IMPLEMENTATION (Pages 22 to 33)
    # ---------------------------------------------------------
    add_heading_1("5. SYSTEM IMPLEMENTATION")
    add_heading_2("5.1 Frontend Implementation")
    add_p(
        "The frontend of the EduMentor AI system is developed using React.js with Vite, HTML5, CSS3, and JavaScript. It provides an interactive, "
        "modern, and responsive user interface that allows students to take daily quizzes, interact with the AI Tutor chatbot, review scores, "
        "and enables mentors to monitor cohort performance and configure syllabi through REST APIs. React's component-based architecture "
        "improves code reusability, maintainability, and user experience."
    )

    add_heading_3("5.1.1 Authentication Module")
    add_p(
        "The Authentication module allows students and mentors to register and log in securely. Registration includes field validation, register "
        "number checks, and password encryption, while login authenticates the user and stores the JWT token for secure access to protected pages. "
        "The authentication interface is implemented with clear student and mentor tabs."
    )
    add_p("Key Features", bold=True)
    add_bullet("Student Registration")
    add_bullet("Mentor Registration")
    add_bullet("Role-Based Login")
    add_bullet("Form Validation")
    add_bullet("JWT Token Storage")
    add_bullet("Secure Navigation")

    add_heading_3("5.1.2 Student Dashboard & Daily Quiz Module")
    add_p(
        "The Student Dashboard displays the active daily topic and provides an interactive test-taking interface. Students can answer Multiple "
        "Choice, True/False, and Short Answer questions with a live countdown timer and receive instant scores upon completion."
    )
    add_p("Key Features", bold=True)
    add_bullet("Daily Active Topic Display")
    add_bullet("Multi-Format Quiz Rendering")
    add_bullet("Submission Countdown Timer")
    add_bullet("Instant Percentage Score")
    add_bullet("Itemized Solution Review")

    add_heading_3("5.1.3 AI Study Assistant & Chatbot Module")
    add_p(
        "The AI Study Assistant module provides an interactive conversational interface where students can ask questions about the current lecture. "
        "The chatbot delivers pedagogical explanations, hints, and code examples without giving direct answers to test questions."
    )
    add_p("Key Features", bold=True)
    add_bullet("24/7 Chatbot Interface")
    add_bullet("Contextual Lecture Scoping")
    add_bullet("Socratic Concept Explanations")
    add_bullet("Markdown Code Highlighting")
    add_bullet("Real-Time Message Streaming")

    add_heading_3("5.1.4 Mentor Dashboard & Cohort Monitoring Module")
    add_p(
        "The Mentor Dashboard aggregates student assessment results into intuitive visual summaries. Mentors can view class averages, pass rates, "
        "individual student attempts, and flagged weak students across different academic years."
    )
    add_p("Key Features", bold=True)
    add_bullet("Cohort Performance Overview")
    add_bullet("Year 1, 2, and 3 Cohort Switching")
    add_bullet("At-Risk Student Highlighting")
    add_bullet("Score Distribution Analytics")
    add_bullet("One-Click Email Report Generation")

    add_heading_3("5.1.5 Topic Setter & Curriculum Management Module")
    add_p(
        "This module allows mentors to manage the weekly lecture timetable and activate daily topics. Mentors can configure question counts, "
        "set submission due dates and times, and view historical assessment archives."
    )
    add_p("Key Features", bold=True)
    add_bullet("Weekly Timetable Integration")
    add_bullet("Daily Topic Activation")
    add_bullet("Custom Question Quota Configuration")
    add_bullet("Assessment Deadline Expiry")
    add_bullet("Historical Topic Logging")

    doc.add_page_break()

    # 5.2 BACKEND IMPLEMENTATION
    add_heading_2("5.2 Backend Implementation")
    add_p(
        "The backend of the EduMentor AI system is developed using Python with the FastAPI framework. It provides asynchronous RESTful APIs "
        "for communication between the React frontend and the PostgreSQL database. The backend handles authentication, daily topic scheduling, "
        "AI question generation via Gemini, assessment scoring, at-risk student alerting, and background notification services."
    )

    add_heading_3("5.2.1 Authentication API")
    add_p(
        "The Authentication API manages student and mentor registration, credential verification, BCrypt password hashing, and JWT token "
        "issuance. It validates credentials and enforces role-based authorization across protected endpoints."
    )
    add_p("Key Features", bold=True)
    add_bullet("User Registration")
    add_bullet("BCrypt Password Encryption")
    add_bullet("JWT Token Generation")
    add_bullet("Role-Based Route Protection")
    add_bullet("Password Recovery")

    add_heading_3("5.2.2 Daily Topic Management API")
    add_p(
        "The Daily Topic API allows mentors to activate daily lecture topics, configure question specifications, and retrieve currently active "
        "topics for specific cohort years."
    )
    add_p("Key Features", bold=True)
    add_bullet("Set Active Daily Topic")
    add_bullet("Retrieve Today's Topic by Year")
    add_bullet("Timetable Schedule Retrieval")
    add_bullet("Historical Topic Archiving")

    add_heading_3("5.2.3 AI Quiz Generation API")
    add_p(
        "The AI Quiz Generation API communicates with Google Gemini models to synthesize assessment questions covering specified lecture topics, "
        "validating response schemas using Pydantic."
    )
    add_p("Key Features", bold=True)
    add_bullet("Gemini API Orchestration")
    add_bullet("Multi-Format Question Synthesis")
    add_bullet("Pydantic JSON Validation")
    add_bullet("Automated Solution & Distractor Creation")

    add_heading_3("5.2.4 Assessment Scoring & Alert API")
    add_p(
        "The Assessment Scoring API records student quiz submissions, grades answers, updates historical student scores, and evaluates "
        "performance against mastery thresholds to trigger mentor alerts."
    )
    add_p("Key Features", bold=True)
    add_bullet("Quiz Score Logging")
    add_bullet("Automated Answer Evaluation")
    add_bullet("Weak-Student Detection (<50%)")
    add_bullet("Automatic Mentor Email Trigger")

    add_heading_3("5.2.5 AI Tutor Chatbot API")
    add_p(
        "The Chatbot API provides conversational AI assistance, scoping conversations strictly to current syllabus topics and preserving "
        "chat interaction records in PostgreSQL."
    )
    add_p("Key Features", bold=True)
    add_bullet("Conversational Message Processing")
    add_bullet("Curriculum Guardrails")
    add_bullet("Socratic Hint Generation")
    add_bullet("Chat History Persistence")

    add_heading_3("5.2.6 Database Integration")
    add_p(
        "The backend connects to PostgreSQL using SQLAlchemy 2.0 ORM. Declarative entity classes define relational tables, while sessions "
        "manage transactional operations. Relationships between students, scores, daily topics, and chat logs are enforced via foreign keys."
    )
    add_p("Database Tables", bold=True)
    add_bullet("Student")
    add_bullet("Mentor")
    add_bullet("DailyTopic")
    add_bullet("WeeklyTimetable")
    add_bullet("StudentScore")
    add_bullet("BoringReport")
    add_bullet("ChatMessage")
    add_bullet("MentorAction")
    add_bullet("TopicHistory")
    add_bullet("QuizAttempt")

    doc.add_page_break()

    # ---------------------------------------------------------
    # 5.3 SAMPLE CODING (Pages 26 to 33)
    # ---------------------------------------------------------
    add_heading_2("5.3 SAMPLE CODING")

    # Snippet 1: Student Registration (FastAPI)
    add_heading_3("Student Registration (FastAPI Backend)")
    code_lines_reg = [
        "@router.post('/student/register', response_model=StudentResponse, status_code=status.HTTP_201_CREATED)",
        "def register_student(payload: StudentRegister, db: Session = Depends(get_db)):",
        "    # Check if email is already registered",
        "    existing_email = db.query(Student).filter(Student.email == payload.email).first()",
        "    if existing_email:",
        "        raise HTTPException(status_code=400, detail='Registration failed. Email already registered.')",
        "",
        "    # Check if register number is already registered",
        "    existing_regno = db.query(Student).filter(Student.regno == payload.regno).first()",
        "    if existing_regno:",
        "        raise HTTPException(status_code=400, detail='Registration failed. Register number already registered.')",
        "",
        "    # Hash password securely using BCrypt",
        "    hashed_pass = get_password_hash(payload.password)",
        "    new_student = Student(",
        "        username=payload.username,",
        "        regno=payload.regno,",
        "        dept=payload.dept,",
        "        year=payload.year,",
        "        email=payload.email,",
        "        password_hash=hashed_pass",
        "    )",
        "    db.add(new_student)",
        "    db.commit()",
        "    db.refresh(new_student)",
        "",
        "    # Send welcome email asynchronously",
        "    send_welcome_email(to_email=new_student.email, user_name=new_student.username)",
        "    return new_student"
    ]
    for line in code_lines_reg:
        add_code_line(line)

    add_heading_3("Explanation")
    add_p(
        "The registration API accepts student registration details, validates email and institutional register number uniqueness, "
        "encrypts the plain-text password using BCrypt hashing, stores the new student record in the PostgreSQL database, and triggers "
        "an asynchronous welcome email notification before returning the student entity."
    )

    doc.add_page_break()

    # Snippet 2: Daily Topic & AI Quiz Generation (FastAPI)
    add_heading_3("Daily Topic & AI Quiz Generation (FastAPI Backend)")
    code_lines_topic = [
        "@router.post('/api/timetable/set-today', response_model=DailyTopicResponse)",
        "def set_today_topic(payload: DailyTopicSetRequest, db: Session = Depends(get_db), current_mentor: Mentor = Depends(get_current_mentor)):",
        "    # Retrieve or initialize daily topic for cohort year",
        "    dt = db.query(DailyTopic).filter(DailyTopic.year == payload.year).first()",
        "    if not dt:",
        "        dt = DailyTopic(year=payload.year)",
        "        db.add(dt)",
        "",
        "    dt.subject = payload.subject",
        "    dt.topic = payload.topic",
        "    dt.counts = payload.counts.dict()",
        "    dt.due_date = payload.due_date",
        "    dt.due_time = payload.due_time",
        "",
        "    # Archive to immutable topic history log",
        "    history = TopicHistory(",
        "        year=payload.year,",
        "        subject=payload.subject,",
        "        topic=payload.topic,",
        "        counts=payload.counts.dict(),",
        "        set_by=current_mentor.name,",
        "        due_date=payload.due_date,",
        "        due_time=payload.due_time",
        "    )",
        "    db.add(history)",
        "    db.commit()",
        "    db.refresh(dt)",
        "    return dt"
    ]
    for line in code_lines_topic:
        add_code_line(line)

    add_heading_3("Explanation")
    add_p(
        "This API allows verified mentors to configure the daily active syllabus topic for a particular student year cohort. "
        "The endpoint updates the active daily topic in the database, specifies question counts and submission deadlines, "
        "and appends an immutable entry to the topic history table to preserve complete departmental syllabus records."
    )

    doc.add_page_break()

    # Snippet 3: Assessment Score Logging & Auto-Alert (FastAPI)
    add_heading_3("Assessment Score Submission & Auto-Alert (FastAPI Backend)")
    code_lines_score = [
        "@router.post('/api/students/score', response_model=StudentScoreResponse, status_code=status.HTTP_201_CREATED)",
        "def log_score(payload: StudentScoreCreate, db: Session = Depends(get_db), current_student: Student = Depends(get_current_student)):",
        "    # Persist student assessment score",
        "    new_score = StudentScore(",
        "        student_id=current_student.id,",
        "        topic=payload.topic,",
        "        score=payload.score,",
        "        percentage=payload.percentage,",
        "        date=payload.date,",
        "        not_understood=payload.not_understood,",
        "    )",
        "    db.add(new_score)",
        "    db.commit()",
        "    db.refresh(new_score)",
        "",
        "    # Automated Weak-Student check: alert mentor if cohort weak percentage exceeds 50%",
        "    year = current_student.year",
        "    all_students = db.query(Student).filter(Student.year == year).all()",
        "    if all_students:",
        "        weak_count = 0",
        "        for s in all_students:",
        "            latest = db.query(StudentScore).filter(StudentScore.student_id == s.id).order_by(StudentScore.created_at.desc()).first()",
        "            if latest and (latest.percentage < 50 or latest.not_understood):",
        "                weak_count += 1",
        "        if (weak_count / len(all_students)) * 100 > 50:",
        "            send_high_weak_alert(db, year, weak_count, len(all_students), payload.topic)",
        "",
        "    return new_score"
    ]
    for line in code_lines_score:
        add_code_line(line)

    add_heading_3("Explanation")
    add_p(
        "This endpoint logs the student's completed quiz score in the PostgreSQL database. Following submission, the system evaluates the "
        "comprehension status of the cohort; if more than 50% of the students scored below the passing benchmark or reported difficulty understanding "
        "the lecture, an automated alert email is immediately triggered to the faculty mentor urging topic remediation."
    )

    doc.add_page_break()

    # Snippet 4: React Student Login
    add_heading_3("Student Login Component (React.js Frontend)")
    code_lines_react = [
        "const handleStudentLogin = async (e) => {",
        "  e.preventDefault();",
        "  if (!email || !password) {",
        "    showAlert('error', 'Please enter both college email and password.');",
        "    return;",
        "  }",
        "  setLoading(true);",
        "  try {",
        "    const res = await fetch('/api/auth/student/login', {",
        "      method: 'POST',",
        "      headers: { 'Content-Type': 'application/json' },",
        "      body: JSON.stringify({ email, password }),",
        "    });",
        "    const data = await res.json();",
        "    if (res.ok) {",
        "      sessionStorage.setItem('studentToken', data.access_token);",
        "      sessionStorage.setItem('userRole', 'student');",
        "      sessionStorage.setItem('studentName', data.name);",
        "      sessionStorage.setItem('studentYear', data.year);",
        "      sessionStorage.setItem('studentRegNo', data.regno);",
        "      showAlert('success', `Welcome back, ${data.name}! Loading dashboard...`);",
        "      setTimeout(() => navigate('/student-dashboard'), 800);",
        "    } else {",
        "      showAlert('error', data.detail || 'Invalid credentials. Please try again.');",
        "    }",
        "  } catch (err) {",
        "    showAlert('error', 'Unable to connect to backend server.');",
        "  } finally {",
        "    setLoading(false);",
        "  }",
        "};"
    ]
    for line in code_lines_react:
        add_code_line(line)

    add_heading_3("Explanation")
    add_p(
        "The React student login component transmits user credentials via an HTTP POST request to the FastAPI authentication endpoint. "
        "Upon successful verification, the JWT token, student name, academic year, and register number are securely saved into session "
        "storage, and the student is smoothly redirected to their interactive learning dashboard."
    )

    doc.add_page_break()

    # Snippet 5: React Quiz Taking & Instant Score
    add_heading_3("Interactive Quiz Taking & Submission Component (React.js)")
    code_lines_quiz = [
        "const handleQuizSubmit = async () => {",
        "  if (!todayTopic || !quiz) return;",
        "  setSubmitting(true);",
        "  let correctCount = 0;",
        "  const total = quiz.questions.length;",
        "  quiz.questions.forEach((q, idx) => {",
        "    if (userAnswers[idx] && userAnswers[idx].trim().toLowerCase() === q.answer.trim().toLowerCase()) {",
        "      correctCount++;",
        "    }",
        "  });",
        "  const percentage = Math.round((correctCount / total) * 100);",
        "  try {",
        "    const res = await fetch('/api/students/score', {",
        "      method: 'POST',",
        "      headers: {",
        "        'Content-Type': 'application/json',",
        "        'Authorization': `Bearer ${studentToken}`",
        "      },",
        "      body: JSON.stringify({",
        "        topic: todayTopic.topic,",
        "        score: `${correctCount}/${total}`,",
        "        percentage: percentage,",
        "        date: new Date().toLocaleDateString(),",
        "        not_understood: percentage < 50",
        "      })",
        "    });",
        "    if (res.ok) {",
        "      setSessionScore({ correct: correctCount, total, percentage });",
        "      setQuizDoneToday(true);",
        "    }",
        "  } catch (err) {",
        "    console.error('Score submission error:', err);",
        "  } finally {",
        "    setSubmitting(false);",
        "  }",
        "};"
    ]
    for line in code_lines_quiz:
        add_code_line(line)

    add_heading_3("Explanation")
    add_p(
        "This React component evaluates student quiz responses against verified answer models, computes the percentage score, and dispatches "
        "the result to the FastAPI backend with the student's JWT authorization header. It marks the assessment as completed for the day and "
        "displays the instant score review to the learner."
    )

    # Save output documents
    output_academic = "EduMentor_AI_Academic_Project_Report.docx"
    output_general = "EduMentor_AI_Project_Report.docx"
    doc.save(output_academic)
    doc.save(output_general)
    print(f"Generated {output_academic} and {output_general} successfully.")

if __name__ == "__main__":
    build_report()
