import os
from dotenv import load_dotenv

load_dotenv()

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class GeminiDocumentGenerator:
    """Gemini-powered legal document generator."""

    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-pro").strip()

        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is missing. Create a .env file and add your Gemini API key."
            )

        if genai is None:
            raise RuntimeError(
                "google-generativeai is not installed. Run: pip install -r requirements.txt"
            )

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    @staticmethod
    def _build_prompt(document_type: str, parties: str, terms: str, dates: str) -> str:
        term_items = [item.strip() for item in terms.split(";") if item.strip()]
        terms_text = "\n".join(f"- {item}" for item in term_items)
        if not terms_text:
            terms_text = "- No additional terms supplied."

        return f"""
You are the document-generation component of LegalEase.

Create a professional DRAFT legal document using the information below.

Document type:
{document_type}

Parties:
{parties}

Effective date:
{dates}

Requested terms:
{terms_text}

Requirements:
1. Use only information supplied by the user. Do not invent names, addresses,
   monetary amounts, dates, jurisdictions, statutes, registration numbers,
   or other material facts.
2. Clearly mark the output as a DRAFT.
3. Use a professional legal-document structure.
4. Include a title, parties/introduction, definitions where useful,
   numbered sections, requested terms, general provisions where appropriate,
   signature blocks, and an effective-date section.
5. If important information is missing, use a clear placeholder such as
   [NOT PROVIDED] instead of inventing it.
6. Keep the document editable as plain text.
7. Do not include markdown fences.
8. Do not provide a legal opinion about whether the document is enforceable.
9. End with a short review notice saying the draft should be reviewed for the
   applicable jurisdiction and circumstances.

Return only the document text.
""".strip()

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
    ) -> str:
        prompt = self._build_prompt(document_type, parties, terms, dates)

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 8192,
                },
            )
        except Exception as exc:
            raise RuntimeError(f"Gemini API request failed: {exc}") from exc

        text = getattr(response, "text", None)
        if not text:
            raise RuntimeError("Gemini returned an empty response.")

        return text.strip()
