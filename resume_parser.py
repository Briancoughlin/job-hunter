import pdfplumber


def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def parse_resume(pdf_path: str, client) -> dict:
    """Parse a CV PDF into a profile dict. ``client`` is any llm.py client."""
    raw_text = extract_text_from_pdf(pdf_path)

    prompt = f"""Extract structured profile data from this LinkedIn/resume PDF text.
Return ONLY valid JSON with this exact structure:

{{
  "name": "full name",
  "current_title": "most recent job title",
  "years_experience": number,
  "seniority": "junior|mid|senior|staff|principal|director|vp|c-level",
  "skills": ["skill1", "skill2", ...],
  "domains": ["domain1", ...],
  "industries": ["industry1", ...],
  "past_titles": ["title1", ...],
  "education": ["degree/school", ...],
  "languages": ["language1", ...],
  "summary": "2-3 sentence professional summary"
}}

Resume text:
{raw_text}"""

    return client.complete_json(prompt, max_tokens=2048)
