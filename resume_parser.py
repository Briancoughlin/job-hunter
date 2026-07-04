import pdfplumber

from llm import generate_json


def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def parse_resume(pdf_path: str, model: str = "llama3.2", base_url: str = "http://localhost:11434") -> dict:
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

    return generate_json(prompt, model=model, base_url=base_url)
