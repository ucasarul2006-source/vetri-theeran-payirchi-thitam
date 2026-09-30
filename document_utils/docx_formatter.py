from io import BytesIO
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.shared import Inches, Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from document_utils.sanitizer import sanitize_text


def _set_cell_shading(cell, fill="EAEAEA"):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def _set_document_font(document: Document):
    normal = document.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(11)

    for section in document.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)


def _add_footer(document: Document):
    for section in document.sections:
        paragraph = section.footer.paragraphs[0]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = paragraph.add_run("Generated with LegalEase — Draft for review")
        run.font.name = "Times New Roman"
        run.font.size = Pt(8)


def _is_heading(line: str) -> bool:
    upper = line.upper()
    return (
        upper.startswith("SECTION ")
        or upper.startswith("ARTICLE ")
        or upper.startswith("PARTIES")
        or upper.startswith("RECITALS")
        or upper.startswith("BACKGROUND")
        or upper.startswith("SIGNATURE")
        or upper.startswith("GOVERNING LAW")
        or upper.startswith("CONFIDENTIALITY")
        or upper.startswith("TERMINATION")
    )


def format_docx(
    text: str,
    doc_type: str,
    terms: str = "",
    logo_path: str | None = None,
) -> bytes:
    document = Document()
    _set_document_font(document)

    if logo_path and Path(logo_path).exists():
        paragraph = document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.add_run().add_picture(logo_path, width=Inches(1.35))

    title = document.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run(doc_type.upper())
    run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(16)

    draft = document.add_paragraph()
    draft.alignment = WD_ALIGN_PARAGRAPH.CENTER
    draft_run = draft.add_run("DRAFT")
    draft_run.bold = True
    draft_run.font.size = Pt(10)

    for raw_line in sanitize_text(text).splitlines():
        line = raw_line.strip()

        if not line:
            document.add_paragraph()
            continue

        paragraph = document.add_paragraph()
        run = paragraph.add_run(line)
        if _is_heading(line) or line.upper() == "DRAFT":
            run.bold = True

    if terms.strip():
        document.add_page_break()

        heading = document.add_paragraph()
        heading_run = heading.add_run("USER-PROVIDED TERMS")
        heading_run.bold = True

        table = document.add_table(rows=1, cols=2)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.style = "Table Grid"

        header = table.rows[0].cells
        header[0].text = "No."
        header[1].text = "Term"
        _set_cell_shading(header[0])
        _set_cell_shading(header[1])

        for index, item in enumerate(
            [x.strip() for x in terms.split(";") if x.strip()],
            start=1,
        ):
            cells = table.add_row().cells
            cells[0].text = str(index)
            cells[1].text = item

    _add_footer(document)

    buffer = BytesIO()
    document.save(buffer)
    return buffer.getvalue()
