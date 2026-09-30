import html

from document_utils.sanitizer import sanitize_text


def format_html_preview(text: str) -> str:
    blocks = []

    for raw_line in sanitize_text(text).splitlines():
        line = raw_line.strip()
        if not line:
            continue

        escaped = html.escape(line)
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

        if heading:
            blocks.append(f"<h3>{escaped}</h3>")
        elif line.startswith("- "):
            blocks.append(f"<li>{escaped[2:]}</li>")
        else:
            blocks.append(f"<p>{escaped}</p>")

    return '<div class="legalease-preview">' + "\n".join(blocks) + "</div>"
