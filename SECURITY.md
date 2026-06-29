# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | ✅ Current |

## Reporting a Vulnerability

Job Hunter handles API keys locally. Security issues are taken seriously.

**Please do not report security vulnerabilities as public GitHub issues.**

Instead, report them privately via:

1. **GitHub Private Vulnerability Reporting** — use the "Report a vulnerability" button on the [Security tab](https://github.com/Briancoughlin/job-hunter/security/advisories/new)

### What to include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested fix if you have one

### What to expect

- Acknowledgement within 48 hours
- Assessment and fix timeline within 7 days for critical issues

## Security Design

Job Hunter is designed with security in mind:

- API keys are stored in a local `.env` file — never committed to git
- `.gitignore` explicitly excludes `.env` and `saved_profile.json`
- No data is sent to external servers beyond the APIs you configure (Anthropic, job boards)
- Your CV and parsed profile stay on your machine
- Dependabot runs weekly to catch dependency vulnerabilities
