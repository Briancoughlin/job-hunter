# Contributing to Job Hunter

Thanks for your interest in contributing!

---

## Getting started

### Prerequisites
- Python 3.11+
- An Anthropic API key

### Setup

```bash
git clone https://github.com/Briancoughlin/job-hunter.git
cd job-hunter
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
streamlit run app.py
```

---

## Project structure

```
job_hunter/
  app.py              — Streamlit UI and main entry point
  scraper.py          — Job board search (Remotive, WeWorkRemotely, LinkedIn via jobspy)
  scorer.py           — Claude-powered job scoring against candidate profile
  resume_parser.py    — PDF CV parser using Claude
  requirements.txt    — Python dependencies
  .env.example        — Environment variable template
```

---

## Making changes

1. Fork the repo and create a branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Run lint: `ruff check .`
4. Push and open a PR against `main`

### Adding a new job board

1. Add a `_yourboard(term, ...)` function in `scraper.py`
2. Call it inside `fetch_jobs()` alongside the existing sources
3. Return a list of dicts with keys: `site`, `title`, `company`, `location`, `job_url`, `date_posted`, `description`, `job_type`

---

## Reporting bugs

Open a GitHub issue with:
- What you were doing
- What happened vs what you expected
- Any error output from the terminal
