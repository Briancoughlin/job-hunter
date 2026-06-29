# Changelog

All notable changes to Job Hunter are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] - 2026-06-29

### Added
- **CV parser** — upload a PDF CV; Claude extracts skills, experience, seniority, domains, and industries into a structured profile
- **Multi-source job search** — searches Remotive, WeWorkRemotely, and LinkedIn via `python-jobspy`
- **AI scoring** — Claude scores each job 0–100 against your profile with skills match, seniority match, domain match, strengths, gaps, and a fit summary
- **Interview probability** — low / medium / high / very high rating per role
- **Ranked results table** — sortable by score, filterable by recommendation
- **Profile persistence** — parsed profile saved locally so CV doesn't need re-uploading each session
- **UK location filtering** — roles that exclude UK candidates are scored lower
- **Configurable LLM gateway** — Base URL field supports internal LLM proxies
- **CI pipeline** — ruff lint + import check on every push via GitHub Actions
- **Dependabot** — weekly Python dependency scanning
