# Job Hunter

An AI-powered job search assistant built with Python and Streamlit. Upload your LinkedIn profile PDF, and it searches job boards, scores each role against your profile, and ranks them by fit — so you spend time on the right applications, not scrolling through noise.

![Job Hunter screenshot](docs/screenshot.png)

---

## Features

- **CV Parsing** — upload a LinkedIn PDF; Claude extracts your skills, experience, seniority, and domains into a structured profile
- **Multi-Board Search** — queries Remotive, Jobicy, and LinkedIn for remote roles using terms derived from your profile
- **AI Scoring** — Claude scores each job 0-100 against your profile, with skills match, seniority match, domain match, strengths, gaps, and a fit summary
- **Interview Probability** — low / medium / high / very high rating per role
- **Ranked Results** — sortable, filterable table with color-coded scores (green 75+, amber 55-74, red <55)
- **Save & Track** — save roles, mark as applied, export results to CSV
- **Profile Persistence** — parsed profile cached locally; no need to re-upload CV each session
- **Configurable LLM Gateway** — Base URL field supports internal LLM proxies alongside the standard Anthropic API
- **Custom Search Terms** — add your own job titles alongside auto-generated ones
- **Windows Desktop Mode** — launch silently in Edge app mode with no terminal window

---

## Project Structure

```
job-hunter/
├── app.py                  # Streamlit application (main entry point)
├── resume_parser.py        # PDF text extraction and Claude-based parsing
├── scraper.py              # Job board scraping (Remotive, Jobicy, LinkedIn)
├── scorer.py               # Claude-based job scoring
├── requirements.txt        # Python dependencies
├── ruff.toml               # Ruff linter configuration
├── .env.example            # Environment variable template
├── run.bat                 # Windows launcher (headless)
├── run.vbs                 # VBScript wrapper to suppress terminal
├── create_shortcut.ps1     # PowerShell script to create desktop shortcut
├── static/
│   ├── manifest.json       # PWA manifest
│   ├── sw.js               # Service worker
│   └── icon.ico            # App icon
├── docs/
│   └── screenshot.png      # Application screenshot
├── .github/
│   ├── workflows/
│   │   ├── ci.yml          # CI: ruff lint + import check
│   │   └── launcher-integrity.yml
│   └── dependabot.yml      # Weekly pip dependency updates
└── .streamlit/
    └── config.toml         # Streamlit configuration
```

---

## Prerequisites

- **Python 3.11+**
- **Anthropic API Key** — get one at [console.anthropic.com](https://console.anthropic.com)

---

## Installation

```bash
git clone https://github.com/Briancoughlin/job-hunter.git
cd job-hunter
pip install -r requirements.txt
pip install python-jobspy --no-deps
```

> **Note:** `python-jobspy` pins an older numpy that has no prebuilt wheels for Python 3.12+. Using `--no-deps` skips that constraint — it works correctly at runtime.

---

## Configuration

Copy the example environment file and add your API key:

```bash
cp .env.example .env
```

Edit `.env`:

```env
ANTHROPIC_API_KEY=sk-ant-...your-key-here...
# Optional: set this if your organisation has an internal LLM gateway
# ANTHROPIC_BASE_URL=https://your-llm-gateway.example.com
```

Or enter your API key directly in the sidebar when the app is running. The key is saved to `.env` for future sessions.

---

## Running the App

```bash
python -m streamlit run app.py
```

Opens at [http://localhost:8501](http://localhost:8501).

---

## Windows Desktop Mode

Launch Job Hunter silently in its own Edge window — no terminal, no browser tabs.

1. Generate the custom icon (once, after cloning):
   ```bash
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

1. Enter your Anthropic API key in the sidebar (or set it in `.env`)
2. Upload your LinkedIn profile PDF — export via **Me → Resources → Save to PDF**
3. Adjust search settings: remote only, location, results per term, minimum score
4. Add optional custom search terms (e.g. `Senior Product Manager`)
5. Click **Search & Score Jobs**
6. Browse ranked results — green (75+), amber (55-74), red (<55)
7. Save roles, mark as applied, or export to CSV

Your parsed profile is cached as `saved_profile.json` — no need to re-upload your CV each session.

---

## Tech Stack

| Component | Purpose |
|-----------|---------|
| Python | Backend logic |
| Streamlit | Web UI |
| Claude (Anthropic) | CV parsing and job scoring |
| Remotive / Jobicy / LinkedIn | Job board sources |
| pdfplumber | PDF text extraction |
| pandas | Data manipulation |
| ruff | Linting |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Security

See [SECURITY.md](SECURITY.md).

---

## Licence

MIT
