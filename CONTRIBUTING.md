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
pip install python-jobspy --no-deps
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
python -m streamlit run app.py
```

---

## Project structure

```
job_hunter/
  app.py                 -- Streamlit UI and main entry point
  scraper.py             -- Job board search via python-jobspy
  scorer.py              -- Claude-powered job scoring
  resume_parser.py       -- LinkedIn PDF parser using Claude
  requirements.txt       -- Python dependencies
  .env.example           -- Environment variable template
  run.bat                -- Windows launcher (CI monitored)
  run.vbs                -- Silent launcher wrapper (CI monitored)
  create_shortcut.ps1    -- Generates a pinnable taskbar shortcut
  create_icons.py        -- Generates PWA and Windows icons (run locally)
  static/
    manifest.json        -- PWA manifest
    sw.js                -- Service worker
    icon.ico             -- Windows shortcut icon
```

---

## Making changes

1. Fork the repo and create a branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Run lint: `ruff check .`
4. Push and open a PR against `master`

### Adding a new job board

1. Add a fetch function in `scraper.py`
2. Call it inside `fetch_jobs()` alongside the existing sources
3. Return a list of dicts with keys: `site`, `title`, `company`, `location`, `job_url`, `date_posted`, `description`, `job_type`

---

## Launcher files

`run.bat`, `run.vbs`, and `create_shortcut.ps1` are monitored by CI. Any PR modifying these files will trigger a review warning. Direct pushes to `master` that touch these files will fail the CI check. This is intentional — launcher scripts are a common vector for supply-chain attacks.

---

## Reporting bugs

Open a GitHub issue with:
- What you were doing
- What happened vs what you expected
- Any error output from the terminal
