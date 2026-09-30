import os

import requests
import streamlit as st
from dotenv import load_dotenv

from document_utils.docx_formatter import format_docx
from document_utils.pdf_formatter import format_pdf
from document_utils.html_formatter import format_html_preview

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "120"))

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.1rem;
    }
    .subtitle {
        text-align: center;
        color: #777;
        margin-bottom: 1.5rem;
    }
    .legalease-preview {
        background: #111827;
        color: #f9fafb;
        padding: 28px;
        border-radius: 14px;
        max-height: 650px;
        overflow-y: auto;
        line-height: 1.65;
    }
    .legalease-preview h3 {
        color: #ffffff;
        margin-top: 20px;
    }
    .legalease-preview p {
        color: #e5e7eb;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">⚖️ LegalEase</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">AI-Powered Legal Document Generator</div>',
    unsafe_allow_html=True,
)

if "document_text" not in st.session_state:
    st.session_state.document_text = ""

if "generated" not in st.session_state:
    st.session_state.generated = False

with st.sidebar:
    st.header("Backend")
    st.code(BACKEND_URL)
    st.caption(
        "Start FastAPI first: "
        "`uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload`"
    )

left, right = st.columns([1, 1])

with left:
    st.subheader("Document Details")

    document_type = st.selectbox(
        "Document Type",
        [
            "Employment Contract",
            "Non-Disclosure Agreement",
            "Lease Agreement",
            "Employment Offer Letter",
            "Freelance Work Contract",
            "Service Agreement",
            "General Agreement",
            "Custom",
        ],
    )

    if document_type == "Custom":
        document_type = st.text_input(
            "Custom Document Type",
            placeholder="e.g. Partnership Agreement",
        )

    parties = st.text_area(
        "Parties Involved",
        height=120,
        placeholder="Jane Doe (Service Provider), TechNova Inc. (Client)",
    )

    terms = st.text_area(
        "Terms & Conditions",
        height=180,
        placeholder=(
            "Payment within 30 days; "
            "Provider delivers work by agreed deadline; "
            "Confidentiality must be maintained; "
            "Either party may terminate with 15 days notice"
        ),
        help="Separate individual terms with semicolons (;).",
    )

    dates = st.text_input(
        "Effective Date",
        placeholder="April 15, 2026",
    )

    generate = st.button(
        "Generate Document",
        type="primary",
        use_container_width=True,
    )

    if generate:
        if not document_type.strip():
            st.error("Enter a document type.")
        elif not parties.strip():
            st.error("Enter the parties.")
        elif not terms.strip():
            st.error("Enter at least one term.")
        elif not dates.strip():
            st.error("Enter the effective date.")
        else:
            payload = {
                "document_type": document_type.strip(),
                "parties": parties.strip(),
                "terms": terms.strip(),
                "dates": dates.strip(),
            }

            try:
                with st.spinner("Generating your legal document..."):
                    response = requests.post(
                        f"{BACKEND_URL}/generate",
                        json=payload,
                        timeout=REQUEST_TIMEOUT,
                    )

                if response.ok:
                    data = response.json()
                    st.session_state.document_text = data["content"]
                    st.session_state.generated = True
                    st.success("Document generated successfully.")
                else:
                    try:
                        detail = response.json().get("detail", response.text)
                    except Exception:
                        detail = response.text
                    st.error(f"Backend error: {detail}")

            except requests.exceptions.ConnectionError:
                st.error(
                    "Cannot connect to FastAPI. Start the backend first at "
                    f"{BACKEND_URL}."
                )
            except requests.exceptions.Timeout:
                st.error("The backend request timed out.")
            except Exception as exc:
                st.error(f"Unexpected error: {exc}")

with right:
    st.subheader("Document Preview")

    if st.session_state.generated:
        st.markdown(
            format_html_preview(st.session_state.document_text),
            unsafe_allow_html=True,
        )
    else:
        st.info("Your generated document will appear here.")

if st.session_state.generated:
    st.divider()
    st.subheader("Edit Document")

    edited = st.text_area(
        "Edit the generated document below.",
        value=st.session_state.document_text,
        height=500,
        label_visibility="collapsed",
    )

    st.session_state.document_text = edited

    st.subheader("Download")

    col1, col2, col3 = st.columns(3)

    safe_name = (
        document_type.lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
    )

    with col1:
        st.download_button(
            "Download TXT",
            data=st.session_state.document_text.encode("utf-8"),
            file_name=f"{safe_name}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with col2:
        try:
            docx_bytes = format_docx(
                st.session_state.document_text,
                document_type,
                terms=terms,
            )
            st.download_button(
                "Download DOCX",
                data=docx_bytes,
                file_name=f"{safe_name}.docx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
                use_container_width=True,
            )
        except Exception as exc:
            st.error(f"DOCX generation failed: {exc}")

    with col3:
        try:
            pdf_bytes = format_pdf(
                st.session_state.document_text,
                document_type,
            )
            st.download_button(
                "Download PDF",
                data=pdf_bytes,
                file_name=f"{safe_name}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as exc:
            st.error(f"PDF generation failed: {exc}")

    st.caption(
        "LegalEase creates drafts for review. Review the document for the "
        "applicable jurisdiction and your specific circumstances before use."
    )
