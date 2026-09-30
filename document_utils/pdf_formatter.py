from pathlib import Path

from fpdf import FPDF

from document_utils.sanitizer import sanitize_text


class LegalPDF(FPDF):
    def __init__(self, doc_type: str, logo_path: str | None = None):
        super().__init__()
        self.doc_type = doc_type
        self.logo_path = logo_path

    def header(self):
        if self.logo_path and Path(self.logo_path).exists():
            try:
                self.image(self.logo_path, x=95, y=8, w=20)
                self.ln(18)
            except Exception:
                self.ln(4)
        else:
            self.ln(5)

        self.set_font("Times", "B", 12)
        self.cell(0, 8, self.doc_type.upper(), align="C")
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("Times", "", 8)
        self.cell(
            0,
            5,
            f"LegalEase - Draft for review | Page {self.page_no()}",
            align="C",
        )


def format_pdf(
    text: str,
    doc_type: str,
    logo_path: str | None = None,
) -> bytes:
    pdf = LegalPDF(doc_type, logo_path)
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    pdf.set_font("Times", "", 11)

    for raw_line in sanitize_text(text).splitlines():
        line = raw_line.strip()

        if not line:
            pdf.ln(4)
            continue

        upper = line.upper()
        heading = (
            upper.startswith("SECTION ")
            or upper.startswith("ARTICLE ")
            or upper.startswith("PARTIES")
            or upper.startswith("RECITALS")
            or upper.startswith("BACKGROUND")
            or upper.startswith("SIGNATURE")
            or upper.startswith("GOVERNING LAW")
            or upper.startswith("CONFIDENTIALITY")
            or upper.startswith("TERMINATION")
            or upper == "DRAFT"
        )

        pdf.set_font("Times", "B" if heading else "", 11)
        pdf.multi_cell(0, 6, line)

    return bytes(pdf.output())
