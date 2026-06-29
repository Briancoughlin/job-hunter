# Job Hunter

An AI-powered job search assistant built with Python and Streamlit. Upload your CV, and it searches job boards, scores each role against your profile, and ranks them by fit — so you spend time on the right applications, not scrolling through noise.

Built in a few evenings using AI-assisted development.

![Job Hunter screenshot](docs/screenshot.png)

---

## What it does

1. **Parses your CV** — upload a LinkedIn PDF; Claude extracts your skills, experience, seniority, and domains into a structured profile
2. **Searches job boards** — queries LinkedIn, Indeed, Glassdoor, and ZipRecruiter via `python-jobspy` using terms derived from your profile
3. **Scores every role** — Claude scores each job 0–100 against your profile, with skills match, seniority match, domain match, strengths, gaps, and a fit summary
4. **Ranks results** — sortable table of scored jobs so the best matches rise to the top; save roles, mark applied, export to CSV

---

## Setup

### Requirements
- Python 3.11+
- An Anthropic API key (get one at [console.anthropic.com](https://console.anthropic.com))

### Install

```bash
git clone https://github.com/Briancoughlin/job-hunter.git
cd job-hunter
pip install -r requirements.txt
pip install python-jobspy --no-deps
```

> **Note:** `python-jobspy` pins an older numpy that has no prebuilt wheels for Python 3.12+. `--no-deps` skips that constraint — it works correctly with the current numpy at runtime.

### Configure

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

Or enter your API key directly in the sidebar when the app is running.

### Run

```bash
python -m streamlit run app.py
```

Opens at http://localhost:8501

---

## Run as a desktop app (Windows)

Launch Job Hunter silently in its own Edge window — no terminal, no browser tabs.

1. Generate the icon (once, after cloning):
   ```
   python create_icons.py
   ```
2. Create the Start/taskbar shortcut (once):
   ```powershell
   .\create_shortcut.ps1
   ```
3. Right-click **Job Hunter.lnk** → **Pin to Start** or **Show more options** → **Pin to taskbar**

Clicking the shortcut starts Streamlit in the background and opens Edge in app mode.

> **Security:** `run.bat`, `run.vbs`, and `create_shortcut.ps1` are version-controlled and monitored by CI. Any modification triggers a review alert; direct pushes to `master` are blocked.

---

## Usage

1. Enter your Anthropic API key in the sidebar (saved to `.env` for future sessions)
2. Upload your LinkedIn profile PDF (`Me → Resources → Save to PDF`)
3. Adjust search settings — remote only, location, results per term, minimum score
4. Click **Search & Score Jobs**
5. Browse the ranked results — green 75+, amber 55–74, red below 55
6. Save roles, mark applied, or export to CSV

Your parsed profile is cached locally as `saved_profile.json` — no need to re-upload your CV each session.

---

## Tech stack

| Component | Purpose |
|-----------|---------|
| Python | Backend logic |
| Streamlit | UI |
| Claude (Anthropic) | CV parsing and job scoring |
| python-jobspy | Job board scraping (LinkedIn, Indeed, Glassdoor, ZipRecruiter) |
| pdfplumber | PDF text extraction |

---

## Privacy

Everything runs locally. Your CV and profile never leave your machine beyond the API calls to Claude for parsing and scoring. No accounts, no cloud sync, no telemetry.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Security

See [SECURITY.md](SECURITY.md).

---

## Licence

MIT
